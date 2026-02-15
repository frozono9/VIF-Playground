# VFI Backend

This directory contains the core ML pipeline for Video Frame Interpolation using RIFE.

## Setup

1. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Ensure you have the pretrained weights in `backend/model/weights/flownet.pkl`.

## Usage

To double the frame rate of a video (2x interpolation):

```bash
python3 backend/process_video.py --input path/to/input.mp4 --output path/to/output_2x.mp4
```

The script automatically detects MPS (Metal Performance Shaders) on macOS for acceleration.

## Testing

Run the inference test script to verify model loading and basic functionality:

```bash
python3 backend/test_inference.py
```
