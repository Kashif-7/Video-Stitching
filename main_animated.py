import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, VideoFileClip

# Paths
DATA_DIR = "data"
TEMP_DIR = "temp"
OUTPUT_DIR = "output"

# Create folders if not exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Define image-audio-text pairs
pairs = [
    {"image": "image1.png", "audio": "audio1.mp3", "text": "text1"},
    {"image": "image2.png", "audio": "audio2.mp3", "text": "text2"},
]

# Step 2: Function to create animated subtitles
def create_animated_subtitles(text, duration, video_size):
    """Create word-by-word animated subtitles with fade effects"""
    words = text.split()
    word_clips = []

    # Calculate timing for each word
    time_per_word = duration / len(words)

    for i, word in enumerate(words):
        start_time = i * time_per_word

        # Create text clip for each word with better sizing
        # Add a trailing newline to create bottom padding and avoid cropping descenders
        txt_clip = TextClip(
            text=f"{word}\n",
            font_size=28,  # EVEN SMALLER FONT SIZE
            color='white',
            font='C:\\Windows\\Fonts\\arialbd.ttf',
            stroke_color='black',
            stroke_width=1,  # Thinner stroke
            method='caption',
            size=(video_size[0] - 350, None)  # MUCH MORE MARGIN
        )

        # Position at bottom center with better spacing and room for padding
        txt_clip = txt_clip.with_position(('center', video_size[1] - 220))

        # Set timing for each word
        txt_clip = txt_clip.with_start(start_time).with_duration(time_per_word)

        word_clips.append(txt_clip)

    return word_clips
# Step 3: Function to apply zoom/pan animation to image



# Step 4: Function to create subvideo with animations
def create_subvideo(image_path, audio_path, text_path, output_path):
    print(f"Creating animated subvideo for {image_path} + {audio_path}")
    
    # Load audio
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Read subtitle text
    with open(text_path, 'r', encoding='utf-8') as f:
        subtitle_text = f.read().strip()
    
    # Load image and set duration = audio duration
    image_clip = ImageClip(image_path).with_duration(duration)
    
    # Resize image
    image_clip = image_clip.resized(height=720)
    video_size = image_clip.size
    
    
    # Create animated subtitles
    subtitle_clips = create_animated_subtitles(subtitle_text, duration, video_size)
    
    # Combine image with subtitles
    video = CompositeVideoClip([image_clip] + subtitle_clips)
    
    # Add audio
    video = video.with_audio(audio_clip)
    
    # Export subvideo with proper audio settings
    video.write_videofile(
        output_path, 
        fps=24, 
        codec='libx264',
        audio=True,
        audio_codec='aac',
        audio_bitrate='256k',
        audio_fps=44100,
        bitrate='5000k',
        preset='medium',
        threads=4,
        logger=None
    )
    
    # Close clips to free memory
    video.close()
    image_clip.close()
    audio_clip.close()

# Step 5: Create all subvideos
subvideos = []
for idx, pair in enumerate(pairs, start=1):
    image_path = os.path.join(DATA_DIR, pair["image"])
    audio_path = os.path.join(DATA_DIR, pair["audio"])
    text_path = os.path.join(DATA_DIR, pair["text"])
    output_path = os.path.join(TEMP_DIR, f"subvideo_{idx}.mp4")
    
    create_subvideo(image_path, audio_path, text_path, output_path)
    subvideos.append(output_path)

# Step 6: Merge all subvideos with animated transitions
print("Merging animated subvideos with crossfade transitions...")

video_clips = [VideoFileClip(subvideo) for subvideo in subvideos]

# Use concatenate_videoclips with padding for crossfade effect
final_video = concatenate_videoclips(video_clips, method="compose", padding=-0.3)# Step 7: Write the final video file
final_output_path = os.path.join(OUTPUT_DIR, "final_output.mp4")
final_video.write_videofile(
    final_output_path, 
    fps=24, 
    codec='libx264',
    audio=True,
    audio_codec='aac',
    audio_bitrate='256k',
    audio_fps=44100,
    bitrate='5000k',
    preset='medium',
    threads=4,
    logger=None
)

# Step 8: Clean up
for clip in video_clips:
    clip.close()
final_video.close()

print(f"\n✅ Animated video generation complete: {final_output_path}")
print("   Features added:")
print("   - ✨ Zoom & pan animation on images")
print("   - 📝 Word-by-word animated subtitles with fade effects")
print("   - 🎬 Animated crossfade transitions between clips")
