import os
import numpy as np
import xarray as xr
import pandas as pd
from scipy.signal import find_peaks
import pydicom as dicom
import matplotlib.pylab as plt

def load_image(dicom_image,fname):
    ### to load in ultrasound pixel data from dicom file
    print('processing:', fname)
    ds = dicom.dcmread(dicom_image)
    ps = ds.pixel_array
    da = xr.DataArray(data=ps,dims=['d','w','l'],name=ds.PatientName, attrs={'ImageType':ds.ImageType}) # Add more attributes as needed
    crop_image = np.array(da[125:780,400:1050,0])

    plt.figure()
    plt.imshow(crop_image,cmap='Greys_r')
    plt.savefig(out_path + fname +'_CROPPED.jpeg')
    plt.close()

    return(crop_image)

def bone_geom(x_im,fname,start=400,window_size=50):
    ### To be refined works sort of for calc
    x_size,y_size = x_im.shape
    steps = int(y_size/100)
    b_geo = pd.DataFrame()
    
    for i in range(0,y_size,steps):
        b_geo[i] = x_im[start-window_size:start+window_size,i]
    
    mx = b_geo.max(axis=0)
    ys = b_geo.idxmax(axis=0)
    ys = ys + start-window_size
    xs = range(0,y_size,steps)

    vals = pd.DataFrame()
    vals['Grey'] = mx
    vals['Y-Pos'] = ys

    bone = vals.loc[vals['Grey'] > 30]

    # plt.figure()
    # plt.subplot(121)
    # plt.plot(bone['Grey'])
    # plt.subplot(122)
    # plt.plot(bone['Y-Pos'])
    # plt.savefig(out_path + fname +'_Bone.jpeg')
    # plt.close()

    return(bone)


def spectrum(x_im,fname):
    ### to define intensity of speckle across image
    x_size,y_size = x_im.shape
    steps = int(y_size/20)
    spect = pd.DataFrame()
    for i in range(0,y_size,steps):
        spect[i] = x_im[:,i]

    plt.figure()
    plt.subplot(121)
    plt.plot(spect)
    spect['ave'] = spect.mean(axis=1)
    plt.plot(spect['ave'],color='k',linestyle='-',linewidth=3)
    
    ### Find Peaks and trim to 500 depth
    peaks, _ = find_peaks(spect['ave'], height=5, distance=60)
    peaks = [x for x in peaks if x < 500]

    plt.plot(peaks, spect['ave'][peaks], "ro", markersize=8, label="Peaks")
    plt.subplot(222)
    plt.imshow(x_im,cmap='Greys_r')
    plt.subplot(224)
    plt.imshow(x_im,cmap='Greys_r')
    for peak in peaks:
        plt.axhline(y=peak, color='r', linestyle='-')

    if peaks[-1] > 300:
        bone = bone_geom(x_im,fname,peaks[-1])
        plt.plot(bone['Y-Pos'],color='g',linewidth='2')


    plt.savefig(out_path + fname +'_Spectrum.jpeg')
    plt.close()

    return(spect)


################################################################

### Setup:
dicom_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Stage 2/DICOM/DB108/Calc/'
out_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Stage 2/DICOM/DB108/Calc_Images/'
dicom_files = os.listdir(dicom_path)

### Act:
for file in dicom_files:
    crop_image = load_image(dicom_path+file,file)
    spect = spectrum(crop_image,file)