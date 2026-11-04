



import os
import xarray as xr
import numpy as np
import pandas as pd
import pydicom
import matplotlib.pylab as plt
from matplotlib.widgets import Slider

import local_file_links as lf 

from pydicom.pixels import pixel_array 


dicom_path = lf.ultra_point() + '/USVid/'

print(dicom_path)

from pydicom import dcmread

flist = [file for file in os.listdir(dicom_path) if os.path.isfile(os.path.join(dicom_path, file)) and '.' not in file]

for filename in flist:

    file_path = dicom_path + filename
    
    meta = dcmread(file_path, stop_before_pixels=True)
    frames = meta.NumberOfFrames

    with open(file_path, 'rb') as f:
        arr = pixel_array(f,index=0)
        da = xr.DataArray(data=arr,dims=['d','w','l'])

        # Create figure and main plot
        fig, ax = plt.subplots()
        im = ax.imshow(da,cmap='Greys_r')
        
        # Create slider axes
        axcolor = 'lightgoldenrodyellow'
        ax1 = fig.add_axes([0.2, 0.9, 0.65, 0.03])
        
        # Create sliders
        slider1 = Slider(ax1, 'Frame (time)', 0, frames-1, valinit=0)
        
        
        def update(val1):
            # Slice the 4D array along both axes
            arr2 = pixel_array(f,index=int(val1))
            da2 = xr.DataArray(data=arr2,dims=['d','w','l'])
            # im = ax.imshow(da,cmap='Greys_r')
            im.set_data(da2)
            fig.canvas.draw_idle()




        # Connect sliders to update function
        slider1.on_changed(update)

        #### to add buttons for fine tuning the slider, see https://matplotlib.org/stable/gallery/widgets/slider_demo.html


        
        plt.show()



    








