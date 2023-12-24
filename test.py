import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from collections import Counter
from modules import analyze_audio

audio_file = 'test_files/voice_10-12-2023_08-01-37.wav'
result = analyze_audio(audio_file)

fps = 150
frame_duration = 1 / fps  # Duration of each frame in seconds
frame_width = 640
frame_height = 480
video_file = 'lip_syncing_visualization.avi'

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(video_file, fourcc, fps, (frame_width, frame_height))

# Aggregate data
aggregated_result = []
current_frame_start = 0
while current_frame_start < result[-1][0]:
    # Filter data points within the current frame
    frame_data = [r for r in result if current_frame_start <= r[0] < current_frame_start + frame_duration]
    if frame_data:
        # Average amplitude
        avg_amp = np.mean([fd[1] for fd in frame_data])
        # Most common status
        most_common_status = Counter([fd[2] for fd in frame_data]).most_common(1)[0][0]
        aggregated_result.append((current_frame_start, avg_amp, most_common_status))
    current_frame_start += frame_duration

for time, amp, status in aggregated_result:
    # Create a black image
    frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    # Calculate line positions based on amplitude
    center_y = frame_height // 2
    line_offset = int(amp * 100)  # Adjust the multiplier for more dramatic effect if needed

    # Draw the lines
    cv2.line(frame, (0, center_y - line_offset), (frame_width, center_y - line_offset), (255, 0, 0), 2)
    cv2.line(frame, (0, center_y + line_offset), (frame_width, center_y + line_offset), (255, 0, 0), 2)

    # Display the status
    text = status if status else 'None'
    cv2.putText(frame, text, (50, center_y - line_offset - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Write the frame
    out.write(frame)

# Release everything
out.release()

# Add audio to the video
video_clip = VideoFileClip(video_file)
audio_clip = AudioFileClip(audio_file)
video_clip_with_audio = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
final_video_file = 'lip_syncing_visualization_with_audio.mp4'
video_clip_with_audio.write_videofile(final_video_file, codec="libx264")

print(f"Video file with audio '{final_video_file}' created.")
