import os
import tempfile
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from video_processor import VideoProcessor

app = FastAPI(title="Video Stitching API", description="Create videos by stitching sentences, audio, and images")

# Initialize video processor
video_processor = VideoProcessor()

class VideoItem(BaseModel):
    sentence: str
    audioPath: str
    imagePath: str

@app.post("/create-video/")
async def create_video(request_data: List[dict]):
    """
    Create a video from JSON data containing sentences and file paths.
    
    Args:
        request_data: List of objects with structure:
        [
          {
            "json": {
              "sentence": "First sentence",
              "audioPath": "/path/to/audio_0.mp3", 
              "imagePath": "/path/to/image_0.png"
            }
          }
        ]
    
    Returns:
        The final stitched video file
    """
    
    if not request_data or len(request_data) == 0:
        raise HTTPException(status_code=400, detail="Request data cannot be empty")
    
    # Extract data from the request
    sentences = []
    audio_paths = []
    image_paths = []
    
    try:
        for item in request_data:
            if "json" not in item:
                raise HTTPException(status_code=400, detail="Each item must have a 'json' field")
            
            json_data = item["json"]
            
            # Validate required fields
            if not all(key in json_data for key in ["sentence", "audioPath", "imagePath"]):
                raise HTTPException(
                    status_code=400, 
                    detail="Each item must contain 'sentence', 'audioPath', and 'imagePath'"
                )
            
            sentence = json_data["sentence"]
            audio_path = json_data["audioPath"]
            image_path = json_data["imagePath"]
            
            # Validate files exist
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")
            
            if not os.path.exists(image_path):
                raise HTTPException(status_code=404, detail=f"Image file not found: {image_path}")
            
            # Validate file extensions
            audio_ext = os.path.splitext(audio_path)[1].lower()
            if audio_ext not in ['.mp3', '.wav', '.m4a', '.aac']:
                raise HTTPException(status_code=400, detail=f"Unsupported audio format: {audio_ext}")
            
            image_ext = os.path.splitext(image_path)[1].lower()
            if image_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                raise HTTPException(status_code=400, detail=f"Unsupported image format: {image_ext}")
            
            sentences.append(sentence)
            audio_paths.append(audio_path)
            image_paths.append(image_path)
        
        # Create video using the video processor
        output_video_path = video_processor.create_video_from_arrays(
            sentences=sentences,
            audio_files=audio_paths,
            image_files=image_paths
        )
        
        # Return the video file
        return FileResponse(
            path=output_video_path,
            media_type='video/mp4',
            filename='stitched_video.mp4'
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating video: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Video Stitching API is running", 
        "version": "1.0.0",
        "endpoints": {
            "create_video": "/create-video/ (POST) - Accepts JSON with file paths",
            "health": "/health (GET) - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
