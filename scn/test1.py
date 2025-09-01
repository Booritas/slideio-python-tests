"""slideio SCN driver testing."""
import numpy as np
import slideio
import sys, os
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity

image_path =Tools().getImageFilePath("scn", "private/HER2-63x_1.scn",ImageDir.FULL)
print(image_path)
slide = slideio.open_slide(image_path, "SCN")
print(slide)
for i in range(slide.num_scenes):
    scene = slide.get_scene(i)
    print(f"        Scene {i}:      ")
    print(scene)
    if scene.num_z_slices > 1:
        rect = scene.rect
        slice = scene.num_z_slices // 2
        block_rect = (rect[2] // 2, rect[3] // 2, rect[2] // 4, rect[3] // 4)
        channels = [0, 1, 2] if scene.num_channels > 2 else [0]
        scene_raster = scene.read_block(block_rect, (512, 0), channel_indices=channels, slices=(slice, slice + 1))
        image = Image.fromarray(scene_raster)
        image.save(f"scene_{i}.png")
