# NSFW Image Generator

A lightweight web application for generating images from text prompts using AI. Built with FastAPI (backend) and vanilla JavaScript (frontend), optimized for CPU-only systems.

## Features

✨ **Text-to-Image Generation**
- Generate single or batch images from text prompts
- Customizable inference steps and guidance scale
- Negative prompts support

🎨 **User-Friendly Interface**
- Clean, modern dark theme UI
- Real-time image preview gallery
- Generation history with deletion
- Single and batch generation modes

⚡ **Performance Optimized**
- CPU-only compatible
- Lightweight frontend (vanilla JS, no heavy frameworks)
- Efficient image caching
- Asynchronous processing

📁 **History & Storage**
- Automatic generation history tracking
- Local image storage
- History management (view/delete)

## Requirements

- Python 3.8+
- Node.js 16+ (for frontend development)
- 8GB+ RAM (for CPU inference)
- ~20GB free disk space (for model weights)

## Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/nsfw-image-generator.git
cd nsfw-image-generator

# Build and run
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the server
python app.py
```

#### Frontend Setup

```bash
cd frontend

# For development, open index.html in a browser
# Or use a simple HTTP server:
python -m http.server 3000

# For production build:
npm install
npm run build
```

## Configuration

Edit `backend/.env` to customize:

```env
# Model Configuration
MODEL_ID="SexGod1979/PinkCherry_NSFW_LTX23"
DEVICE="cpu"                    # or "cuda" for NVIDIA GPU
OUTPUT_DIR="./generated_images"
MAX_BATCH_SIZE=4                # Maximum images to generate at once
DEFAULT_STEPS=30                # Default inference steps
DEFAULT_GUIDANCE_SCALE=7.5      # Default guidance scale

# Server Configuration
PORT=8000
HOST="0.0.0.0"
```

## API Endpoints

### Generate Single Image
```bash
POST /generate
Content-Type: application/json

{
  "prompt": "a beautiful landscape",
  "negative_prompt": "",
  "num_images": 1,
  "num_inference_steps": 30,
  "guidance_scale": 7.5,
  "seed": null
}
```

### Batch Generate
```bash
POST /batch-generate
Content-Type: application/json

{
  "prompts": ["prompt 1", "prompt 2", "prompt 3"],
  "negative_prompt": "",
  "num_inference_steps": 30,
  "guidance_scale": 7.5
}
```

### Get History
```bash
GET /history
```

### Get Image
```bash
GET /image/{image_name}
```

### Delete from History
```bash
DELETE /history/{generation_id}
```

### Get Status
```bash
GET /status
```

## Performance Tips

**For CPU-only systems:**

1. **Reduce inference steps**: Use 20-30 steps instead of 50+ for faster generation
2. **Batch processing**: Generate multiple images in one session
3. **Keep prompts reasonable**: Shorter, simpler prompts generate faster
4. **Monitor RAM**: Ensure at least 8GB available RAM
5. **Disable background processes**: Close unnecessary applications

**Estimated generation time (CPU):**
- 512x512 image: 3-5 minutes (30 steps)
- Batch of 4: 12-20 minutes

## Project Structure

```
nsfw-image-generator/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Configuration template
├── frontend/
│   ├── index.html             # Frontend UI
│   ├── package.json           # Node dependencies (optional)
│   └── vite.config.js         # Vite configuration (optional)
├── docker-compose.yml         # Docker orchestration
├── Dockerfile.backend         # Backend container
├── Dockerfile.frontend        # Frontend container
└── README.md                  # This file
```

## Troubleshooting

### Model Download Issues
```bash
# Pre-download the model
python -c "from diffusers import AutoPipelineForText2Image; AutoPipelineForText2Image.from_pretrained('SexGod1979/PinkCherry_NSFW_LTX23')"
```

### Memory Issues
- Reduce `num_inference_steps` to 10-20
- Use `MAX_BATCH_SIZE=1` in .env
- Ensure no other heavy applications are running

### CORS Issues
- Frontend and backend must be on same network
- Update `API_URL` in frontend if backend is on different host

### Model Not Found
- Ensure internet connection (model downloads from Hugging Face)
- Check Hugging Face API status
- Try downloading manually with HF_TOKEN

## Security Considerations

⚠️ **This application generates NSFW content. Use responsibly:**

- Deploy only on secure, private networks
- Restrict access with firewall rules
- Implement authentication for production use
- Store generated images securely
- Follow your jurisdiction's laws regarding AI-generated content

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions:
- Check [Troubleshooting](#troubleshooting) section
- Open a GitHub issue
- Review API documentation at `/docs` when backend is running

## Acknowledgments

- Model: [SexGod1979/PinkCherry_NSFW_LTX23](https://huggingface.co/SexGod1979/PinkCherry_NSFW_LTX23)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend uses vanilla JavaScript
