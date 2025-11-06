import json
import multiprocessing
import os
import re
import shlex
import signal
import subprocess
import sys
from pathlib import Path

# --- ANSI Color Codes ---
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# import 'resource' at the top level for multiprocessing
try:
    import resource

    IS_UNIX = True
except ImportError:
    IS_UNIX = False

# --- Global Pool for Signal Handling ---
# This is the standard, required pattern for signal handlers
# to access the pool, and it prevents pickling errors.
pool = None


def _main_shutdown_handler(signum, frame):
    """
    MAIN SCRIPT'S HANDLER (Global function)
    Catches SIGTERM/SIGINT and gracefully shuts down the global pool.
    """
    global pool
    if signum == signal.SIGTERM:
        print(f"\n\n{YELLOW}SIGTERM received. Shutting down pool...{RESET}")
    elif signum == signal.SIGINT:
        print(f"\n\n{YELLOW}Ctrl+C (SIGINT) received. Shutting down pool...{RESET}")

    if pool:
        pool.terminate()
        pool.join()
    print("Pool shut down. Exiting.")
    sys.exit(0)


class StressTester:
    def __init__(self, config_path: Path, script_dir: Path):
        print("Initializing Stress Tester...")
        self.config_path = Path(config_path)
        self.script_dir = script_dir

        self.config = self._load_config(self.config_path)
        self._validate_config(self.config)

        self.can_measure = self._check_environment()

        self.current_child_pgid = None

        # Unpack config
        self._unpack_and_resolve_paths(self.config)

        # Configure number of parallel processes
        max_cores = multiprocessing.cpu_count()
        if self.cfg_tester["num_cores"] <= 0:
            self.num_workers = max_cores
        else:
            self.num_workers = min(self.cfg_tester["num_cores"], max_cores)

        print(
            f"Loaded config. Using {CYAN}{self.num_workers}/{max_cores}{RESET} CPU cores for parallel testing."
        )

    def _unpack_and_resolve_paths(self, config):
        """Unpacks config and makes all relative paths absolute."""
        self.cfg_limits = config["limits"]
        self.cfg_tester = config["tester"]
        self.cfg_paths = {}

        # --- Resolve "commands" paths ---
        self.cfg_cmd = {}
        print("Resolving script paths:")
        for key, command_str in config["commands"].items():
            # e.g., command_str = "pypy3 generator.py"
            parts = shlex.split(command_str)

            # Find the script part (e.g., "generator.py")
            # We assume it's the last part.
            # This is robust for "python" vs "pypy3" vs "java -jar"
            script_file = parts[-1]

            # Create an absolute path to the script
            # e.g., /home/shadow30812/.../stress_test/generator.py
            absolute_script_path = self.script_dir / script_file

            # Replace the relative path with the absolute one
            parts[-1] = str(absolute_script_path)

            # Re-join the command
            self.cfg_cmd[key] = shlex.join(parts)
            print(f"  {key}: {self.cfg_cmd[key]}")

        # --- Resolve "paths" paths ---
        # /usr/bin/time is already absolute, so it's fine
        self.cfg_paths["time_binary"] = config["paths"]["time_binary"]

        # Make the failing_input_file absolute
        failing_file_path = self.script_dir / config["paths"]["failing_input_file"]
        self.cfg_paths["failing_input_file"] = str(failing_file_path)
        print(f"  failing_input_file: {self.cfg_paths['failing_input_file']}")

    def _load_config(self, config_path: Path):
        """Loads the JSON configuration file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with config_path.open() as f:
            return json.load(f)

    def _validate_config(self, config):
        """
        Validates that the loaded config dict contains all necessary keys.
        Raises a friendly KeyError if a key is missing.
        """
        print("Validating config...")
        # Define the required schema
        schema = {
            "commands": ["generator", "solution_a", "solution_b"],
            "limits": [
                "problem_time_s",
                "problem_mem_mb",
                "brute_force_time_s",
                "brute_force_mem_mb",
            ],
            "tester": ["max_tests", "num_cores"],
            "paths": ["time_binary", "failing_input_file"],
        }

        for main_key, sub_keys in schema.items():
            if main_key not in config:
                raise KeyError(
                    f"Config Error: Missing required top-level key '{main_key}'."
                )

            for sub_key in sub_keys:
                if sub_key not in config[main_key]:
                    raise KeyError(
                        f"Config Error: Missing required key '{sub_key}' in '{main_key}' section."
                    )
        print("Config OK.")

    def _check_environment(self):
        """Checks for 'resource' module and '/usr/bin/time'."""
        if not IS_UNIX:
            print(
                f"{YELLOW}Warning: 'resource' module not found. Running without resource limits.{RESET}"
            )
            return False

        time_binary = Path(self.config["paths"]["time_binary"])
        if not time_binary.exists():
            print(
                f"{YELLOW}Warning: '{time_binary}' not found. Cannot measure peak memory.{RESET}"
            )
            return False
        return True

    @staticmethod
    def _make_limits_setter(time_s, mem_mb):
        """Returns a 'preexec_fn' function that sets resource limits."""

        def set_limits():
            # This function runs in the child process *before* exec
            if IS_UNIX:
                # Set CPU Time Limit (hard)
                resource.setrlimit(resource.RLIMIT_CPU, (time_s, time_s))

                # Set Address Space (Virtual Memory) Limit (hard)
                memory_bytes = mem_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

        return set_limits

    def _worker_sigterm_handler(self, signum, frame):
        """
        WORKER'S HANDLER
        Gracefully kill child process group on terminate.
        """
        if self.current_child_pgid:
            try:
                # Kill the entire process group, not just the child
                os.killpg(self.current_child_pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already died
        sys.exit(0)

    def _parse_time_output(self, stderr_str):
        """Parses the verbose output of /usr/bin/time (-v)."""
        try:
            user_time = float(
                re.search(r"User time \(seconds\): ([\d\.]+)", stderr_str).group(1)
            )
            sys_time = float(
                re.search(r"System time \(seconds\): ([\d\.]+)", stderr_str).group(1)
            )
            # This is the key: "Maximum resident set size" == "Peak RAM" (RSS)
            mem_kb = int(
                re.search(
                    r"Maximum resident set size \(kbytes\): (\d+)", stderr_str
                ).group(1)
            )

            return user_time + sys_time, mem_kb / 1024.0
        except (AttributeError, TypeError):
            # This is critical: if we can't parse, return 0.0
            # Our logic in _run_single_test will handle this.
            return 0.0, 0.0

    def _run_command(self, command, input_data, time_limit_s, mem_limit_mb):
        """
        Runs a command with specified OS-level limits.
        """
        # shlex.split handles spaces in file paths (e.g., "python 'My Solution.py'")
        command_parts = shlex.split(command)

        if self.can_measure:
            command_parts = [self.config["paths"]["time_binary"], "-v"] + command_parts

        # This wrapper function is the correct way to pass multiple
        # functions to preexec_fn and avoid lambda/tuple return issues.
        def preexec_tasks():
            os.setpgid(0, 0)  # Create a new process group
            self._make_limits_setter(time_limit_s, mem_limit_mb)()

        try:
            process = subprocess.Popen(
                command_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=preexec_tasks,
            )

            # Record the Process Group ID (which is the same as the child's PID)
            self.current_child_pgid = process.pid

            # Wall clock timeout (safety net)
            wall_timeout = time_limit_s + 2
            try:
                stdout_data, stderr_data = process.communicate(
                    input=input_data, timeout=wall_timeout
                )
            finally:
                # Ensure we clear the pgid once the process is done
                self.current_child_pgid = None

            cpu_time, peak_mem_mb = 0, 0
            if self.can_measure:
                # Check if 'time' output is present before parsing
                if ("User time" in stderr_data) or (
                    "Maximum resident set size" in stderr_data
                ):
                    cpu_time, peak_mem_mb = self._parse_time_output(stderr_data)
                else:
                    # 'time -v' didn't output what we expected
                    pass  # cpu_time and peak_mem_mb remain 0

            # Check if OS killed the process (e.g., TLE)
            if process.returncode != 0:
                error_type = "RE"  # Default
                if "MemoryError" in stderr_data:
                    error_type = "MLE (from Python)"
                elif "Command terminated by signal" in stderr_data:
                    if "CPU time limit exceeded" in stderr_data:
                        error_type = "TLE (OS)"
                    elif "Segmentation fault" in stderr_data:
                        error_type = "RE (Segfault)"
                    else:
                        # This is our safety net AS limit (e.g. 2GB)
                        error_type = "MLE (Safety Net)"
                return {
                    "stdout": stdout_data.strip(),
                    "stderr": stderr_data.strip(),
                    "time": cpu_time,
                    "mem_mb": peak_mem_mb,
                    "error": error_type,
                }

            # Process finished successfully
            return {
                "stdout": stdout_data.strip(),
                "stderr": stderr_data.strip(),
                "time": cpu_time,
                "mem_mb": peak_mem_mb,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            process.kill()  # Kill the '/usr/bin/time' process
            return {
                "stdout": "",
                "stderr": "",
                "time": wall_timeout,
                "mem_mb": 0,
                "error": "TLE (Wall)",
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Tester RE: {e}",
                "time": 0,
                "mem_mb": 0,
                "error": "Tester RE",
            }

    def _run_single_test(self, test_index):
        """
        The "worker" function that runs and judges a single test case.
        This runs in a separate process from the pool.
        """
        # Set the worker's own SIGTERM handler
        signal.signal(signal.SIGTERM, self._worker_sigterm_handler)

        # --- Define Limits ---
        problem_time_s = self.cfg_limits["problem_time_s"]
        problem_mem_mb = self.cfg_limits["problem_mem_mb"]
        safety_time_s = self.cfg_limits["brute_force_time_s"]
        safety_mem_mb = self.cfg_limits["brute_force_mem_mb"]

        # --- 1. Run Generator (with safety limits) ---
        gen_result = self._run_command(
            self.cfg_cmd["generator"], None, safety_time_s, safety_mem_mb
        )
        if gen_result["error"]:
            return (
                test_index,
                "Generator Error",
                "N/A",
                gen_result,
                gen_result,
                gen_result,
            )
        test_case = gen_result["stdout"]

        # --- 2. Run Solution A (with *hybrid* limits) ---
        sol_a_result = self._run_command(
            self.cfg_cmd["solution_a"],
            test_case,
            problem_time_s,  # Use REAL time limit (for OS TLE)
            safety_mem_mb,  # Use HIGH memory limit (to *measure* RSS)
        )

        # --- 3. Run Solution B (with safety limits) ---
        sol_b_result = self._run_command(
            self.cfg_cmd["solution_b"], test_case, safety_time_s, safety_mem_mb
        )

        # --- 4. Judge the Results ---

        # 4a. Check Brute Force
        if sol_b_result["error"]:
            return (
                test_index,
                "Brute Force Error",
                test_case,
                sol_a_result,
                sol_b_result,
                gen_result,
            )

        # 4b. Check Solution A's OS-level errors (TLE, RE, Segfault)
        if sol_a_result["error"]:
            return (
                test_index,
                sol_a_result["error"],
                test_case,
                sol_a_result,
                sol_b_result,
                gen_result,
            )

        # 4c. Check Measured Memory (MLE)
        if self.can_measure:
            # We *can* measure. Check if parsing failed (mem_mb is 0).
            # We check if mem_mb is 0 AND 'Maximum resident set size' is NOT in stderr,
            # which means parsing failed. A real 0MB program is fine.
            if (
                sol_a_result["mem_mb"] == 0.0
                and "Maximum resident set size" not in sol_a_result["stderr"]
            ):
                # This means parsing failed!
                return (
                    test_index,
                    "Measure Error",
                    test_case,
                    sol_a_result,
                    sol_b_result,
                    gen_result,
                )

            # Parsing succeeded. Now, check the actual limit.
            if sol_a_result["mem_mb"] > problem_mem_mb:
                return (
                    test_index,
                    "MLE (Measured)",
                    test_case,
                    sol_a_result,
                    sol_b_result,
                    gen_result,
                )

        else:
            # We *cannot* measure (e.g., /usr/bin/time missing).
            # We cannot give an "OK" verdict.
            return (
                test_index,
                "Measure Error",
                test_case,
                sol_a_result,
                sol_b_result,
                gen_result,
            )

        # 4d. Check for Wrong Answer (Only if TLE/RE/MLE all passed)
        if sol_a_result["stdout"] != sol_b_result["stdout"]:
            return (
                test_index,
                "Wrong Answer",
                test_case,
                sol_a_result,
                sol_b_result,
                gen_result,
            )

        # 5. If all passed, it's OK
        return (test_index, "OK", test_case, sol_a_result, sol_b_result, gen_result)

    def run(self):
        """Main entry point. Uses the global 'pool'."""
        global pool
        print(f"Starting {self.cfg_tester['max_tests']} tests...\n")

        pool = multiprocessing.Pool(processes=self.num_workers)
        test_indices = range(1, self.cfg_tester["max_tests"] + 1)
        tests_run = 0

        try:
            # imap_unordered is best for performance
            for result in pool.imap_unordered(self._run_single_test, test_indices):
                tests_run += 1
                test_index, verdict, test_case, sol_a, sol_b, gen_result = result

                # --- Centralized Printing ---
                if verdict == "OK":
                    print(f"{GREEN}.{RESET}", end="", flush=True)
                    if tests_run % 80 == 0:  # Newline every 80 tests
                        print()
                else:
                    # Failure found! Stop everything.
                    pool.terminate()

                    # --- Full Failure Report ---
                    print(
                        f"\n\n{RED}--- FAILURE on Test #{test_index}: {verdict} ---{RESET}"
                    )

                    time_str = f"Time: {sol_a['time']:.3f}s"
                    mem_str = f"Mem: {sol_a['mem_mb']:.1f}MB"
                    print(f"({time_str}, {mem_str})\n")

                    # Save the failing test case
                    failing_file = Path(self.cfg_paths["failing_input_file"])
                    failing_file.write_text(test_case)
                    print(f"Failing test case saved to '{failing_file}'\n")

                    # --- Detailed Report ---
                    print(f"{CYAN}--- INPUT ---{RESET}")
                    print(test_case)
                    print(f"\n{CYAN}--- YOUR ({verdict}) ANSWER ---{RESET}")
                    print(sol_a["stdout"])

                    if verdict == "Wrong Answer":
                        print(f"\n{CYAN}--- CORRECT (Brute) ANSWER ---{RESET}")
                        print(sol_b["stdout"])

                    if gen_result["stderr"]:
                        print(
                            f"\n{CYAN}--- GENERATOR STDERR ---{RESET}\n{gen_result['stderr']}"
                        )
                    if sol_a["stderr"]:
                        print(
                            f"\n{CYAN}--- YOUR (solution_a) STDERR ---{RESET}\n{sol_a['stderr']}"
                        )
                    if sol_b["stderr"]:
                        print(
                            f"\n{CYAN}--- BRUTE FORCE (solution_b) STDERR ---{RESET}\n{sol_b['stderr']}"
                        )

                    pool.join()  # Wait for termination
                    return  # Exit the run() method

            # Loop finished without a 'break'
            print(f"\n\n{GREEN}Passed all {tests_run} tests!{RESET}")
            pool.close()
            pool.join()

        except KeyboardInterrupt:
            # The SIGINT signal handler (_main_shutdown_handler)
            # already gracefully handles the pool shutdown.
            # This 'except' block just prevents an ugly
            # "KeyboardInterrupt" stack trace from printing.
            pass
        except Exception as e:
            # Catch any other unexpected error
            print(f"\n\n{RED}A critical error occurred: {e}{RESET}")
            if pool:
                pool.terminate()
                pool.join()


if __name__ == "__main__":
    if not IS_UNIX:
        print(
            f"{RED}Error: This stress tester relies on Unix-specific modules ('resource') and tools ('/usr/bin/time').{RESET}"
        )
        print("It will not run correctly on this system (e.g., native Windows).")
    else:
        # Register the graceful shutdown handlers for the MAIN script
        signal.signal(signal.SIGTERM, _main_shutdown_handler)
        signal.signal(signal.SIGINT, _main_shutdown_handler)  # Also catch Ctrl+C

        SCRIPT_DIR = Path(__file__).resolve().parent
        # Build the absolute path to the config.json file
        CONFIG_FILE_PATH = SCRIPT_DIR / "config.json"

        try:
            tester = StressTester(config_path=CONFIG_FILE_PATH, script_dir=SCRIPT_DIR)
            tester.run()
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            # Catch config-related startup errors
            print(f"\n{RED}Configuration Error: {e}{RESET}")
            sys.exit(1)
