# Quick Start Guide - Deploy to Render

## 🚀 Nhanh Chóng Deploy (5 phút)

### 1. Push code lên GitHub:

```bash
cd c:\Users\Lenovo\STUDY\SEARCH_IMG
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 2. Vào Render:

- Truy cập: https://dashboard.render.com
- Click **"New +"** → **"Web Service"**
- Connect repo: **HoaiNhu/SEARCH_IMG**

### 3. Cấu hình (1 phút):

**Build & Deploy:**

```
Name: image-search-api
Region: Singapore
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free (hoặc Starter $7/tháng)
```

**Environment Variables** (click "Add Environment Variable"):

```
MONGO_URI = mongodb+srv://username:password@webbuycake.asd8v.mongodb.net/?retryWrites=true&w=majority&appName=WebBuyCake
MONGO_DB_NAME = test
MONGO_COLLECTION = products
MODEL_NAME = openai/clip-vit-base-patch32
DEVICE = cpu
TOP_K = 10
SIMILARITY_THRESHOLD = 0.5
PYTHON_VERSION = 3.11.0
```

### 4. Deploy:

- Click **"Create Web Service"**
- Đợi 10-15 phút (tải CLIP model)
- URL: `https://image-search-api.onrender.com`

### 5. Test:

```bash
curl https://image-search-api.onrender.com/health
```

### 6. Cập nhật Frontend:

File `.env` trong FE-Project_AvocadoCake:

```env
REACT_APP_IMAGE_SEARCH_API_URL=https://image-search-api.onrender.com
```

## ✅ Done!

Xem hướng dẫn chi tiết: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)
