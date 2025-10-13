import os
import tempfile
from typing import List
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, VideoFileClip


class VideoProcessor:
    """Handles video creation and processing functionality"""
    
    def __init__(self, temp_dir: str = "temp", output_dir: str = "output"):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    
    def create_animated_subtitles(self, text: str, duration: float, video_size: tuple):
        """Create complete sentence subtitles that appear for the entire duration"""
        
        # Create text clip for the complete sentence
        txt_clip = TextClip(
            text=text,
            font_size=32,  # Slightly larger font for better readability
            color='white',
            font='C:\\Windows\\Fonts\\arialbd.ttf',
            stroke_color='black',
            stroke_width=2,  # Slightly thicker stroke for better visibility
            method='caption',
            size=(video_size[0] - 200, None)  # Leave margin on both sides
        )

        # Position at bottom center
        txt_clip = txt_clip.with_position(('center', video_size[1] - 150))

        # Set timing for the complete duration
        txt_clip = txt_clip.with_start(0).with_duration(duration)
        
        # Add fade in and fade out effects using crossfadein/crossfadeout
        txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)

        return [txt_clip]  # Return as list for compatibility

    def create_subvideo(self, image_path: str, audio_path: str, text: str, output_path: str):
        """Create a subvideo from image, audio, and text"""
        print(f"Creating animated subvideo for {image_path} + {audio_path}")
        
        # Load audio
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # Load image and set duration = audio duration
        image_clip = ImageClip(image_path).with_duration(duration)
        
        # Resize image
        image_clip = image_clip.resized(height=720)
        video_size = image_clip.size
        
        # Create animated subtitles
        subtitle_clips = self.create_animated_subtitles(text, duration, video_size)
        
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
        
        return output_path

    def create_video_from_arrays(self, sentences: List[str], audio_files: List[str], image_files: List[str]) -> str:
        """Create a video from arrays of sentences, audio files, and image files"""
        
        # Validate input arrays have same length
        if not (len(sentences) == len(audio_files) == len(image_files)):
            raise ValueError("All input arrays must have the same length")
        
        if len(sentences) == 0:
            raise ValueError("Input arrays cannot be empty")
        
        # Create subvideos
        subvideos = []
        for idx, (sentence, audio_file, image_file) in enumerate(zip(sentences, audio_files, image_files)):
            subvideo_path = os.path.join(self.temp_dir, f"subvideo_{idx + 1}.mp4")
            self.create_subvideo(image_file, audio_file, sentence, subvideo_path)
            subvideos.append(subvideo_path)
        
        # Merge all subvideos with animated transitions
        print("Merging animated subvideos with crossfade transitions...")
        
        video_clips = [VideoFileClip(subvideo) for subvideo in subvideos]
        
        # Use concatenate_videoclips with padding for crossfade effect
        final_video = concatenate_videoclips(video_clips, method="compose", padding=-0.3)
        
        # Write the final video file
        final_output_path = os.path.join(self.output_dir, "final_output.mp4")
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
        
        # Clean up
        for clip in video_clips:
            clip.close()
        final_video.close()
        
        # Clean up temporary subvideos
        for subvideo in subvideos:
            try:
                os.remove(subvideo)
            except OSError:
                pass
        
        print(f"\n✅ Animated video generation complete: {final_output_path}")
        return final_output_path