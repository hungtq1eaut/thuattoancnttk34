"""Đo thời gian nén/giải nén theo kích thước n để kiểm chứng T(n) = Θ(n + k log k)."""
import time
from huffman import compress, decompress

with open("sample.txt", "rb") as f:
    base = f.read()

print(f"{'n (byte)':>10} {'nén (ms)':>10} {'giải nén (ms)':>14} {'µs/byte (nén)':>14} {'tỉ lệ nén':>10}")
for mult in (20, 40, 80, 160, 320, 640):
    data = base * mult
    t0 = time.perf_counter(); c = compress(data); t1 = time.perf_counter()
    d = decompress(c); t2 = time.perf_counter()
    assert d == data
    print(f"{len(data):>10} {(t1-t0)*1e3:>10.1f} {(t2-t1)*1e3:>14.1f} "
          f"{(t1-t0)*1e6/len(data):>14.3f} {len(c)/len(data):>10.2%}")
