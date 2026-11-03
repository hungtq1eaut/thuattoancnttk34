import os
import random
import unittest
from huffman import compress, decompress, stats


class TestHuffman(unittest.TestCase):
    def roundtrip(self, data: bytes):
        self.assertEqual(decompress(compress(data)), data)

    def test_empty(self):
        self.roundtrip(b"")

    def test_single_symbol(self):
        self.roundtrip(b"aaaaaaa")

    def test_textbook_example(self):
        self.roundtrip(b"abracadabra")

    def test_vietnamese_utf8(self):
        self.roundtrip("Trường Đại học Công nghệ Đông Á – nén Huffman".encode("utf-8"))

    def test_all_bytes(self):
        self.roundtrip(bytes(range(256)) * 3)

    def test_random(self):
        rnd = random.Random(1)
        for _ in range(50):
            self.roundtrip(bytes(rnd.randrange(256) for _ in range(rnd.randrange(1, 2000))))

    def test_sample_file(self):
        path = os.path.join(os.path.dirname(__file__), "sample.txt")
        with open(path, "rb") as f:
            self.roundtrip(f.read())

    def test_optimal_vs_entropy(self):
        s = stats(b"this is an example of a huffman tree")
        # Định lý Shannon: H <= L < H + 1
        self.assertLessEqual(s["entropy"], s["avg_bits"])
        self.assertLess(s["avg_bits"], s["entropy"] + 1)


if __name__ == "__main__":
    unittest.main()
