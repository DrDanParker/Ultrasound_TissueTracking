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


        above_height=20 # need to check typical bone depth - calc looks more like 20
        below_depth=20
        """
        Calculate brightness ratio above vs below contour.
        Lower ratio => more likely to be bone.
        """

        # Draw contour
        cv2.drawContours(mask, [contour], -1, 255, 1)
        ys, xs = np.where(mask > 0)

        if max(ys) < 100:
            continue

        above_vals = []
        below_vals = []

        for x, y in zip(xs, ys):

            # Region above contour
            y_top = max(0, y - above_height)
            above_vals.extend(img[y_top:y, x].flatten())

            # Region below contour
            y_bottom = min(h, y + below_depth)
            below_vals.extend(img[y+1:y_bottom, x].flatten())

        if len(above_vals) == 0 or len(below_vals) == 0:
            shadow_ratio = 0
            

        mean_above = np.mean(above_vals)
        mean_below = np.mean(below_vals)

        shadow_ratio = mean_above / (mean_below + 1e-6)


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

        contour_scores.append({'contour': contour,'length': length,'shadow_score': score,'bone_score':bone_score,'shadow_ratio':shadow_ratio})

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

    r_contour_scores = sorted(contour_scores, key=lambda x: x['shadow_ratio'])

    for key, value in r_contour_scores[0].items():
        if key != 'contour':
            print(f'{key}={value}')


    best_bone3 = [r_contour_scores[0]['contour'],
                  r_contour_scores[1]['contour'],
                  r_contour_scores[2]['contour'],
                  r_contour_scores[3]['contour'],
                  r_contour_scores[4]['contour']]




    plt.figure(figsize=(8,6))

    plt.subplot(232)
    contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0), 2)
    plt.imshow(contour_img)
    plt.title("Contours")
    # plt.axis('off')


    plt.subplot(234)
    display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display,best_bone,-1,(255, 0, 0),3)

    plt.imshow(display)
    plt.title("Shadow Score")
    plt.axis('off')

    plt.subplot(235)
    display2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display2,best_bone2,-1,(255, 0, 0),3)

    plt.imshow(display2)
    plt.title("Bone Score")
    plt.axis('off')

    plt.subplot(236)
    display3 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display3,best_bone3,-1,(255, 0, 0),3)

    plt.imshow(display3)
    plt.title("Shadow Ratio")
    plt.axis('off')



    plt.show()

    return(contour_scores)

def bone_id(dat,dicom_path,filename,steps=20,width=10):

    contours = contour_map(dat)
    contour_scores = shadow_score(dat,contours,shadow_depth=40)



##### RUN CODE

#get file list:
dicom_path = lf.ultra_point() + '/Heel L2-9/'
flist = [file for file in os.listdir(dicom_path) if os.path.isfile(os.path.join(dicom_path, file)) and '.' not in file]

for filename in flist:
    # load cropped data:
    raw, cropped = uff.load_dat(dicom_path+filename)
    bone_id(cropped,dicom_path,filename,steps=50,width=5)
    
