import argparse
import sys
import os
import torch
import cv2
from tqdm import tqdm

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from backend.model.rife_wrapper import RIFEWrapper
from backend.pipeline.processor import VideoReader, VideoWriter

def process_video(input_path, output_path, scale=1.0, fp16=True):
    print(f"Processing {input_path} -> {output_path}")
    
    if torch.backends.mps.is_available():
        device = 'mps'
    elif torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    print(f"Using device: {device}")

    weights_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model/weights')
    model = RIFEWrapper(weights_path, device=device)
    
    reader = VideoReader(input_path)
    info = reader.get_info()
    print(f"Input info: {info}")
    
    # 2x interpolation -> 2 * fps
    out_fps = info['fps'] * 2
    writer = VideoWriter(output_path, out_fps, info['width'], info['height'])
    
    # Sliding window approach for low memory usage
    reader = VideoReader(input_path) # Re-open or reset
    # Actually VideoReader usage in my impl is an iterator.
    # I should use the iterator directly.
    
    prev_frame = None
    
    # buffer frames to process pairs
    # Logic: 
    # Read F0. Write F0.
    # Read F1. Interpolate F0.5. Write F0.5. Write F1.
    # Set prev = F1.
    
    # Actually, RIFE standard:
    # Output: F0, F0.5, F1, F1.5, ...
    
    pbar = tqdm(total=info['total_frames'])
    
    for i, frame in enumerate(reader):
        if prev_frame is not None:
            # Interpolate
            mid = model.interpolate(prev_frame, frame, scale)
            writer.write_frame(mid)
        
        writer.write_frame(frame)
        prev_frame = frame
        pbar.update(1)
        
    pbar.close()
    writer.close()
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()
    
    process_video(args.input, args.output)
