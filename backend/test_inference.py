import sys
import os
import cv2
import numpy as np
import torch

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from backend.model.rife_wrapper import RIFEWrapper

def test_inference():
    print("Testing RIFE Inference...")
    if torch.backends.mps.is_available():
        device = 'mps'
    elif torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    print(f"Using device: {device}")
    
    # Path to weights
    weights_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model/weights/flownet.pkl')
    
    try:
        model = RIFEWrapper(weights_path, device=device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return

    # Create dummy frames (small resolution for speed)
    h, w = 256, 448
    frame1 = np.zeros((h, w, 3), dtype=np.uint8)
    frame2 = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Simple movement: draw a white square moving
    cv2.rectangle(frame1, (50, 50), (100, 100), (255, 255, 255), -1)
    cv2.rectangle(frame2, (100, 100), (150, 150), (255, 255, 255), -1)
    
    try:
        result = model.interpolate(frame1, frame2, scale=1.0)
        print(f"Interpolation successful. Output shape: {result.shape}")
        
        # Save output
        cv2.imwrite('test_output.png', result)
        print("Saved test_output.png")
    except Exception as e:
        print(f"Inference failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference()
