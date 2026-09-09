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
from scipy.signal import savgol_filter

def extract_top_surface(contour):

    points = contour.squeeze()

    # Handle contours with very few points
    if points.ndim < 2:
        return None

    top_surface = np.array([
        [x, points[points[:,0]==x,1].min()]
        for x in np.unique(points[:,0])])

    dy = np.abs(np.diff(points[:,1]))

    ys = points[:,1]
    i_ymax = np.argmax(ys)
    y_max =np.max(ys)

    y_coords = [i_ymax,y_max]

    y_smooth = savgol_filter(ys,window_length=9,polyorder=3)



    dys = np.diff(y_smooth)
    ddys = np.diff(np.diff(y_smooth))

    split_idx = np.argmax(dy)
    part1 = points[:split_idx]
    part2 = points[split_idx:]
    if np.mean(part1[:,1]) < np.mean(part2[:,1]):
        top_surface2 = part1
    else:
        top_surface2 = part2

    pm = np.argmin(ys)
    pmax = points[pm]

    smax = points[split_idx]


    # y_smooth = savgol_filter(y,window_length=21,polyorder=3)



    # print(len(top_surface))
    # print(top_surface)
    # top_surface = []
    # for x in np.unique(points[:, 0]):
    #     y = points[points[:, 0] == x, 1].min()
    #     top_surface.append([x, y])

    # print(len(top_surface))
    # print(top_surface)    

    return np.array(top_surface),np.array(top_surface2),np.array(y_smooth),np.array(dys),np.array(ddys),y_coords,pmax,smax
    

