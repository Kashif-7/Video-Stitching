# Video Stitching API

A FastAPI server that creates videos by stitching together text, audio, and images. Each index from the input arrays is combined to create subvideos, which are then merged into a final video.

## Features

- **Array-based processing**: Takes three arrays (sentences, audio files, images) and processes them index by index
- **Animated subtitles**: Word-by-word animated text overlays
- **Crossfade transitions**: Smooth transitions between subvideos
- **Base64 file handling**: Accept files as base64 encoded strings
- **Web interface**: Simple HTML interface for testing

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the required folders:
```
audio-image-ext-video-stitching/
├── server.py
├── test_api.py
├── test_interface.html
├── requirements.txt
├── data/           # Sample data (optional)
├── temp/           # Temporary files (created automatically)
└── output/         # Final videos (created automatically)
```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### POST `/create-video`

Creates a video from three arrays of equal length:

**Request Body:**
```json
{
  "sentences": ["First sentence", "Second sentence"],
  "audio_files_base64": ["base64_audio_1", "base64_audio_2"],
  "image_files_base64": ["base64_image_1", "base64_image_2"]
}
```

**Response:**
```json
{
  "message": "Video created successfully",
  "video_url": "/download-video/{video_id}",
  "video_id": "unique-video-id"
}
```

#### GET `/download-video/{video_id}`

Downloads the generated video file.

#### GET `/`

Serves a web interface for testing the API.

#### GET `/health`

Health check endpoint.

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Set the number of items you want to process
3. Fill in the sentences, upload audio files, and upload image files
4. Click "Create Video" to generate your video
5. Download the result when processing is complete

### Python Test Script

Run the test script (requires sample files in the `data/` folder):

```bash
python test_api.py
```

## API Behavior

- **Index Matching**: `sentences[0]` + `audio_files[0]` + `images[0]` = `subvideo_1`
- **Array Validation**: All three arrays must have the same length
- **File Processing**: Audio and image files are accepted as base64 encoded strings
- **Video Output**: Subvideos are concatenated with crossfade transitions
- **Cleanup**: Temporary files are automatically cleaned up after processing

## File Format Support

- **Audio**: MP3, WAV, and other formats supported by MoviePy
- **Images**: PNG, JPG, and other formats supported by MoviePy
- **Output**: MP4 video with H.264 codec and AAC audio

## Example with Sample Data

If you have sample files in the `data/` folder:
- `data/audio1.mp3`, `data/audio2.mp3`
- `data/image1.png`, `data/image2.png`

You can test with:

```python
import requests
import base64

def encode_file(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

data = {
    "sentences": ["Hello world!", "This is a test video"],
    "audio_files_base64": [
        encode_file("data/audio1.mp3"),
        encode_file("data/audio2.mp3")
    ],
    "image_files_base64": [
        encode_file("data/image1.png"),
        encode_file("data/image2.png")
    ]
}

response = requests.post("http://localhost:8000/create-video", json=data)
print(response.json())
```

## Error Handling

The API includes comprehensive error handling for:
- Mismatched array lengths
- Invalid base64 data
- Missing files
- Video processing errors
- Automatic cleanup on failures

## Performance Notes

- Video processing can take several minutes depending on file sizes
- Large images are automatically resized to 720p height
- Audio duration determines the length of each subvideo
- Memory is managed with proper cleanup of video clips