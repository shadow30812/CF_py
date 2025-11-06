import json

t = 1

if t:
    template_file = "rough.py"
    boilerplate_file = "boilerplate.json"

    print(f"🐍 Reading boilerplate from '{template_file}'...")

    try:
        with open(template_file, "r") as f:
            lines = [line.rstrip("\n") for line in f]

        json_output = json.dumps(lines, indent=4, ensure_ascii=False)

        print(
            "\n✅ Success! Copy the array below (from '[' to ']') and paste it into your settings.json:\n"
        )
        print(json_output)

        with open(boilerplate_file, "w+") as bp:
            bp.writelines(json_output)
            print(
                f"\nThe same has been written to the file {boilerplate_file} in the parent directory.\n\n"
            )

    except FileNotFoundError:
        print(f"\n❌ Error: The file '{template_file}' was not found.")
        print(
            "Please make sure this script is in the same directory as your template file."
        )

else:
    input_json_file = "boilerplate.json"
    output_txt_file = "rough.txt"

    print(f"Reading JSON data from '{input_json_file}'...")

    try:
        with open(input_json_file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        print(f"Writing formatted text to '{output_txt_file}'...")

        with open(output_txt_file, "w", encoding="utf-8") as txt_file:
            formatted_text = json.dumps(data, indent=4, ensure_ascii=False)
            txt_file.write(formatted_text)

        print("\n✅ Conversion successful!")
        print(f"Check the output in '{output_txt_file}'.")

    except FileNotFoundError:
        print(f"\n❌ Error: The file '{input_json_file}' was not found.")
        print("Please make sure the file exists in the same directory as the script.")
    except json.JSONDecodeError:
        print(f"\n❌ Error: Could not decode JSON from '{input_json_file}'.")
        print("Please ensure it is a valid JSON file.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
