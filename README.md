# Nén tệp văn bản bằng mã Huffman

Bài kiểm tra môn Thiết kế và phân tích thuật toán – Câu 1 (loại dữ liệu: **tệp văn bản**).

## Chạy chương trình (Python 3.8+, không cần thư viện ngoài)

```bash
python huffman.py compress   sample.txt sample.huf    # nén
python huffman.py decompress sample.huf restored.txt  # giải nén
python test_huffman.py                                # kiểm thử
python benchmark.py                                   # đo thời gian theo n
```

## Các bước thuật toán

| Bước | Hàm | Độ phức tạp |
|---|---|---|
| 1. Đếm tần suất | `count_frequencies` | Θ(n) |
| 2. Dựng cây Huffman bằng hàng đợi ưu tiên | `build_tree` | Θ(k log k) |
| 3. Sinh mã (chuẩn tắc) | `code_lengths`, `canonical_codes` | O(k log k) |
| 4. Mã hóa dữ liệu | `encode` | Θ(n · L̄) |
| Giải nén | `decompress` | Θ(số bit nén) |

Tổng: **T(n, k) = Θ(n + k log k)**; với văn bản byte (k ≤ 256) → **Θ(n)**.
