# 🚀 Hướng Dẫn Deploy Image Search API lên Render

## 📋 Yêu Cầu Trước Khi Deploy

- ✅ Tài khoản GitHub
- ✅ Tài khoản Render (https://render.com)
- ✅ Code đã push lên GitHub repository

---

## 🔧 Bước 1: Chuẩn Bị Repository

### 1.1. Kiểm tra các file cần thiết:

```bash
# Kiểm tra cấu trúc project
SEARCH_IMG/
├── src/
│   ├── main.py
│   ├── api/
│   ├── config/
│   ├── models/
│   ├── services/
│   └── utils/
├── requirements.txt
├── Procfile
├── .gitignore
└── README.md
```

### 1.2. Push code lên GitHub:

```bash
cd c:\Users\Lenovo\STUDY\SEARCH_IMG

# Initialize git (nếu chưa có)
git init

# Add remote repository
git remote add origin https://github.com/HoaiNhu/SEARCH_IMG.git

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Push to GitHub
git push -u origin main
```

---

## 🌐 Bước 2: Tạo Web Service trên Render

### 2.1. Đăng nhập vào Render:

- Truy cập: https://render.com
- Đăng nhập bằng tài khoản GitHub

### 2.2. Tạo Web Service mới:

1. **Click "New +"** → Chọn **"Web Service"**

2. **Connect Repository:**

   - Chọn repository: `HoaiNhu/SEARCH_IMG`
   - Click **"Connect"**

3. **Cấu hình Web Service:**

   | Field              | Value                                              |
   | ------------------ | -------------------------------------------------- |
   | **Name**           | `image-search-api` (hoặc tên bạn muốn)             |
   | **Region**         | `Singapore` (gần Việt Nam nhất)                    |
   | **Branch**         | `main`                                             |
   | **Root Directory** | _(để trống)_                                       |
   | **Runtime**        | `Python 3`                                         |
   | **Build Command**  | `pip install -r requirements.txt`                  |
   | **Start Command**  | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |

4. **Instance Type:**
   - Chọn **"Free"** (miễn phí nhưng sẽ sleep sau 15 phút không hoạt động)
   - Hoặc **"Starter"** ($7/tháng - recommended cho production)

---

## 🔐 Bước 3: Cấu hình Environment Variables

Trong phần **Environment** của Render, thêm các biến môi trường:

| Key                    | Value                                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- |
| `MONGO_URI`            | `mongodb+srv://hnhu:hoainhu1234@webbuycake.asd8v.mongodb.net/?retryWrites=true&w=majority&appName=WebBuyCake` |
| `MONGO_DB_NAME`        | `test`                                                                                                        |
| `MONGO_COLLECTION`     | `products`                                                                                                    |
| `MODEL_NAME`           | `openai/clip-vit-base-patch32`                                                                                |
| `DEVICE`               | `cpu`                                                                                                         |
| `TOP_K`                | `10`                                                                                                          |
| `SIMILARITY_THRESHOLD` | `0.5`                                                                                                         |
| `PYTHON_VERSION`       | `3.11.0`                                                                                                      |

**⚠️ Lưu ý:**

- Không cần set `HOST` và `PORT` vì Render tự động xử lý
- Nếu muốn đổi mật khẩu MongoDB, tạo user mới trong MongoDB Atlas

---

## 🚀 Bước 4: Deploy

1. **Click "Create Web Service"**
2. Render sẽ bắt đầu build và deploy
3. Quá trình deploy có thể mất **10-15 phút** (do phải tải CLIP model ~605MB)

### Theo dõi logs:

- Click vào service → Tab **"Logs"**
- Xem quá trình build và start

---

## ✅ Bước 5: Kiểm Tra Deployment

### 5.1. Lấy URL của service:

Render sẽ tạo URL dạng:

```
https://image-search-api.onrender.com
```

### 5.2. Test API:

**Health Check:**

```bash
curl https://image-search-api.onrender.com/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "message": "Image Search API is running",
  "indexed_products": 50
}
```

**Test API Documentation:**

```
https://image-search-api.onrender.com/docs
```

### 5.3. Test Search by Image:

**Using Postman:**

1. Import file `Image_Search_API.postman_collection.json`
2. Thay đổi base URL thành: `https://image-search-api.onrender.com`
3. Test endpoint POST `/search/image`

**Using cURL:**

```bash
curl -X POST "https://image-search-api.onrender.com/search/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "top_k=5"
```

---

## 🔄 Bước 6: Cập Nhật Frontend

Trong project **FE-Project_AvocadoCake**, cập nhật file `.env`:

```env
REACT_APP_IMAGE_SEARCH_API_URL=https://image-search-api.onrender.com
```

Hoặc trong `ImageSearchService.js`:

```javascript
const API_BASE_URL = "https://image-search-api.onrender.com";
```

---

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### 1. **Build Failed - Memory Error:**

```
Solution: Nâng cấp lên Starter plan ($7/tháng) vì Free plan có RAM hạn chế
```

#### 2. **Service Sleeping:**

```
Free plan sẽ sleep sau 15 phút không hoạt động
Solution:
- Nâng cấp lên Starter plan
- Hoặc dùng cron job để ping service mỗi 10 phút
```

#### 3. **CLIP Model Download Failed:**

```
Logs: "Failed to download model"
Solution:
- Kiểm tra internet của Render server
- Wait và deploy lại
```

#### 4. **MongoDB Connection Error:**

```
Logs: "Failed to connect to MongoDB"
Solution:
- Kiểm tra MONGO_URI trong Environment Variables
- Whitelist IP của Render trong MongoDB Atlas (0.0.0.0/0)
```

#### 5. **CORS Error từ Frontend:**

```javascript
// Trong src/main.py, đảm bảo có:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring

### Check Logs:

```
Render Dashboard → Your Service → Logs
```

### Check Metrics:

```
Render Dashboard → Your Service → Metrics
- CPU Usage
- Memory Usage
- Request Count
```

### Set up Health Checks:

Render tự động ping `/` endpoint. Nếu muốn custom:

```
Settings → Health Check Path: /health
```

---

## 💰 Chi Phí Dự Kiến

| Plan         | Giá       | RAM   | CPU     | Đặc điểm                             |
| ------------ | --------- | ----- | ------- | ------------------------------------ |
| **Free**     | $0        | 512MB | 0.1 CPU | Sleep sau 15 phút, 750 giờ/tháng     |
| **Starter**  | $7/tháng  | 512MB | 0.5 CPU | Không sleep, suitable cho production |
| **Standard** | $25/tháng | 2GB   | 1 CPU   | Better performance                   |

**Khuyến nghị:** Dùng **Starter plan** ($7/tháng) cho production

---

## 🔒 Bảo Mật

### 1. Bảo vệ MongoDB:

```
- Đổi password mạnh hơn
- Whitelist chỉ IP của Render
- Enable MongoDB Atlas monitoring
```

### 2. Rate Limiting:

```python
# Thêm vào src/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/search/image")
@limiter.limit("10/minute")
async def search_image(...):
    ...
```

### 3. API Key Authentication:

```python
# Thêm API key trong headers
X-API-KEY: your-secret-key
```

---

## 🚀 Auto Deploy

Render tự động deploy khi có commit mới:

```bash
# Mỗi lần update code
git add .
git commit -m "Update feature"
git push origin main

# Render sẽ tự động build và deploy
```

Để tắt auto-deploy:

```
Settings → Auto-Deploy: OFF
```

---

## 📝 Checklist Deploy

- [ ] Code đã push lên GitHub
- [ ] File `requirements.txt` đầy đủ
- [ ] File `Procfile` có start command đúng
- [ ] Đã tạo Web Service trên Render
- [ ] Đã config Environment Variables
- [ ] Deploy thành công (check logs)
- [ ] Test `/health` endpoint
- [ ] Test `/docs` swagger UI
- [ ] Test `/search/image` với image thực
- [ ] Cập nhật URL trong frontend
- [ ] Test frontend integration

---

## 🆘 Liên Hệ & Hỗ Trợ

- **Render Support:** https://render.com/docs
- **Python FastAPI Docs:** https://fastapi.tiangolo.com/
- **CLIP Model:** https://huggingface.co/openai/clip-vit-base-patch32

---

## 🎉 Hoàn Thành!

API của bạn đã được deploy tại:

```
https://image-search-api.onrender.com
```

Test ngay:

```
https://image-search-api.onrender.com/docs
```

**Happy Coding! 🚀**
