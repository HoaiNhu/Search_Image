# 📮 Postman Testing Guide - Image Search API

## 🚀 Quick Start

### 1. Import Collection

1. Mở Postman
2. Click **Import** (góc trên bên trái)
3. Chọn file `Image_Search_API.postman_collection.json`
4. Click **Import**

### 2. Kiểm tra Environment Variables

Collection đã có sẵn 2 variables:

- `base_url`: `http://localhost:8001` (default)
- `test_image_url`: Sample product image URL

Nếu server chạy ở port khác, edit `base_url` trong Collection Variables.

---

## 🧪 Test Cases

### ✅ Test 1: Health Check

**Endpoint:** `GET /api/v1/health`

**Mục đích:** Kiểm tra API đang chạy và xem số products đã được index

**Expected Response:**

```json
{
  "status": "healthy",
  "total_products": 150,
  "indexed_products": 145
}
```

**Cách test:**

1. Chọn request "Health Check"
2. Click **Send**
3. Verify status code = 200
4. Check `indexed_products > 0`

---

### 🔍 Test 2: Search by Image Upload

**Endpoint:** `POST /api/v1/search/image`

**Mục đích:** Upload ảnh bánh và tìm sản phẩm tương tự

**Parameters:**

- `file` (required): Image file (JPEG, PNG, etc.)
- `top_k` (optional): Số lượng kết quả (default: 10)
- `threshold` (optional): Ngưỡng similarity (default: 0.5)

**Cách test:**

1. Chọn request "Search by Image Upload"
2. Trong tab **Body** → **form-data**
3. Click chọn file ở row `file`
4. Browse và chọn 1 ảnh bánh từ máy bạn
5. Điều chỉnh `top_k` và `threshold` nếu cần
6. Click **Send**

**Expected Response:**

```json
[
    {
        "product": {
            "productName": "Bánh hoa xuân",
            "productPrice": 260000,
            "productImage": "https://res.cloudinary.com/...",
            "productSize": 11,
            "productDescription": "Bánh được làm từ...",
            "averageRating": 4.3,
            "totalRatings": 9
        },
        "similarity_score": 0.9234,
        "rank": 1
    },
    ...
]
```

**Success Criteria:**

- Status code = 200
- Array có từ 1-10 items (tùy top_k)
- Mỗi item có `similarity_score` >= threshold
- Kết quả được sắp xếp theo rank (1, 2, 3...)

---

### 🌐 Test 3: Search by Image URL

**Endpoint:** `POST /api/v1/search/url`

**Mục đích:** Tìm kiếm bằng URL của ảnh (không cần upload)

**Parameters:**

- `image_url` (required): URL của ảnh
- `top_k` (optional): Số lượng kết quả
- `threshold` (optional): Ngưỡng similarity

**Cách test:**

1. Chọn request "Search by Image URL"
2. URL đã set sẵn là 1 product từ database của bạn
3. Click **Send**
4. Hoặc thay đổi `image_url` trong Params tab

**Test với product khác:**

```
https://res.cloudinary.com/dlyl41lgq/image/upload/v1735795001/products/file_u9ksse.jpg
```

**Expected Response:** Tương tự Test 2

---

### 🔄 Test 4: Refresh Product Features

**Endpoint:** `POST /api/v1/refresh`

**Mục đích:** Cập nhật lại features khi có product mới trong database

**Khi nào dùng:**

- Sau khi thêm sản phẩm mới vào MongoDB
- Sau khi update ảnh sản phẩm
- Khi muốn reset cache

**Cách test:**

1. Chọn request "Refresh Product Features"
2. Click **Send**

**Expected Response:**

```json
{
  "message": "Product features refreshed successfully",
  "total_products": 150,
  "indexed_products": 150
}
```

**Note:** Request này có thể mất 1-2 phút tùy số lượng products

---

## 🎯 Advanced Testing Scenarios

### Scenario 1: Tìm bánh giống với threshold cao

**Purpose:** Chỉ lấy bánh rất giống nhau

**Steps:**

