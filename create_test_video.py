import cv2
import numpy as np

def create_bouncing_ball_video(filename, width=640, height=480, fps=10, duration=2):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    frames = int(fps * duration)
    radius = 30
    x, y = 50, height // 2
    speed = (width - 100) / frames # Move across screen
    
    print(f"Generating {frames} frames...")
    
    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw background (checkerboard to see motion clearly)
        step = 40
        for r in range(0, height, step):
            for c in range(0, width, step):
                if (r//step + c//step) % 2 == 0:
                    frame[r:r+step, c:c+step] = (30, 30, 30)
                    
        # Draw ball
        cv2.circle(frame, (int(x), int(y)), radius, (0, 0, 255), -1)
        
        # Draw text frame number
        cv2.putText(frame, f"Frame {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
        x += speed
        
    out.release()
    print(f"Video saved to {filename}")

if __name__ == "__main__":
    create_bouncing_ball_video("input_test.mp4")