def bone_filt(img,dicom_path,filename):
    
    # Normalise if necessary
    h, w = img.shape
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX,cv2.COLOR_GRAY2RGB).astype(np.uint8)

    # Initial Filter to Smooth Image
    # blur = cv2.GaussianBlur(img, (15, 15), 0) #Removes most soft tissue noise
    # blur = cv2.GaussianBlur(img, (25, 25), 0) #Removes most soft tissue noise
    # blur = cv2.medianBlur(img, 5)
    blur = cv2.bilateralFilter(img,d=15,sigmaColor=100,sigmaSpace=20)

    # intensity_mask = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
    # intensity_img = cv2.cvtColor(intensity_mask, cv2.COLOR_GRAY2RGB)


    df = pd.DataFrame(blur)
    intensity_mask = df.mask(df < np.max(df)*0.3,1)

    # threshold = 100
    # intensity_mask = (blur > threshold).astype(np.uint8)



    shadow_depth =50
    shadow_mask = np.zeros_like(blur, dtype=np.float32)
    for y in range(blur.shape[0] - shadow_depth):
        above = blur[y,:].astype(float)
        below = np.mean(blur[y+30:y+shadow_depth,:],axis=0)
        ratio = (above - below) / ( above + below + 1e-6 )
        # for r in range(len(ratio)): 
        #     if ratio[r] < 0: ratio[r] = 0
        shadow_mask[y,:] = ratio*100

    df = pd.DataFrame(shadow_mask)
    shadow_mask = df.mask(df < 0,0)

    bone_mask = intensity_mask * shadow_mask
    # bone_mask = bone_mask.mask(bone_mask < np.max(bone_mask)/2, np.nan)

    plt.figure()
    plt.subplot(231)
    plt.imshow(img)
    plt.subplot(232)
    plt.imshow(shadow_mask)
    # plt.colorbar()
    plt.subplot(233)
    plt.imshow(intensity_mask)
    # plt.colorbar()
    plt.subplot(212)
    plt.imshow(bone_mask)
    plt.colorbar()
    plt.savefig(dicom_path + filename + '.png')
    # plt.show()

    return(shadow_mask)


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
    h, w = img.shape # used to chop image from 40 - 100% depth for focus on skeletal structures.

    bone_img = bone_filt(img)

    return

    shadow_depth = 40

    shadow1 = np.zeros_like(img,dtype=np.float32)
    for y in range(img.shape[0]-shadow_depth):
        shadow1[y,:] = (img[y,:].astype(float) - np.mean(img[y+1:y+40,:],axis=0))

    shadow2 = np.zeros_like(blur4,dtype=np.float32)
    for y in range(blur4.shape[0]-shadow_depth):
        shadow2[y,:] = (blur4[y,:].astype(float) - np.mean(blur4[y+1:y+40,:],axis=0))


    bone_response1 = np.zeros_like(img, dtype=np.float32)

    for y in range(img.shape[0] - shadow_depth):
        above = img[y,:].astype(float)
        below = np.mean(img[y+1:y+shadow_depth,:],axis=0)
        bone_response1[y,:] = (above - below) / ( above + below + 1e-6 )

    bone_response2 = np.zeros_like(blur4, dtype=np.float32)

    for y in range(blur4.shape[0] - shadow_depth):
        above = blur4[y,:].astype(float)
        below = np.mean(blur4[y+1:y+shadow_depth,:],axis=0)
        bone_response2[y,:] = (above - below) / ( above + below + 1e-6 )




    plt.subplot(321)
    plt.imshow(img)
    plt.subplot(322)
    plt.imshow(blur4)
    plt.subplot(323)
    plt.imshow(shadow1)
    plt.subplot(324)
    plt.imshow(shadow2)
    plt.subplot(325)
    plt.imshow(bone_response1)
    plt.subplot(326)
    plt.imshow(bone_response2)


    # plt.subplot(422)
    # plt.imshow(blur)
    # plt.subplot(424)
    # plt.imshow(blur2)
    # plt.subplot(426)
    # plt.imshow(blur3)
    # plt.subplot(428)
    # plt.imshow(blur4)

    plt.show()
    return

    # Canny edge detection
    L2Gradient = True
    shadow = cv2.normalize(shadow, None, 0, 255, cv2.NORM_MINMAX,cv2.COLOR_GRAY2RGB).astype(np.uint8)
    edges = cv2.Canny(shadow, 50, 150,L2gradient=L2Gradient) 

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,5))
    # closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )





    # Draw and plot contours over original image
    contour_img = cv2.cvtColor(shadow, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0))



    plt.subplot(212)
    plt.imshow(contour_img)


    plt.show()


    return


    # Initial Levels - could be improved
    # Calc = 
    # MTH = Blur (7,7) edge 75,175
    
    # Find contours
    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )


    top_surfaces1 = []
    top_surfaces2 = []
    y_ = []
    dy_ = []
    ddy_ = []
    pmax_ = []
    smax_ = []
    co_ords = []
    for contour in contours:
        if len(contour) > 15:
            surface1,surface2,ys,dys,ddys,ycoords,pmax,smax = extract_top_surface(contour)
            y_.append(ys)
            dy_.append(dys)
            ddy_.append(ddys)
            co_ords.append(ycoords)
            pmax_.append(pmax)
            smax_.append(smax)
            if surface1 is not None and len(surface1) > 10:
                surface1 = surface1.reshape((-1, 1, 2)).astype(np.int32)
                top_surfaces1.append(surface1)
            if surface2 is not None and len(surface2) > 10:
                surface2 = surface2.reshape((-1, 1, 2)).astype(np.int32)
                top_surfaces2.append(surface2)


    # Draw and plot contours over original image
    contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0))
    
    plt.subplot(211)
    plt.imshow(contour_img)

    for y in pmax_:
        plt.plot(y[0],y[1],marker='*')
        break

    for y in smax_:
        plt.plot(y[0],y[1],marker='+')
        break

    # plt.title("Blur 1 - 50-100")
    # plt.axis('off')

    plt.subplot(212)
    for y in y_:
        plt.plot(y)
        break

    for y in co_ords:
        plt.plot(y[0],y[1],marker='*')
        break


    # plt.subplot(235)
    # for y in dy_:
    #     plt.plot(y)
    # plt.subplot(236)
    # for y in ddy_:
    #     plt.plot(y)

    # Visual Check Point
    
    # plt.figure()
    # plt.subplot(321)
    # plt.imshow(blur)
    # plt.axis('off')

    # plt.subplot(323)
    # plt.imshow(img)
    # plt.axis('off')

    # plt.subplot(325)
    # plt.imshow(blur2)
    # plt.axis('off')

    

    # # Draw and plot contours over original image
    # contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # cv2.drawContours(contour_img, top_surfaces1,-1,(255, 0, 0), 2)
    
    # plt.subplot(324)
    # plt.imshow(contour_img)
    # plt.title("Blur 1 - 50-100")
    # plt.axis('off')

    # # Draw and plot contours over original image
    # contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # cv2.drawContours(contour_img, top_surfaces2,-1,(255, 0, 0), 2)
    
    # plt.subplot(326)
    # plt.imshow(contour_img)
    # plt.title("Blur 1 - 50-100")
    # plt.axis('off')

   

    '''
    L2Gradient = True
    edges = cv2.Canny(blur2, 10, 50,L2gradient=L2Gradient) 

    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )

    top_surfaces = []
    for contour in contours:
        surface = extract_top_surface(contour)
        if surface is not None and len(surface) > 10:
            surface = surface.reshape((-1, 1, 2)).astype(np.int32)
            top_surfaces.append(surface)


    contour_img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img2, top_surfaces,-1,(255, 0, 0), 2)


    plt.subplot(235)
    plt.imshow(contour_img2)
    plt.title("Blur 2 (no_loops) - 10-50")
    plt.axis('off')

    L2Gradient = True
    edges = cv2.Canny(blur2, 10, 50,L2gradient=L2Gradient) 

    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )

    contour_img3 = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img3, contours,-1,(255, 0, 0), 2)

    plt.subplot(236)
    plt.imshow(contour_img3)
    plt.title("Blur 2 - 10-50")
    plt.axis('off')
    '''
    plt.show()

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


        above_height=60 # need to check typical bone depth - calc looks more like 20
        below_depth=20
        """
        Calculate brightness ratio above vs below contour.
        Lower ratio => more likely to be bone.
        """

        # Draw contour
        cv2.drawContours(mask, [contour], -1, 255, 1)
        ys, xs = np.where(mask > 0)

        if max(ys) < h/2:
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

    # for key, value in s_contour_scores[0].items():
        # if key != 'contour':
        #     print(f'{key}={value}')

    best_bone = [s_contour_scores[0]['contour'],
                 s_contour_scores[1]['contour'],
                 s_contour_scores[2]['contour'],
                 s_contour_scores[3]['contour'],
                 s_contour_scores[4]['contour']]

    b_contour_scores = sorted(contour_scores, key=lambda x: x['bone_score'])

    # for key, value in b_contour_scores[0].items():
    #     if key != 'contour':
    #         print(f'{key}={value}')


    best_bone2 = [b_contour_scores[0]['contour'],
                  b_contour_scores[1]['contour'],
                  b_contour_scores[2]['contour'],
                  b_contour_scores[3]['contour'],
                  b_contour_scores[4]['contour']]

    r_contour_scores = sorted(contour_scores, key=lambda x: x['shadow_ratio'])

    # for key, value in r_contour_scores[0].items():
    #     if key != 'contour':
    #         print(f'{key}={value}')


    best_bone3 = [r_contour_scores[0]['contour'],
                  r_contour_scores[1]['contour'],
                  r_contour_scores[2]['contour'],
                  r_contour_scores[3]['contour'],
                  r_contour_scores[4]['contour']]




    

    plt.subplot(233)
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

# def bone_id(dat,dicom_path,filename,steps=20,width=10):

    

    # contours = contour_map(dat)
    # contour_scores = shadow_score(dat,contours,shadow_depth=40)

    # def bone_filt(img):


##### RUN CODE

#get file list:
dicom_path = lf.ultra_point() + '/Heel Hoc_L8/'
flist = [file for file in os.listdir(dicom_path) if os.path.isfile(os.path.join(dicom_path, file)) and '.' not in file]

for filename in flist:
    print(filename)
    # load cropped data:
    raw, cropped = uff.load_dat(dicom_path+filename)
    bone_filt(cropped,dicom_path,filename)

    # bone_id(cropped,dicom_path,filename,steps=50,width=5)
    