1. Chọn "Search by Image Upload - High Threshold"
2. Upload ảnh bánh
3. `threshold=0.7` (70% similarity)
4. `top_k=10`

**Expected:** Chỉ trả về bánh rất tương tự, có thể < 10 results

---

### Scenario 2: Test với ảnh không phải bánh

**Purpose:** Kiểm tra API handle ảnh không match

**Steps:**

1. Upload ảnh không phải bánh (ví dụ: xe hơi, người)
2. `threshold=0.5`
3. `top_k=5`

**Expected:**

- Status 200
- Array rỗng hoặc có ít results với similarity_score thấp

---

### Scenario 3: Test với ảnh lỗi

**Purpose:** Kiểm tra error handling

**Test cases:**

- Upload file không phải ảnh (.txt, .pdf)
- Upload ảnh bị corrupt
- URL không tồn tại
- URL không phải ảnh

**Expected:**

- Status 400 hoặc 500
- Error message rõ ràng

---

## 🔧 Troubleshooting

### ❌ Connection Refused

**Problem:** `Error: connect ECONNREFUSED 127.0.0.1:8001`

**Solution:**

- Kiểm tra server đang chạy: `python run.py`
- Check port đúng trong `base_url`

---

### ❌ Empty Results

**Problem:** API trả về array rỗng `[]`

**Possible causes:**

1. **Threshold quá cao**: Giảm threshold xuống 0.3-0.5
2. **Chưa index products**: Gọi `/refresh` endpoint
3. **Database rỗng**: Kiểm tra MongoDB có products không

---

### ❌ Slow Response

**Problem:** Request mất >5 giây

**Normal for:**

- Lần đầu gọi API (loading model)
- `/refresh` endpoint (re-indexing)

**Solutions:**

- Đợi model load xong (1-2 phút đầu)
- Với <1000 products, search nên <1s

---

## 📊 Performance Benchmarks

| Endpoint        | Expected Time | Notes                 |
| --------------- | ------------- | --------------------- |
| `/health`       | < 50ms        | Very fast             |
| `/search/image` | 200-500ms     | First time slower     |
| `/search/url`   | 300-600ms     | Includes download     |
| `/refresh`      | 30-120s       | Depends on # products |

---

## 💡 Tips

### Tip 1: Test với ảnh từ database

```
GET products từ MongoDB → Copy productImage URL → Paste vào search/url
```

→ Nên trả về chính product đó với similarity ~0.99

### Tip 2: So sánh với ảnh tương tự

- Upload ảnh bánh kem trắng → Nên match với bánh kem trắng khác
- Upload bánh sinh nhật → Match với bánh sinh nhật
- Upload bánh tart → Match với bánh tart

### Tip 3: Adjust threshold

- `0.3-0.5`: Broad search, nhiều results
- `0.6-0.7`: Medium similarity
- `0.8-0.9`: Very similar only
- `0.95+`: Almost identical

---

## 🧪 Testing Checklist

### Basic Functionality

- [ ] Health check returns 200
- [ ] Can upload image and get results
- [ ] Can search by URL
- [ ] Results sorted by similarity
- [ ] Refresh endpoint works

### Edge Cases

- [ ] Empty image file
- [ ] Invalid file format
- [ ] Invalid URL
- [ ] Very large image (>10MB)
- [ ] Threshold = 0.0
- [ ] Threshold = 1.0
- [ ] top_k = 1
- [ ] top_k = 50

### Performance

- [ ] Response time acceptable
- [ ] Multiple concurrent requests
- [ ] API stable after refresh

---

## 🎓 Example Test Flow

```
1. Health Check → Verify API ready
2. Search by URL (existing product) → Should find itself
3. Upload similar cake image → Check similarity scores
4. Try different thresholds → Compare results
5. Refresh → Verify reindexing works
6. Repeat search → Ensure consistent results
```

---

## 📝 Notes

- Collection có built-in tests tự động check status code
- Có thể export results từ Postman để so sánh
- Save favorite requests vào folder riêng
- Share collection với team members

Happy Testing! 🎂🔍
