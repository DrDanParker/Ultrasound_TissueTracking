#########################################################
#
#  Ultrasound Dataset Tools
#	Discreate grid mapping in US image 
#	Uses XArray to build 2d stacked grid per participant
#
#	Author D Parker - University of Salford - Nov 23
#
#########################################################


import os
import numpy as np
import xarray as xr
import pandas as pd
import pydicom as dicom
import matplotlib.pylab as plt
import matplotlib.cm as cm

def rebin(a, n_pix=2):
    n_sh = [a.shape[0]//n_pix,a.shape[1]//n_pix]
    if ((a.shape[0]//n_pix)*n_pix)*((a.shape[1]//n_pix)*n_pix) != (a.shape[0]*a.shape[1]):
        a = a[0:((a.shape[0]//n_pix)*n_pix),0:((a.shape[1]//n_pix)*n_pix)]
        sh = n_sh[0],a.shape[0]//n_sh[0],n_sh[1],a.shape[1]//n_sh[1]
    else:
       sh = n_sh[0],a.shape[0]//n_sh[0],n_sh[1],a.shape[1]//n_sh[1]
    a_mean=a.reshape(sh).mean(-1).mean(1)
    a_sd =a.reshape(sh).std(-1).std(1) # need to check if this is effective way to calc variance across block
    a_max =a.reshape(sh).max(-1).max(1)
    a_min =a.reshape(sh).min(-1).min(1)
    a_sum =a.reshape(sh).max(-1).max(1)
    
    return [a_mean,a_sd,a_max,a_min,a_sum]


def load_image(data_path,outdir):
    files = os.listdir(data_path)
    print('importing files')

    for file in files:
        print(file)
        ds = dicom.dcmread(data_path + file)
        ps = ds.pixel_array

        da = xr.DataArray(data=ps,dims=['d','w','l'],name=ds.PatientName, attrs={'ImageType':ds.ImageType}) # Add more attributes as needed

        crop_image = np.array(da[135:780,400:1050,0]) # top 5 removed to reduce noise from interference
        #nshape = rebin(crop_image,n_pix=10) # reshapes with block of set pixel size

        test_size = [5,10,15,20,25,30,35,40]

        #Mean Plots
        plt.subplots(3, 3, figsize=(10,10))
        plt.subplot(331)
        plt.imshow(crop_image,vmax=100,cmap=cm.get_cmap('jet'))
        for i in range(len(test_size)):
            nshape = rebin(crop_image,n_pix=test_size[i]) # reshapes with block of set pixel size
            plt.subplot(3,3,i+2)
            plt.imshow(nshape[0],vmax=100,cmap=cm.get_cmap('jet'))
        plt.tight_layout()
        plt.savefig(outdir + 'Mean_' + file + '.png')



        #SD Plots
        plt.subplots(3, 3, figsize=(10,10))
        plt.subplot(331)
        plt.imshow(crop_image,vmax=10,cmap=cm.get_cmap('jet'))
        for i in range(len(test_size)):
            nshape = rebin(crop_image,n_pix=test_size[i]) # reshapes with block of set pixel size
            plt.subplot(3,3,i+2)
            plt.imshow(nshape[1],vmax=100,cmap=cm.get_cmap('jet'))
        plt.tight_layout()
        plt.savefig(outdir + 'SD_' + file + '.png')

        #Max Plots
        plt.subplots(3, 3, figsize=(10,10))
        plt.subplot(331)
        plt.imshow(crop_image,vmax=200,cmap=cm.get_cmap('jet'))
        for i in range(len(test_size)):
            nshape = rebin(crop_image,n_pix=test_size[i]) # reshapes with block of set pixel size
            plt.subplot(3,3,i+2)
            plt.imshow(nshape[2],vmax=100,cmap=cm.get_cmap('jet'))
        plt.tight_layout()
        plt.savefig(outdir + 'Max_' + file + '.png')

        #Min Plots
        plt.subplots(3, 3, figsize=(10,10))
        plt.subplot(331)
        plt.imshow(crop_image,vmax=10,cmap=cm.get_cmap('jet'))
        for i in range(len(test_size)):
            nshape = rebin(crop_image,n_pix=test_size[i]) # reshapes with block of set pixel size
            plt.subplot(3,3,i+2)
            plt.imshow(nshape[3],vmax=100,cmap=cm.get_cmap('jet'))
        plt.tight_layout()
        plt.savefig(outdir + 'Min_' + file + '.png')

        #Sum Plots
        plt.subplots(3, 3, figsize=(10,10))
        plt.subplot(331)
        plt.imshow(crop_image,vmax=300,cmap=cm.get_cmap('jet'))
        for i in range(len(test_size)):
            nshape = rebin(crop_image,n_pix=test_size[i]) # reshapes with block of set pixel size
            plt.subplot(3,3,i+2)
            plt.imshow(nshape[4],vmax=100,cmap=cm.get_cmap('jet'))
        plt.tight_layout()
        plt.savefig(outdir + 'Sum_' + file + '.png')



        



fdir = 'D:/DB101/test/'
outdir = 'D:/plots/'
load_image(fdir,outdir)
