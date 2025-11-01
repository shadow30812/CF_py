"""
File: <<filename>>
Author: <<author>>
Affiliated to: <<company>>
Created: <<dateformat('dddd MMMM Do YYYY HH:mm:ss')>>
"""

import math
import sys

# sys.setrecursionlimit(10**6)

inf = math.inf
eps = 1e-9
mod = 10**9 + 7
# mod = 998244353

std_in, basic, search_sort, packages = 1, 1, 1, 1
out_tog = 0
graph = 0
hashing = 0
rof = 0
de = 0


if True:
    if std_in:
        _input = input  # Display prompt to stdout
        input = lambda: sys.stdin.readline().rstrip()

        def intput():
            return sys.stdin.readline()

        def printf(tbp: list[str]):
            sys.stdout.write("\n".join(tbp) + "\n")

        def sprint(op: list[str]):
            sys.stdout.write(" ".join(op) + "\n")

        def iprint(arr: list[int]):
            sys.stdout.write("\n".join(map(str, arr)) + "\n")

        def I():
            return input()

        def II():
            return int(intput())

        def MII():
            return map(int, intput().split())

        def LI():
            return input().split()

        def LII():
            return list(map(int, intput().split()))

        def LFI():
            return list(map(float, input().split()))

    if basic:

        def find(L: list, tg):
            try:
                return L.index(tg)
            except ValueError:
                return -1

        def exp(x, n, m=None):
            modular = m is not None
            if modular:
                x %= m
            res = 1

            while n:
                if n % 2:
                    res = res * x
                    if modular:
                        res %= m

                x = x * x
                if modular:
                    x %= m
                n //= 2

            return res

        def fmax(x, y):
            return x if x > y else y

        def fmin(x, y):
            return x if x < y else y

        def feq(x: float, y: float):
            return abs(x - y) <= max(eps * max(abs(x), abs(y)), eps)

        def nprime(n: int):
            if n <= 1:
                return False
            if n % 2 == 0:
                return n == 2

            max_div = math.ceil(math.sqrt(n))
            for i in range(3, max_div, 2):
                if n % i == 0:
                    return False
            return True

        def allprime(n):
            prime = [True for _ in range(n + 1)]
            p = 2

            while p * p <= n:
                if prime[p]:
                    for i in range(p * p, n + 1, p):
                        prime[i] = False
                p += 1
            c = 0

            for p in range(2, n):
                if prime[p]:
                    c += 1
            return c

        PRIMES = [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
            101,
            103,
            107,
            109,
            113,
            127,
            131,
            137,
            139,
            149,
            151,
            157,
            163,
            167,
            173,
            179,
            181,
            191,
            193,
            197,
            199,
        ]

        class PrefixSum:
            def __init__(self, a, n):
                self.a, self.n = a, n
                self.arr = [0] * n
                for i in range(1, n + 1):
                    self.arr[i] = self.arr[i - 1] + a[i]

            def ret(self):
                return self.arr

            def psum(self, i):
                return self.arr[i]

            def rsum(self, L, R):
                return self.arr[R] if L == 0 else self.arr[R] - self.arr[L - 1]

            def xsum(self, x):
                cnt = {0: 1}
                res = 0
                for i in self.arr:
                    tg = i - x
                    if tg in cnt:
                        res += cnt[tg]
                    cnt[i] = cnt.get(i, 0) + 1
                return res

            def pxor(self):
                p = [0] * self.n
                for i in range(self.n):
                    p[i] = p[i - 1] ^ self.a[i]
                return p

        class logix(PrefixSum):
            def __init__(self):
                self.a, self.n = super().a, super().n
                self.p = p = [[0] * 30 for _ in range(self.n)]
                for i in range(30):
                    for j in range(1, super().n + 1):
                        p[i][j] = p[i][j - 1] + ((self.a[j] >> i) & 1)

            def AND(self, L, R):
                res = 0
                for i in range(30):
                    if self.p[i][R] - self.p[i][L - 1] == R - L + 1:
                        res += 1 << i
                return res

            def OR(self, L, R):
                res = 0
                for i in range(30):
                    if self.p[i][R] - self.p[i][L - 1] > 0:
                        res += 1 << i
                return res

    if packages:
        import bisect as bs
        import cmath
        import os
        import random
        from collections import Counter as ctr
        from collections import defaultdict as dd
        from collections import deque as dq
        from copy import deepcopy
        from functools import (
            cmp_to_key,
            lru_cache,
            reduce,
        )
        from heapq import heapify as hpfy
        from heapq import heappop as hpop
        from heapq import heappush as hpsh
        from heapq import (
            heappushpop,
            merge,
            nlargest,
            nsmallest,
        )
        from heapq import heapreplace as hrep
        from io import BytesIO, IOBase
        from itertools import (
            accumulate,
            combinations,
            count,
            permutations,
            product,
        )
        from operator import itemgetter
        from string import ascii_letters as a_al
        from string import ascii_lowercase as a_lc
        from string import ascii_uppercase as a_uc

        try:
            from sortedcontainers import SortedDict as sd
            from sortedcontainers import SortedList as sl
            from sortedcontainers import SortedSet as ss
        except ImportError:
            pass

        BUFSIZE = 4096

    if search_sort:

        def bin_search(arr, tg, lo=0, hi: int | None = None):
            left, right = lo, hi or len(arr) - 1
            while left <= right:
                mid = left + (right - left) // 2
                if arr[mid] == tg:
                    return mid
                elif arr[mid] < tg:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1

        def lower_bound(arr, tg):
            left, right = 0, len(arr)
            while left < right:
                mid = left + (right - left) // 2
                if arr[mid] < tg:
                    left = mid + 1
                else:
                    right = mid
            return left

        def csort(L):
            if len(L) < 2:
                return L

            top = max(L)
            bot = min(L)
            new = []
            ct = [0] * (top - bot + 1)

            for num in L:
                ct[num - bot] += 1
            for n, c in enumerate(ct):
                new.extend([n + bot] * c)
            return new

        def merge_sub(arr, temp, l, mid, r):
            for idx in range(l, r + 1):
                temp[idx] = arr[idx]

            i = k = l
            j = mid + 1

            while i <= mid and j <= r:
                if temp[i] <= temp[j]:
                    arr[k] = temp[i]
                    i += 1
                else:
                    arr[k] = temp[j]
                    j += 1
                k += 1

            while i <= mid:
                arr[k] = temp[i]
                i += 1
                k += 1

            while j <= r:
                arr[k] = temp[j]
                j += 1
                k += 1

        def msort(L, n):
            temp = [0] * n
            sz = 1
            while sz < n:
                l = 0
                while l < n - 1:
                    mid = min(l + sz - 1, n - 1)
                    r = min(l + 2 * sz - 1, n - 1)
                    merge_sub(L, temp, l, mid, r)
                    l += 2 * sz
                sz *= 2
            return L

        def rbk(text, pattern):
            """
            Rabin-Karp algorithm with a rolling hash... O(N*M) worst case
            """
            N = len(text)
            M = len(pattern)

            if M > N:
                return -1

            MOD = 10**9 + 7
            BASE = 256
            H_POW = pow(BASE, M - 1, MOD)

            hash_pattern = 0
            hash_text = 0

            for i in range(M):
                hash_pattern = (hash_pattern * BASE + ord(pattern[i])) % MOD
                hash_text = (hash_text * BASE + ord(text[i])) % MOD

            for i in range(N - M + 1):
                if hash_text == hash_pattern:
                    if text[i : i + M] == pattern:
                        return i

                if i < N - M:
                    hash_text = (hash_text - ord(text[i]) * H_POW) % MOD
                    hash_text = (hash_text * BASE) % MOD
                    hash_text = (hash_text + ord(text[i + M])) % MOD

                    if hash_text < 0:
                        hash_text += MOD

            return -1

        def kmp(text, pattern):
            """
            Knuth-Morris-Pratt algorithm with no backtracks... O(N + M) all case
            """
            N = len(text)
            M = len(pattern)

            if not M:
                return 0
            if M > N:
                return -1

            lps = [0] * M
            hash_length = 0
            i = 1

            while i < M:
                if pattern[i] == pattern[hash_length]:
                    hash_length += 1
                    lps[i] = hash_length
                    i += 1
                else:
                    if hash_length:
                        hash_length = lps[hash_length - 1]
                    else:
                        lps[i] = 0
                        i += 1

            i = 0
            j = 0

            while i < N:
                if pattern[j] == text[i]:
                    i += 1
                    j += 1

                if j == M:
                    return i - j

                elif i < N and pattern[j] != text[i]:
                    if j:
                        j = lps[j - 1]
                    else:
                        i += 1

            return -1

    if out_tog:
        import os
        from io import BytesIO, IOBase

        class FastIO(IOBase):
            newlines = 0

            def __init__(self, file):
                self._fd = file.fileno()
                self.buffer = BytesIO()
                self.writable = "x" in file.mode or "r" not in file.mode
                self.write = self.buffer.write if self.writable else None

            def read(self):
                while True:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    if not b:
                        break
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines = 0
                return self.buffer.read()

            def readline(self, size: int | None = -1):
                while self.newlines == 0:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    self.newlines = b.count(b"\n") + (not b)
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines -= 1
                return self.buffer.readline()

            def flush(self):
                if self.writable:
                    os.write(self._fd, self.buffer.getvalue())
                    self.buffer.truncate(0), self.buffer.seek(0)

        class IOWrapper(IOBase):
            def __init__(self, file):
                self.buffer = FastIO(file)
                self.flush = self.buffer.flush
                self.writable = self.buffer.writable
                self.write = lambda s: self.buffer.write(s.encode("ascii"))
                self.read = lambda: self.buffer.read().decode("ascii")
                self.readline = lambda: self.buffer.readline().decode("ascii")

        sys.stdout = IOWrapper(sys.stdout)

    if graph:
        from types import GeneratorType

        # Graph 1-indexing -> list 0-idx
        def GMI():
            return map(lambda x: int(x) - 1, intput().split())

        def LGMI():
            return list(map(lambda x: int(x) - 1, intput().split()))

        def bootstrap(f, stk=[]):
            def wrappedfunc(*args, **kwargs):
                if stk:
                    return f(*args, **kwargs)
                else:
                    to = f(*args, **kwargs)
                    while True:
                        if type(to) is GeneratorType:
                            stk.append(to)
                            to = next(to)
                        else:
                            stk.pop()
                            if not stk:
                                break
                            to = stk[-1].send(to)
                    return to

            return wrappedfunc

        class lst_lst:
            def __init__(self, n):
                self.n = n
                self.pre = []
                self.cur = []
                self.notest = [-1] * (n + 1)

            def append(self, i, j):
                self.pre.append(self.notest[i])
                self.notest[i] = len(self.cur)
                self.cur.append(j)

            def iterate(self, i):
                tmp = self.notest[i]
                while tmp != -1:
                    yield self.cur[tmp]
                    tmp = self.pre[tmp]

        class FenwickTree:
            def __init__(self, size_or_list):
                if isinstance(size_or_list, int):
                    self.n = size_or_list
                    self.tree = [0] * (self.n + 1)
                else:
                    self.n = len(size_or_list)
                    self.tree = [0] * (self.n + 1)
                    for i in range(self.n):
                        self._add(i + 1, size_or_list[i])

            def _add(self, i, delta):
                while i <= self.n:
                    self.tree[i] += delta
                    i += i & (-i)

            def _query(self, i):
                s = 0
                while i > 0:
                    s += self.tree[i]
                    i -= i & (-i)
                return s

            def update(self, i, delta):
                self._add(i + 1, delta)

            def query(self, i):
                return self._query(i + 1)

            def range_query(self, l, r):
                return self._query(r + 1) - self._query(l)

        class SegmentTree:
            def __init__(self, arr, merge_func, identity_val):
                self.n = len(arr)
                self.merge = merge_func
                self.identity = identity_val
                self.tree = [self.identity] * (2 * self.n)
                for i in range(self.n):
                    self.tree[self.n + i] = arr[i]
                self._build()

            def _build(self):
                for i in range(self.n - 1, 0, -1):
                    self.tree[i] = self.merge(self.tree[2 * i], self.tree[2 * i + 1])

            def update(self, pos, new_val):
                pos += self.n
                self.tree[pos] = new_val
                while pos > 1:
                    if pos % 2 == 0:
                        self.tree[pos // 2] = self.merge(
                            self.tree[pos], self.tree[pos + 1]
                        )
                    else:
                        self.tree[pos // 2] = self.merge(
                            self.tree[pos - 1], self.tree[pos]
                        )
                    pos //= 2

            def query(self, l, r):
                res_left = self.identity
                res_right = self.identity
                l += self.n
                r += self.n + 1
                while l < r:
                    if l % 2 == 1:
                        res_left = self.merge(res_left, self.tree[l])
                        l += 1
                    if r % 2 == 1:
                        r -= 1
                        res_right = self.merge(self.tree[r], res_right)
                    l //= 2
                    r //= 2
                return self.merge(res_left, res_right)

        def bfs(graph, start_node, n):
            from collections import deque

            dist = [inf] * n
            dist[start_node] = 0
            q = deque([start_node])
            while q:
                u = q.popleft()
                for v in graph[u]:
                    if dist[v] == inf:
                        dist[v] = dist[u] + 1
                        q.append(v)
            return dist

        def dfs(graph, start_node, n):
            visited = set()
            stack = [start_node]
            while stack:
                u = stack.pop()
                if u not in visited:
                    visited.add(u)
                    for v in reversed(graph[u]):
                        if v not in visited:
                            stack.append(v)
            return visited

        def dijkstra(graph, start_node, n):
            import heapq

            dist = {i: inf for i in range(n)}
            dist[start_node] = 0
            pq = [(0, start_node)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for v, weight in graph[u]:
                    if dist[u] + weight < dist[v]:
                        dist[v] = dist[u] + weight
                        heapq.heappush(pq, (dist[v], v))
            return dist

    if hashing:
        import random

        RANDOM = random.getrandbits(20)

        class Wrapper(int):
            def __init__(self, x):
                int.__init__(x)

            def __hash__(self):
                return super(Wrapper, self).__hash__() ^ RANDOM

    if rof:
        file = open("input.txt", "r").readline().strip()[1:-1]
        fin = open(file, "r")

        def input():
            return fin.readline().strip()

        output_file = open("output.txt", "w")

        def fprint(*args, **kwargs):
            print(*args, **kwargs, file=output_file)

    if de:

        def debug(*args, **kwargs):
            print("\033[92m", end="")
            print(*args, **kwargs)
            print("\033[0m", end="")


def solve():
    pass


def main():
    # solve()

    for _ in range(II()):
        solve()

    # res: list[str] = [solve() for _ in range(II())]
    # printf(res)

    # iris: list[int] = [solve() for _ in range(II())]
    # iprint(iris)


if __name__ == "__main__":
    main()
