#########################################################
#
#  Ultrasound Dataset Tools
#	skel_detect - Find distinct bone structures  
#
#	Author D Parker - University of Salford - Sept 26
#
#########################################################

'''
Dev Notes:
current working on shadow_score function
looking to improve id of bone regions

Next steps
look at clustering of contours from the same bone based on position/geometry
Try to generate a single bone layer for each distinct bone. 

Aim at this stage is to ID each bone and will then refine to locate surface of each segment. 

'''

import os
import cv2 
import local_file_links as lf ## Localised script to set directories for local test files - to be updated with links to test set available on git. 
import pydicom
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import us_filefunctions as uff

def load_dat(dicom_file): # Loads dicom file, converts to pixel array and returns cropped data focused on image frame. 
    
    ds = pydicom.dcmread(dicom_file)
    px = ds.pixel_array
    gx = uff.rgb2gray(px)

    # Convert the new array to a DataArray
    da = xr.DataArray(gx, dims=['x', 'y'],name=ds.PatientName)
    #  attrs={'ImageType':ds.ImageType}) # Add more attributes as needed

    # Crop for system settings 
    # System is GE 
    cropped = np.array(da[130:800,200:1200])

    # plt.figure()
    # plt.imshow(da)

    # cropped = da[130:800,200:1200]
    # plt.figure()
    # plt.imshow(cropped)
    # plt.show()

    return(da, cropped)

def contour_map(df): # Uses Canny filter to detect edges and create initial candidate contours
    '''
    Parameters:
    df : grayscale image
    Notes:
    * Other filter approaches (Sobel and Laplacian) were tested for this, Canny was best. 
    * Morphological closing was tested but had minimal effect on identified contours    
    '''

    # Convert fromat of image
    img = df.astype(np.uint8)
    # Normalise if necessary
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    # Smooth image
    blur = cv2.GaussianBlur(img, (7, 7), 0) #Removes most soft tissue noise

    # Canny edge detection
    L2Gradient = True
    edges = cv2.Canny(blur, 75, 175,L2gradient=L2Gradient) # Initial Levels - could be improved
    # Find contours
    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )

    # Visual Check Point
    # Draw and plot contours over original image
    contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0), 2)

    # plt.figure()
    # plt.imshow(contour_img)
    # plt.axis('off')
    # plt.show()

    return(contours)

def shadow_score(img, contours,shadow_depth=30):
    '''
    Parameters:
    img : grayscale image
    contours : set of OpenCV contours
    shadow_depth : pixels below contour to evaluate
    '''

    # Convert fromat of image
    img = img.astype(np.uint8)
    
    contour_scores = []
    for contour in contours:
        length = cv2.arcLength(contour, False)
        if length < 100:
            continue

        h, w = img.shape
        mask = np.zeros_like(img, dtype=np.uint8)

        # Draw contour
        cv2.drawContours(mask, [contour], -1, 255, thickness=1)
        ys, xs = np.where(mask > 0)

        shadow_pixels = []
        for x, y in zip(xs, ys):
            y1 = y + 1
            y2 = min(y + shadow_depth, h)
        if y2 > y1:
            shadow_pixels.extend(img[y1:y2, x].flatten())

        if len(shadow_pixels) == 0:
            score = np.inf

        score = np.mean(shadow_pixels)

        y_top = np.min(contour[:,0,1])

        bone_score = (0.4*(255-score) + 0.2*length - 0.4*y_top)

        contour_scores.append({'contour': contour,'length': length,'shadow_score': score,'bone_score':bone_score})

    s_contour_scores = sorted(contour_scores, key=lambda x: x['shadow_score'])

    for key, value in s_contour_scores[0].items():
        if key != 'contour':
            print(f'{key}={value}')

    best_bone = [s_contour_scores[0]['contour'],
                 s_contour_scores[1]['contour'],
                 s_contour_scores[2]['contour'],
                 s_contour_scores[3]['contour'],
                 s_contour_scores[4]['contour']]

    b_contour_scores = sorted(contour_scores, key=lambda x: x['bone_score'])

    for key, value in b_contour_scores[0].items():
        if key != 'contour':
            print(f'{key}={value}')


    best_bone2 = [b_contour_scores[0]['contour'],
                  b_contour_scores[1]['contour'],
                  b_contour_scores[2]['contour'],
                  b_contour_scores[3]['contour'],
                  b_contour_scores[4]['contour']]

    plt.figure(figsize=(8,6))

    plt.subplot(121)
    contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0), 2)
    plt.imshow(contour_img)
    plt.title("Contours")
    plt.axis('off')


    plt.subplot(222)
    display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display,best_bone,-1,(255, 0, 0),3)

    plt.imshow(display)
    plt.title("Shadow Score")
    plt.axis('off')

    plt.subplot(224)
    display2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display2,best_bone2,-1,(255, 0, 0),3)

    plt.imshow(display2)
    plt.title("Bone Score")
    plt.axis('off')


    plt.show()

    return(contour_scores)

def bone_id(dat,dicom_path,filename,steps=20,width=10):

    contours = contour_map(dat)
    contour_scores = shadow_score(dat,contours,shadow_depth=40)



##### RUN CODE

#get file list:
dicom_path = lf.ultra_point() + '/1MTP L2-9/'
flist = [file for file in os.listdir(dicom_path) if os.path.isfile(os.path.join(dicom_path, file)) and '.' not in file]

for filename in flist:
    # load cropped data:
    raw, cropped = uff.load_dat(dicom_path+filename)
    bone_id(cropped,dicom_path,filename,steps=50,width=5)
    
