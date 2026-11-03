"""
Nén / giải nén tệp văn bản bằng mã Huffman.

Cách dùng:
    python huffman.py compress   input.txt  output.huf
    python huffman.py decompress input.huf  output.txt

Định dạng tệp .huf (dùng mã Huffman dạng chuẩn tắc - canonical):
    [4 byte]  số byte gốc n
    [2 byte]  số ký hiệu khác nhau k
    k x [1 byte ký hiệu + 1 byte độ dài mã]  (đủ để dựng lại bảng mã)
    [1 byte]  số bit đệm ở byte cuối
    [...]     dãy bit đã mã hóa
"""
import heapq
import struct
import sys
from collections import Counter
from itertools import count


class Node:
    __slots__ = ("freq", "symbol", "left", "right")

    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol      # None với nút trong
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.symbol is not None


# ---------- Bước 1: đếm tần suất  O(n) ----------
def count_frequencies(data: bytes) -> dict:
    return dict(Counter(data))


# ---------- Bước 2: dựng cây Huffman  O(k log k) ----------
def build_tree(freq: dict) -> Node:
    tie = count()  # phá hòa khi tần suất bằng nhau -> kết quả tất định
    heap = [(f, next(tie), Node(f, s)) for s, f in sorted(freq.items())]
    heapq.heapify(heap)                               # O(k)
    if len(heap) == 1:                                # chỉ 1 ký hiệu: thêm nút giả
        f, _, only = heap[0]
        return Node(f, None, only, None)
    while len(heap) > 1:                              # k - 1 lần lặp
        f1, _, a = heapq.heappop(heap)                # O(log k)
        f2, _, b = heapq.heappop(heap)                # O(log k)
        heapq.heappush(heap, (f1 + f2, next(tie), Node(f1 + f2, None, a, b)))
    return heap[0][2]


# ---------- Bước 3: sinh bảng mã  O(k) (+ O(k log k) để chuẩn tắc hóa) ----------
def code_lengths(root: Node) -> dict:
    """Duyệt cây, độ dài mã của mỗi ký hiệu = độ sâu của lá."""
    lengths = {}
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if node is None:
            continue
        if node.is_leaf():
            lengths[node.symbol] = max(depth, 1)
        else:
            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))
    return lengths


def canonical_codes(lengths: dict) -> dict:
    """Mã chuẩn tắc: cùng độ dài như cây Huffman (nên vẫn tối ưu), nhưng chỉ cần
    lưu độ dài mã trong header thay vì cả cây/bảng tần suất."""
    codes = {}
    code = 0
    prev_len = 0
    for sym, length in sorted(lengths.items(), key=lambda x: (x[1], x[0])):
        code <<= (length - prev_len)
        codes[sym] = format(code, f"0{length}b")
        code += 1
        prev_len = length
    return codes


def build_codes(root: Node) -> dict:
    return canonical_codes(code_lengths(root))


# ---------- Bước 4: mã hóa  O(n + tổng số bit) ----------
def encode(data: bytes, codes: dict) -> tuple:
    bits = "".join(codes[b] for b in data)
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    out = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return out, padding


def compress(data: bytes) -> bytes:
    header = struct.pack(">I", len(data))
    if not data:
        return header + struct.pack(">H", 0)
    freq = count_frequencies(data)                   # O(n)
    lengths = code_lengths(build_tree(freq))         # O(k log k)
    codes = canonical_codes(lengths)                 # O(k log k)
    payload, padding = encode(data, codes)           # O(n * L)
    table = b"".join(struct.pack(">BB", s, l) for s, l in sorted(lengths.items()))
    return header + struct.pack(">H", len(lengths)) + table + struct.pack(">B", padding) + payload


# ---------- Giải nén  O(tổng số bit) ----------
def decompress(blob: bytes) -> bytes:
    n = struct.unpack_from(">I", blob, 0)[0]
    k = struct.unpack_from(">H", blob, 4)[0]
    if n == 0:
        return b""
    pos = 6
    lengths = {}
    for _ in range(k):
        s, l = struct.unpack_from(">BB", blob, pos)
        lengths[s] = l
        pos += 2
    padding = blob[pos]
    pos += 1
    decode_table = {c: s for s, c in canonical_codes(lengths).items()}  # mã -> ký hiệu
    out = bytearray()
    cur = ""
    total_bits = (len(blob) - pos) * 8 - padding
    bits = "".join(format(b, "08b") for b in blob[pos:])[:total_bits]
    for bit in bits:                       # mỗi bit được đọc đúng 1 lần
        cur += bit
        sym = decode_table.get(cur)
        if sym is not None:                # mã tiền tố: khớp là chắc chắn đúng
            out.append(sym)
            cur = ""
            if len(out) == n:
                break
    return bytes(out)


def stats(data: bytes) -> dict:
    """Thông tin để báo cáo: bảng mã, độ dài trung bình, entropy."""
    import math
    freq = count_frequencies(data)
    codes = build_codes(build_tree(freq))
    n = len(data)
    avg = sum(freq[s] * len(codes[s]) for s in freq) / n
    entropy = -sum((f / n) * math.log2(f / n) for f in freq.values())
    return {"n": n, "k": len(freq), "avg_bits": avg, "entropy": entropy, "codes": codes, "freq": freq}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("compress", "decompress"):
        print(__doc__)
        sys.exit(1)
    mode, src, dst = sys.argv[1:]
    with open(src, "rb") as f:
        data = f.read()
    result = compress(data) if mode == "compress" else decompress(data)
    with open(dst, "wb") as f:
        f.write(result)
    print(f"{mode}: {len(data)} byte -> {len(result)} byte"
          + (f" (tỉ lệ nén {len(result) / len(data):.2%})" if mode == "compress" and data else ""))


if __name__ == "__main__":
    main()
