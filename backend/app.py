import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image
import json
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

# Configuration
MODEL_ID = os.getenv("MODEL_ID", "SexGod1979/PinkCherry_NSFW_LTX23")
DEVICE = os.getenv("DEVICE", "cpu")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./generated_images"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "4"))
DEFAULT_STEPS = int(os.getenv("DEFAULT_STEPS", "30"))
DEFAULT_GUIDANCE_SCALE = float(os.getenv("DEFAULT_GUIDANCE_SCALE", "7.5"))

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NSFW Image Generator",
    description="Generate images from text prompts using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline (loaded once)
pipeline = None
generation_queue = asyncio.Queue()

# Pydantic models
class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    num_images: int = 1
    num_inference_steps: int = DEFAULT_STEPS
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE
    seed: Optional[int] = None

class BatchGenerationRequest(BaseModel):
    prompts: List[str]
    negative_prompt: Optional[str] = ""
    num_inference_steps: int = DEFAULT_STEPS
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE

class HistoryItem(BaseModel):
    id: str
    timestamp: str
    prompt: str
    negative_prompt: str
    num_images: int
    images: List[str]
    parameters: dict

def load_pipeline():
    """Load the diffusion pipeline"""
    global pipeline
    if pipeline is None:
        logger.info(f"Loading model: {MODEL_ID}")
        try:
            pipeline = AutoPipelineForText2Image.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float32 if DEVICE == "cpu" else torch.float16,
                safety_checker=None,
                requires_safety_checker=False,
            )
            pipeline.to(DEVICE)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    return pipeline

def load_history() -> List[dict]:
    """Load generation history from file"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history: List[dict]):
    """Save generation history to file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_to_history(item: dict):
    """Add item to history"""
    history = load_history()
    history.append(item)
    # Keep only last 100 items
    if len(history) > 100:
        history = history[-100:]
    save_history(history)

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    try:
        load_pipeline()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "NSFW Image Generator API", "docs": "/docs"}

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    """
    Generate images from a text prompt
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if request.num_images < 1 or request.num_images > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"num_images must be between 1 and {MAX_BATCH_SIZE}"
            )
        
        pipeline = load_pipeline()
        
        logger.info(f"Generating {request.num_images} image(s) for prompt: {request.prompt}")
        
        # Generate images
        with torch.no_grad():
            if request.seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(request.seed)
            else:
                generator = None
            
            result = pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_images_per_prompt=request.num_images,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                generator=generator,
            )
        
        images = result.images
        image_paths = []
        generation_id = str(uuid.uuid4())
        
        # Save generated images
        for idx, image in enumerate(images):
            image_name = f"{generation_id}_{idx}.png"
            image_path = OUTPUT_DIR / image_name
            image.save(image_path)
            image_paths.append(image_name)
            logger.info(f"Saved image: {image_name}")
        
        # Add to history
        history_item = {
            "id": generation_id,
            "timestamp": datetime.now().isoformat(),
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "num_images": request.num_images,
            "images": image_paths,
            "parameters": {
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "seed": request.seed
            }
        }
        add_to_history(history_item)
        
        return {
            "success": True,
            "generation_id": generation_id,
            "images": image_paths,
            "prompt": request.prompt,
            "timestamp": history_item["timestamp"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/batch-generate")
async def batch_generate(request: BatchGenerationRequest):
    """
    Generate images for multiple prompts
    """
    try:
        if len(request.prompts) < 1 or len(request.prompts) > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Number of prompts must be between 1 and {MAX_BATCH_SIZE}"
            )
        
        pipeline = load_pipeline()
        results = []
        
        for prompt in request.prompts:
            if not prompt.strip():
                continue
            
            logger.info(f"Batch generating for prompt: {prompt}")
            
            with torch.no_grad():
                result = pipeline(
                    prompt=prompt,
                    negative_prompt=request.negative_prompt,
                    num_images_per_prompt=1,
                    num_inference_steps=request.num_inference_steps,
                    guidance_scale=request.guidance_scale,
                )
            
            image = result.images[0]
            generation_id = str(uuid.uuid4())
            image_name = f"{generation_id}_0.png"
            image_path = OUTPUT_DIR / image_name
            image.save(image_path)
            
            history_item = {
                "id": generation_id,
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "negative_prompt": request.negative_prompt,
                "num_images": 1,
                "images": [image_name],
                "parameters": {
                    "num_inference_steps": request.num_inference_steps,
                    "guidance_scale": request.guidance_scale,
                }
            }
            add_to_history(history_item)
            results.append(history_item)
        
        return {
            "success": True,
            "total_generated": len(results),
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@app.get("/history")
async def get_history():
    """
    Get generation history
    """
    try:
        history = load_history()
        return {
            "success": True,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Error loading history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load history")

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    """
    Get generated image
    """
    try:
        image_path = OUTPUT_DIR / image_name
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        return FileResponse(image_path, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve image")

@app.delete("/history/{generation_id}")
async def delete_from_history(generation_id: str):
    """
    Delete generation from history and remove images
    """
    try:
        history = load_history()
        new_history = [item for item in history if item["id"] != generation_id]
        
        # Remove image files
        for item in history:
            if item["id"] == generation_id:
                for image_name in item["images"]:
                    image_path = OUTPUT_DIR / image_name
                    if image_path.exists():
                        image_path.unlink()
        
        save_history(new_history)
        return {"success": True, "message": "Generation deleted"}
    except Exception as e:
        logger.error(f"Error deleting generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete generation")

@app.get("/status")
async def get_status():
    """
    Get application status and configuration
    """
    return {
        "status": "running",
        "device": DEVICE,
        "model": MODEL_ID,
        "max_batch_size": MAX_BATCH_SIZE,
        "default_steps": DEFAULT_STEPS,
        "default_guidance_scale": DEFAULT_GUIDANCE_SCALE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
