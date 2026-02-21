import slideio
import os
import sys
import time
from PIL import Image
import numpy as np
import json
import tempfile
import uuid

from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common.test_tools import Tools, ImageDir

                
def check_file(input_path, driver):
    with slideio.open_slide(input_path, driver) as slide:
        with slide.get_scene(0) as scene:
            if output_format == "SVS":
                params = slideio.SVSJp2KParameters()
                params.compression_rate = 3
            elif output_format == "OMETIFF":
                params = slideio.OMETIFFJp2KParameters()
                params.compression_rate = 3
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            with tqdm(total=100, desc="Converting", unit="%") as pbar:
                def callback(percentage):
                    pbar.n = percentage
                    pbar.refresh()
                slideio.convert_scene(scene, params, output_path, callback)
            
            print("Createed file:", output_path)

source_path = r"d:\Projects\slideio\images\slideio_extra\testdata\cv\slideio\gdal\Airbus_Pleiades_50cm_8bit_RGB_Yogyakarta.jpg"
output_path = r"d:\Temp\Airbus_Pleiades_50cm_8bit_RGB_Yogyakarta.ome.tiff"
source_path = r"d:\Projects\slideio\images\slideio_extra\testdata\cv\slideio\czi\pJP31mCherry.czi"
output_path = r"d:\Temp\pJP31mCherry.ome.tiff"
source_path = r"d:\Projects\slideio\images\images\ometiff\private\test.ome.tif"
output_path = r"d:\Temp\test.ome.tif"

def progress(percentage):
    print(f"Conversion progress: {percentage:.2f}%")
callback = lambda perc : progress(perc)
start_time = time.time()
convert_file(source_path, "OMETIFF", "OMETIFF", output_path)
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds")
        