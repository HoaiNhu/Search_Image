# 🔍 Image Search API

API tìm kiếm sản phẩm bánh dựa trên hình ảnh sử dụng CLIP model và MongoDB.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![CLIP](https://img.shields.io/badge/Model-CLIP-orange.svg)](https://github.com/openai/CLIP)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)](https://www.mongodb.com/)

> 🚀 **Quick Deploy to Render**: [DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md) (5 phút)
>
> 📖 **Chi tiết deploy**: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)

## 🌟 Tính năng

- **Tìm kiếm bằng hình ảnh**: Upload hình ảnh để tìm các sản phẩm tương tự
- **Tìm kiếm bằng URL**: Sử dụng URL hình ảnh để tìm kiếm
- **Độ chính xác cao**: Sử dụng CLIP model (OpenAI) cho feature extraction
- **RESTful API**: Dễ dàng tích hợp với frontend
- **Clean Architecture**: Code có cấu trúc rõ ràng, dễ mở rộng
- **Auto-refresh**: Có thể refresh database khi có sản phẩm mới

## 📁 Cấu trúc project

```
SEARCH_IMG/
├── src/
│   ├── api/              # API routes và endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── config/           # Configuration settings
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   └── product.py
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── feature_extractor.py
│   │   └── search_service.py
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   ├── image_utils.py
│   │   └── logger.py
│   ├── __init__.py
│   └── main.py           # Application entry point
├── .env                  # Environment variables
├── .gitignore
├── requirements.txt      # Python dependencies
└── README.md
```

## 🚀 Cài đặt

### 1. Clone hoặc tạo môi trường ảo

```bash
cd SEARCH_IMG
python -m venv venv
```

### 2. Kích hoạt môi trường ảo

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
venv\Scripts\activate.bat
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

File `.env` đã được tạo sẵn với cấu hình mặc định. Bạn có thể chỉnh sửa nếu cần:

```env
MONGO_URI=mongodb+srv://username:password@webbuycake.asd8v.mongodb.net/?retryWrites=true&w=majority&appName=WebBuyCake
MONGO_DB_NAME=test
MONGO_COLLECTION=products
HOST=0.0.0.0
PORT=8001
MODEL_NAME=openai/clip-vit-base-patch32
DEVICE=cpu
TOP_K=10
SIMILARITY_THRESHOLD=0.5
```

## 🎯 Chạy ứng dụng

### Development mode với auto-reload

```bash
cd src
python main.py
```

Hoặc sử dụng uvicorn trực tiếp:

```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Production mode

```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

Server sẽ chạy tại: `http://localhost:8001`

## 📚 API Documentation

Sau khi chạy server, truy cập:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Endpoints chính

#### 1. Health Check

```
GET /api/v1/health
```

Kiểm tra trạng thái service và số lượng sản phẩm đã index.

#### 2. Tìm kiếm bằng upload hình ảnh

```
POST /api/v1/search/image
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)
- top_k: Số lượng kết quả (optional, default: 10)
- threshold: Ngưỡng similarity (optional, default: 0.5)
```

**Ví dụ với curl:**

```bash
curl -X POST "http://localhost:8001/api/v1/search/image?top_k=5&threshold=0.6" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/image.jpg"
```

**Ví dụ với JavaScript (Frontend):**

```javascript
const formData = new FormData();
formData.append("file", imageFile);

const response = await fetch(
  "http://localhost:8001/api/v1/search/image?top_k=5&threshold=0.6",
  {
    method: "POST",
    body: formData,
  }
);

const results = await response.json();
console.log(results);
```

#### 3. Tìm kiếm bằng URL hình ảnh

```
POST /api/v1/search/url
Parameters:
- image_url: URL của hình ảnh (required)
- top_k: Số lượng kết quả (optional, default: 10)
- threshold: Ngưỡng similarity (optional, default: 0.5)
```

**Ví dụ:**

```bash
curl -X POST "http://localhost:8001/api/v1/search/url?image_url=https://example.com/image.jpg&top_k=5"
```

#### 4. Refresh product features

```
POST /api/v1/refresh
```

Cập nhật lại features của products từ database. Gọi endpoint này khi có sản phẩm mới được thêm vào.

### Response format

Tất cả search endpoints trả về format:

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

## 🔧 Technical Stack

- **FastAPI**: Web framework
- **PyMongo**: MongoDB driver
- **CLIP Model**: OpenAI's CLIP (openai/clip-vit-base-patch32) cho image feature extraction
- **Scikit-learn**: Cosine similarity calculation
- **PIL/Pillow**: Image processing
- **Transformers**: Hugging Face transformers library

## 🎓 Cách hoạt động

1. **Initialization**:

   - Khi server khởi động, service sẽ tải tất cả products từ MongoDB
   - Extract features từ tất cả hình ảnh sản phẩm sử dụng CLIP model
   - Lưu features vào memory để tăng tốc độ tìm kiếm

2. **Search Process**:

   - Frontend upload hình ảnh lên API
   - Extract features từ hình ảnh query
   - Tính cosine similarity với tất cả product features
   - Lọc kết quả theo threshold
   - Sắp xếp và trả về top K results

3. **Performance**:
   - Features được pre-compute và cache trong memory
   - Với <1000 products, search rất nhanh (< 100ms)
   - CLIP model cho accuracy cao cho cake images

## 🔐 Security Notes

- Trong production, cấu hình CORS cẩn thận trong `main.py`
- Sử dụng environment variables cho sensitive data
- Cân nhắc thêm authentication cho refresh endpoint

## 🚢 Deployment

### 🌐 Deploy lên Render (Recommended)

**Quick Start (5 phút):**

```bash
# 1. Push code
git push origin main

# 2. Vào Render Dashboard
# 3. New Web Service → Connect repo
# 4. Config và Deploy
```

**Xem hướng dẫn chi tiết:**

- [DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md) - Deploy nhanh trong 5 phút
- [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) - Hướng dẫn đầy đủ

### 🐳 Docker

Sử dụng Dockerfile có sẵn:

```bash
docker build -t image-search-api .
docker run -p 8001:8001 --env-file .env image-search-api
```

### 🔄 Keep-Alive (Free Plan)

Nếu dùng Render Free plan, chạy script để tránh sleep:

```bash
python keep_alive.py
```

Hoặc dùng cron service: https://cron-job.org

## 📈 Monitoring và Logs

- Logs được output ra console với format timestamp
- Sử dụng `/api/v1/health` để monitor service status
- Check số lượng products đã được index

## 🤝 Hỗ trợ

Nếu có vấn đề:

1. Check logs để xem lỗi cụ thể
2. Verify MongoDB connection
3. Đảm bảo CLIP model được download thành công (lần đầu sẽ mất thời gian)

## 📝 Notes

- Model CLIP sẽ được download tự động lần đầu chạy (~350MB)
- Với CPU, inference có thể hơi chậm. Cân nhắc sử dụng GPU trong production
- Threshold mặc định là 0.5, có thể điều chỉnh tùy use case
