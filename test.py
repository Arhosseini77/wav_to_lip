import cv2
import numpy as np
from modules import analyze_audio

audio_file = 'test_files/only_silent.mp3'
result = analyze_audio(audio_file)

# Video properties
frame_width = 640
frame_height = 480
fps = 10
video_file = 'lip_syncing_visualization.avi'

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(video_file, fourcc, fps, (frame_width, frame_height))

for time, amp, status in result:
    # Create a black image
    frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    # Draw a line for amplitude
    line_end_y = int((1 - amp) * frame_height)
    cv2.line(frame, (int(time * 10), frame_height), (int(time * 10), line_end_y), (255, 0, 0), 2)

    # Display the status
    text = status if status else 'None'
    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Write the frame
    out.write(frame)

# Release everything
out.release()

print(f"Video file '{video_file}' created.")