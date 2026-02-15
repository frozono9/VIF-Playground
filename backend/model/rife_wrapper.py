import torch
from torch.nn import functional as F
import os
import sys

# Add current directory to path so imports work if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .RIFE_HDv3 import Model

class RIFEWrapper:
    def __init__(self, model_path: str, device: str = 'cuda'):
        self.device = torch.device(device)
        self.model = Model()
        self.model.device()
        self.load_weights(model_path)
        self.model.eval()

    def load_weights(self, path: str):
        if os.path.isfile(path):
            path = os.path.dirname(path)
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model weights path not found at {path}")
        
        try:
            self.model.load_model(path, -1) 
        except Exception as e:
            print(f"Standard load failed: {e}. Trying manual load.")
            # If standard load fails, try manual load of state dict
            self.model.flownet.load_state_dict(torch.load(os.path.join(path, 'flownet.pkl'), map_location=self.device))

    def interpolate(self, I0, I1, scale=1.0, return_flow=False):
        # I0, I1: numpy arrays (H, W, 3) or tensors
        # Return: numpy array (H, W, 3) or tuple if return_flow
        
        # Preprocessing similar to inference_video.py
        h, w, _ = I0.shape
        
        img0 = (torch.tensor(I0.transpose(2, 0, 1)).to(self.device) / 255.).unsqueeze(0).float()
        img1 = (torch.tensor(I1.transpose(2, 0, 1)).to(self.device) / 255.).unsqueeze(0).float()
        
        # Padding
        ph = ((h - 1) // 32 + 1) * 32
        pw = ((w - 1) // 32 + 1) * 32
        padding = (0, pw - w, 0, ph - h)
        
        img0 = F.pad(img0, padding)
        img1 = F.pad(img1, padding)
        
        with torch.no_grad():
            if return_flow:
                mid, flow = self.model.inference_with_flow(img0, img1, scale)
            else:
                mid = self.model.inference(img0, img1, scale)
            
        # Postprocessing
        res = mid[0].cpu().numpy().transpose(1, 2, 0)
        res = (res[:h, :w] * 255).astype('uint8')
        
        if return_flow:
            # Postprocess flow
            flow = flow[0].permute(1, 2, 0).cpu().numpy()
            flow = flow[:h, :w, :]
            return res, flow
            
        return res

class DisplayPath:
    # Helper to trick their load_model if it expects an object with string
    def __init__(self, path):
        # ensure path is directory if their code expects directory
        if os.path.isfile(path):
            self.modelDir = os.path.dirname(path)
        else:
            self.modelDir = path
