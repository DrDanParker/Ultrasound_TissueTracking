#########################################################
#
#  Ultrasound Dataset Tools
#	For creating a filtered image to allow boundary definition.  
#
#	Author D Parker - University of Salford - May 25
#
#########################################################

import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure, morphology, filters
from scipy.ndimage import gaussian_filter
import pydicom


def enhance(filepath):
    ds = pydicom.dcmread(filepath)

    # Single-frame DICOM
    img = ds.pixel_array[125:780,400:1050,0]

    # Step 1: Denoising:
    # bilateral_filtered = cv2.bilateralFilter(img, d=15, sigmaColor=75, sigmaSpace=75)
    # median_filtered = cv2.medianBlur(img, ksize=15)  # ksize must be odd (3, 5, 7...)
    nlm_filtered_1 = cv2.fastNlMeansDenoising(img, None, h=5, templateWindowSize=7, searchWindowSize=21) #h=filter strength
    nlm_filtered_2 = cv2.fastNlMeansDenoising(img, None, h=10, templateWindowSize=7, searchWindowSize=21) #h=filter strength
    nlm_filtered_3 = cv2.fastNlMeansDenoising(img, None, h=15, templateWindowSize=7, searchWindowSize=21) #h=filter strength
    nlm_filtered_4 = cv2.fastNlMeansDenoising(img, None, h=20, templateWindowSize=7, searchWindowSize=21) #h=filter strength
    nlm_filtered_5 = cv2.fastNlMeansDenoising(img, None, h=25, templateWindowSize=7, searchWindowSize=21) #h=filter strength

    # Step 2: Contrast Enhancement (CLAHE)
    
    img = ds.pixel_array[125:780,400:1050,0]
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    # cont_enhanced_bl = clahe.apply(bilateral_filtered) #Selected out
    # cont_enhanced_med = clahe.apply(median_filtered) #Selected out

    cont_enhanced_nlm_1 = clahe.apply(nlm_filtered_1)
    cont_enhanced_nlm_2 = clahe.apply(nlm_filtered_2)
    cont_enhanced_nlm_3 = clahe.apply(nlm_filtered_3)
    cont_enhanced_nlm_4 = clahe.apply(nlm_filtered_4)
    cont_enhanced_nlm_5 = clahe.apply(nlm_filtered_5)


    # plt.figure()
    # plt.subplot(332)
    # plt.imshow(img,cmap='gray')
    # plt.subplot(334)
    # plt.imshow(bilateral_filtered, cmap='gray')
    # plt.subplot(335)
    # plt.imshow(median_filtered, cmap='gray')
    # plt.subplot(336)
    # plt.imshow(nlm_filtered, cmap='gray')
    # plt.subplot(337)
    # plt.imshow(cont_enhanced_bl, cmap='gray')
    # plt.subplot(338)
    # plt.imshow(cont_enhanced_med, cmap='gray')
    # plt.subplot(339)
    # plt.imshow(cont_enhanced_nlm, cmap='gray')
    # plt.savefig(filepath + '_nlm_enhance.png')
    
    plt.figure()
    plt.subplot(3,5,1)
    plt.imshow(img,cmap='gray')

    ###################################
    ###### Add Spectrum and differentials here. 


    plt.subplot(3,5,6)
    plt.imshow(nlm_filtered_1, cmap='gray')
    plt.subplot(3,5,7)
    plt.imshow(nlm_filtered_1, cmap='gray')
    plt.subplot(3,5,8)
    plt.imshow(nlm_filtered_1, cmap='gray')
    plt.subplot(3,5,9)
    plt.imshow(nlm_filtered_1, cmap='gray')
    plt.subplot(3,5,10)
    plt.imshow(nlm_filtered_1, cmap='gray')
    
    plt.subplot(3,5,11)
    plt.imshow(cont_enhanced_nlm_1, cmap='gray')
    plt.subplot(3,5,12)
    plt.imshow(cont_enhanced_nlm_2, cmap='gray')
    plt.subplot(3,5,13)
    plt.imshow(cont_enhanced_nlm_3, cmap='gray')
    plt.subplot(3,5,14)
    plt.imshow(cont_enhanced_nlm_4, cmap='gray')
    plt.subplot(3,5,15)
    plt.imshow(cont_enhanced_nlm_5, cmap='gray')
    plt.savefig(filepath + '_nlm_enhance.png')
    

    plt.close()

folder = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/TestSet/'
files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file)) and '.' not in file]

for file in files:
    filepath = folder+file
    enhance(filepath)





'''
# Step 2: Contrast Enhancement (CLAHE)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
contrast_enhanced = clahe.apply(denoised)

# Step 3: Edge Detection (Canny)
edges = cv2.Canny(contrast_enhanced, threshold1=30, threshold2=100)

# Step 4: Morphological Gradient to refine edges
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
morph_gradient = cv2.morphologyEx(edges, cv2.MORPH_GRADIENT, kernel)

# Optional: Overlay edges on original for visualization
overlay = cv2.addWeighted(img, 0.8, morph_gradient, 0.5, 0)

# Display results
titles = ['Original', 'Denoised', 'CLAHE', 'Canny Edges', 'Morph Gradient', 'Overlay']
images = [img, denoised, contrast_enhanced, edges, morph_gradient, overlay]

plt.figure(figsize=(15, 8))
for i in range(6):
    plt.subplot(2, 3, i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')
plt.tight_layout()
plt.show()
'''