# Setup Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.8 or higher
- Git
- 8GB+ RAM
- ~20GB free disk space

### Step 1: Clone Repository
```bash
git clone https://github.com/ankitmanohar25/nsfw-image-generator.git
cd nsfw-image-generator
```

### Step 2: Set Up Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Create Configuration
```bash
cp .env.example .env
# Edit .env if needed (default settings work for CPU)
```

### Step 4: Run Backend
```bash
python app.py
```
Backend will start at: `http://localhost:8000`

### Step 5: Open Frontend
In another terminal:
```bash
cd frontend
python -m http.server 3000
```
Access at: `http://localhost:3000`

## First Time Setup Tips

### Model Download
- First run will download ~5GB model from Hugging Face
- Requires internet connection
- This happens only once

### Testing the Setup
1. Open `http://localhost:3000` in browser
2. Enter a simple prompt: "a cat"
3. Click "Generate Image"
4. Wait 3-5 minutes for first image (CPU)
5. Image appears in gallery

## Advanced Setup

### Using Docker
```bash
# Build and run everything
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### GPU Setup (NVIDIA)
1. Install CUDA Toolkit
2. Edit `backend/.env`:
   ```
   DEVICE="cuda"
   ```
3. Install GPU dependencies:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Production Deployment

#### Using Gunicorn + Nginx
```bash
# Install gunicorn
pip install gunicorn

# Run backend
cd backend
gunicorn -w 1 -b 0.0.0.0:8000 app:app
```

#### Configure Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

## Troubleshooting Installation

### Issue: "Module not found" error
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: "CUDA not found" (if using GPU)
```bash
# Install CUDA drivers from NVIDIA website
# Then reinstall torch with GPU support
pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "Permission denied" (Linux/macOS)
```bash
chmod +x backend/app.py
```

### Issue: Port 8000/3000 already in use
```bash
# Change in backend/.env
PORT=8001

# Change API_URL in frontend/index.html
const API_URL = 'http://localhost:8001';
```

### Issue: "Out of memory" error
```bash
# Edit backend/.env
MAX_BATCH_SIZE=1      # Reduce batch size
DEFAULT_STEPS=20      # Reduce inference steps
```

## Verification

### Check Backend is Running
```bash
curl http://localhost:8000/status
```

Expected response:
```json
{
  "status": "running",
  "device": "cpu",
  "model": "SexGod1979/PinkCherry_NSFW_LTX23",
  "max_batch_size": 4
}
```

### Check API Documentation
Open: `http://localhost:8000/docs`

## Next Steps

1. ✅ Generate your first image
2. 📖 Read [README.md](README.md) for full features
3. ⚙️ Customize settings in `.env`
4. 🚀 Deploy for production use

## Getting Help

- Check [README.md](README.md) troubleshooting section
- Review API docs at `/docs`
- Open GitHub issue for bugs
