import numpy as np
import cv2

def make_colorwheel():
    """
    Generates a color wheel for optical flow visualization as presented in:
    Baker et al. "A Database and Evaluation Methodology for Optical Flow" (ICCV, 2007)
    URL: http://vision.middlebury.edu/flow/flowEval-iccv07.pdf
    """
    RY = 15
    YG = 6
    GC = 4
    CB = 11
    BM = 13
    MR = 6

    ncols = RY + YG + GC + CB + BM + MR
    colorwheel = np.zeros((ncols, 3))
    col = 0

    # RY
    colorwheel[0:RY, 0] = 255
    colorwheel[0:RY, 1] = np.floor(255*np.arange(0,RY)/RY)
    col = col+RY
    # YG
    colorwheel[col:col+YG, 0] = 255 - np.floor(255*np.arange(0,YG)/YG)
    colorwheel[col:col+YG, 1] = 255
    col = col+YG
    # GC
    colorwheel[col:col+GC, 1] = 255
    colorwheel[col:col+GC, 2] = np.floor(255*np.arange(0,GC)/GC)
    col = col+GC
    # CB
    colorwheel[col:col+CB, 1] = 255 - np.floor(255*np.arange(0,CB)/CB)
    colorwheel[col:col+CB, 2] = 255
    col = col+CB
    # BM
    colorwheel[col:col+BM, 2] = 255
    colorwheel[col:col+BM, 0] = np.floor(255*np.arange(0,BM)/BM)
    col = col+BM
    # MR
    colorwheel[col:col+MR, 2] = 255 - np.floor(255*np.arange(0,MR)/MR)
    colorwheel[col:col+MR, 0] = 255
    return colorwheel

def flow_compute_color(u, v, convert_to_bgr=False):
    """
    Applies the flow color wheel to (u, v) components.
    """
    flow_image = np.zeros((u.shape[0], u.shape[1], 3), np.uint8)
    colorwheel = make_colorwheel()  # shape [55x3]
    ncols = colorwheel.shape[0]
    rad = np.sqrt(u**2 + v**2)
    a = np.arctan2(-v, -u)/np.pi
    fk = (a+1) / 2 * (ncols-1)
    k0 = np.floor(fk).astype(int)
    k1 = k0 + 1
    k1[k1 == ncols] = 0
    f = fk - k0
    
    for i in range(colorwheel.shape[1]):
        tmp = colorwheel[:,i]
        col0 = tmp[k0] / 255.0
        col1 = tmp[k1] / 255.0
        col = (1-f)*col0 + f*col1
        idx = (rad <= 1)
        col[idx]  = 1 - rad[idx] * (1-col[idx])
        col[~idx] = col[~idx] * 0.75
        
        # Scale to 255 and cast
        flow_image[:, :, i] = np.floor(255 * col)
    return flow_image

def flow_to_image(flow):
    """
    Expects a 2D flow image of shape [H, W, 2]
    """
    if flow is None:
        return None
    u = flow[:, :, 0]
    v = flow[:, :, 1]
    
    # Normalize flow for better visualization if needed, or just standard
    # Usually we don't normalize by max in standard Baker plot, but it can be dark.
    # Let's keep standard.
    
    img = flow_compute_color(u, v)
    return img
