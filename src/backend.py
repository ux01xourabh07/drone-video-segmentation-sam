
import os
import cv2
import numpy as np
import torch
import gc
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

class SamController:
    def __init__(self, checkpoint_path, model_type="vit_h"):
        # Model Loading Logic with ViT-B Fallback
        weight_dir = os.path.dirname(checkpoint_path) or "weights"
        vit_b_path = os.path.join(weight_dir, "sam_vit_b_01ec64.pth")
        
        if os.path.exists(vit_b_path):
            print(f"Optimization: Switching to ViT-B: {vit_b_path}")
            self.checkpoint_path = vit_b_path
            self.model_type = "vit_b"
        else:
            print(f"Using provided checkpoint: {checkpoint_path}")
            self.checkpoint_path = checkpoint_path
            if "vit_h" in os.path.basename(checkpoint_path): self.model_type = "vit_h"
            elif "vit_l" in os.path.basename(checkpoint_path): self.model_type = "vit_l"
            elif "vit_b" in os.path.basename(checkpoint_path): self.model_type = "vit_b"
            else: self.model_type = model_type

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading SAM ({self.model_type}) on {self.device}...")
        
        gc.collect()
        self.sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
        self.sam.to(device=self.device)
        
        points = 32 if self.device == "cuda" else 16 
        self.mask_generator = SamAutomaticMaskGenerator(
            model=self.sam,
            points_per_side=points,
            pred_iou_thresh=0.82,
            stability_score_thresh=0.88,
            crop_n_layers=0,
            crop_n_points_downscale_factor=2, 
            min_mask_region_area=200, 
        )

    # Note: process_image (single image) removed as per Video-Only requirement.
    # Logic is now handled frame-by-frame in VideoProcessorThread.

    def classify_mask_geometry(self, mask_bool, area):
        """
        Geometric Classification Logic.
        """
        mask_uint8 = (mask_bool * 255).astype(np.uint8)
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return None
        cnt = max(contours, key=cv2.contourArea)
        
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0: return None
        solidity = area / float(hull_area)
        
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        if aspect_ratio < 1.0: aspect_ratio = 1.0 / aspect_ratio
        
        rect_area = w * h
        extent = area / float(rect_area)
        
        # BUILDING RULES
        if solidity > 0.85 and extent > 0.6 and aspect_ratio < 4.0:
            return "Building"
            
        # ROAD RULES (Ignored in aggregation for this version, but logic remains)
        if solidity < 0.7 or aspect_ratio > 3.5:
             return "Road"
        
        return None
