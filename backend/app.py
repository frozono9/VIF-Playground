import os
import shutil
import uuid
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current directory to path so imports work
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.processor import VideoReader, VideoWriter
from model.rife_wrapper import RIFEWrapper
import torch
import cv2
from tqdm import tqdm

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "backend/uploads"
OUTPUT_DIR = "backend/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory "Database" for task tracking
tasks: Dict[str, Dict] = {}

class ProcessRequest(BaseModel):
    filename: str
    multiplier: int = 2
    visualization: str = "none" # none, flow

def process_video_task(task_id: str, input_path: str, output_path: str, multiplier: int, visualization: str):
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 0
        
        # Determine device
        if torch.backends.mps.is_available():
            device = 'mps'
        elif torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
            
        print(f"Task {task_id}: Processing {input_path} -> {output_path} on {device}. Mult: {multiplier}x. Viz: {visualization}")
        
        # Load Model
        weights_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model/weights')
        model = RIFEWrapper(weights_path, device=device)
        
        # Video Reader
        reader = VideoReader(input_path)
        info = reader.get_info()
        
        # Video Writer
        out_fps = info['fps'] * 2 # If 2x. If 4x -> *4.
        if multiplier == 4:
            out_fps = info['fps'] * 4
            
        # If flow visualization, we might want to output standard FPS but showing flow?
        # Or showing flow at interpolated rate? Let's do interpolated rate.
        
        writer = VideoWriter(output_path, out_fps, info['width'], info['height'])
        
        # Processing Loop (Sliding Window)
        prev_frame = None
        total_frames = info['total_frames']
        processed = 0
        
        reader = VideoReader(input_path) # Reset/Start iterator
        
        # Import visualization if needed
        if visualization == 'flow':
            from pipeline.visualization import flow_to_image
        
        for frame in reader:
            if prev_frame is not None:
                # Interpolate
                # Returns: interpolated frame, [optional flow]
                
                if visualization == 'flow':
                    # If visualizing flow, we likely want to see the flow between prev and frame.
                    # RIFE naturally computes flow Pre->Next.
                    # We can visualize that.
                    
                    # For simple 2x flow viz:
                    # Output: Prev (as flow?), Mid (as flow?), Next (as flow?)
                    # Usually flow is a map.
                    # Let's output: Flow(Prev->Next) as a frame.
                    
                    mid, flow = model.interpolate(prev_frame, frame, scale=1.0, return_flow=True)
                    flow_img = flow_to_image(flow)
                    
                    # Resize flow to match video size if needed (usually it matches)
                    if flow_img.shape != frame.shape:
                        flow_img = cv2.resize(flow_img, (frame.shape[1], frame.shape[0]))
                    
                    # Write flow map instead of video frames? 
                    # User likely wants to see the motion.
                    # Let's write the flow map for the intermediate frame location.
                    # To keep FPS consistent, maybe write Flow for Prev, Flow for Mid?
                    # Flow is defined between two frames. 
                    # Let's write Flow(Prev->Next) twice to fill time? 
                    # Or just write it once? 
                    # If we write it once, we halve the FPS effectively if we don't duplicate.
                    # Let's just output the flow map as the "interpolated" content.
                    # Frame 1: Flow map. Frame 1.5: Flow map? 
                    
                    # Better: Overlay or Side-by-Syde? 
                    # Plan said: "Generate a video of flow maps."
                    # So, for every pair (A, B), we generate Flow(A->B).
                    # We can write this flow map 2 times to match 2x FPS, or just output at 1x FPS?
                    # Let's output at 2x FPS to match the "Interpolation" setting, 
                    # maybe by blending or just holding the flow.
                    
                    writer.write_frame(flow_img) 
                    writer.write_frame(flow_img) # Repeat to fill 2x slots
                    
                else:
                    # Normal Interpolation
                    mid = model.interpolate(prev_frame, frame, scale=1.0)
                    
                    if multiplier == 2:
                        writer.write_frame(prev_frame)
                        writer.write_frame(mid)
                    elif multiplier == 4:
                        # 4x Recursive
                        # A -> Mid -> B
                        # A -> Q1 -> Mid -> Q3 -> B
                        
                        # We have Mid.
                        # Need Q1 = Interp(A, Mid)
                        # Need Q3 = Interp(Mid, B)
                        
                        q1 = model.interpolate(prev_frame, mid, scale=1.0)
                        q3 = model.interpolate(mid, frame, scale=1.0)
                        
                        writer.write_frame(prev_frame)
                        writer.write_frame(q1)
                        writer.write_frame(mid)
                        writer.write_frame(q3)

            elif prev_frame is None and visualization != 'flow':
                 # First frame logic is tricky in loop. 
                 # In standard loop above, we write (Prev, Mid).
                 # The last frame B becomes Prev for next.
                 # So we write A, Mid. Next loop writes B, Mid2. 
                 # This works.
                 pass
            
            prev_frame = frame
            
            processed += 1
            progress = int((processed / total_frames) * 100)
            tasks[task_id]["progress"] = progress
            
        # Write last frame if not flow (flow has no "last frame" single)
        if visualization != 'flow':
            writer.write_frame(prev_frame)
            
        writer.close()
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        print(f"Task {task_id}: Completed")
        
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        import traceback
        traceback.print_exc()
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Analyze video
    try:
        reader = VideoReader(file_path)
        info = reader.get_info()
        reader.close()
        
        return {
            "filename": filename,
            "original_filename": file.filename,
            "fps": info['fps'],
            "duration": info['total_frames'] / info['fps'] if info['fps'] > 0 else 0,
            "width": info['width'],
            "height": info['height'],
            "total_frames": info['total_frames']
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(status_code=400, content={"error": f"Invalid video file: {str(e)}"})

@app.post("/process")
async def start_processing(request: ProcessRequest, background_tasks: BackgroundTasks):
    input_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(input_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
        
    task_id = str(uuid.uuid4())
    output_filename = f"processed_{task_id}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "output_filename": output_filename
    }
    
    background_tasks.add_task(
        process_video_task, 
        task_id, 
        input_path, 
        output_path, 
        request.multiplier,
        request.visualization
    )
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    task = tasks[task_id]
    response = {
        "status": task["status"],
        "progress": task["progress"]
    }
    
    if task["status"] == "completed":
        response["result_url"] = f"/download/{task['output_filename']}"
    elif task["status"] == "failed":
        response["error"] = task.get("error")
        
    return response

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
        
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
