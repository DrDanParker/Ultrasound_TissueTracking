####
import os
import cv2 
import local_file_links as lf ## Localised script to set directories for local test files - to be updated with links to test set available on git. 
import pydicom
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pylab as plt


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

def load_dat(dicom_file): # Loads dicom file, converts to pixel array and returns cropped data focused on image frame. 
    
    ds = pydicom.dcmread(dicom_file)
    px = ds.pixel_array
    gx = rgb2gray(px)

    

    # Convert the new array to a DataArray
    da = xr.DataArray(gx, dims=['x', 'y'],name=ds.PatientName)
    #  attrs={'ImageType':ds.ImageType}) # Add more attributes as needed
            

    # plt.figure()
    # plt.imshow(da)
    cropped = np.array(da[130:800,200:1200])
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
    edges = cv2.Canny(blur, 75, 175) # Initial Levels - could be improved
    # Find contours
    contours, hierarchy = cv2.findContours(edges, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE
                                           )

    # Visual Check Point
    # Draw and plot contours over original image
    contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(contour_img, contours,-1,(255, 0, 0), 2)

    plt.figure()
    plt.imshow(contour_img)
    plt.axis('off')
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
        if length < 20:
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

        score = (shadow_pixels)
        
        contour_scores.append({'contour': contour,'length': length,'shadow_score': score})

    contour_scores = sorted(contour_scores, key=lambda x: x['shadow_score'])
    print(contour_scores[])
    best_bone = contour_scores[0]['contour']


    display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(display,[best_bone],-1,(255, 0, 0),3)

    plt.figure(figsize=(8,6))
    plt.imshow(display)
    plt.title("Bone Contour with Strongest Acoustic Shadow")
    plt.axis('off')
    plt.show()

    return(contour_scores)

def bone_id(dat,dicom_path,filename,steps=20,width=10):

    contours = contour_map(dat)
    contour_scores = shadow_score(dat,contours,shadow_depth=30)




    y_size,x_size = dat.shape
    main = pd.DataFrame()

    offset = 50 #50 used to offset skin layer
    for i in range(0+width,x_size,int((x_size-(width*steps))/steps)):
        # main[i] = pd.DataFrame(dat[offset:,i-width:i+width]).mean(axis=1) 
        main[i] = pd.DataFrame(dat[offset:,i-width:i+width]).max(axis=1) 

    # canny_detect(dat)
    # sobel_detect(dat)
    # laplacian_detect(dat)

    
    ## add initial threshold to narrow range or guess to remove skin:
    max_s = main.max().max()
    
    ## Find Lower bound of range:
    filtered_df = main[main > max_s*0.4] #nominal value. 
    last_non_nan = filtered_df.apply(pd.Series.last_valid_index) + offset
    
    ## remove noise:
    df = last_non_nan.diff().abs()
    no_noise = last_non_nan.loc[df < 10]
    
    #Find Clusters:
    x_cut = 120
    y_cut = 50
    n_cut = 5   #Heel L2-9 = 5

    holder = pd.Series()
    set = []
    for i in range(1,len(no_noise.index)):
        diffx = no_noise.index[i] - no_noise.index[i-1]
        diffy = abs(no_noise.iloc[i] - no_noise.iloc[i-1])
        if diffx < 120 and diffy < 50:
            holder[no_noise.index[i]] = no_noise.iloc[i]
        else:
            if len(holder) > n_cut:
                set.append(holder)
            holder = pd.Series()
    if len(holder) > n_cut:
        set.append(holder)




    plt.figure()
    plt.subplot(221)
    plt.imshow(dat,cmap='gray')
    
    plt.subplot(222)
    plt.imshow(dat,cmap='gray')
    plt.plot(last_non_nan, 'x',color = 'r')

    plt.subplot(223)
    plt.imshow(dat,cmap='gray')
    plt.plot(no_noise, 'x',color = 'r')

    plt.subplot(224)
    plt.imshow(dat,cmap='gray')
    for s in set: 
        plt.plot(s, 'x')

    # plt.subplot(322)
    # plt.imshow(dat,cmap='gray')

    # # plt.subplot(324)
    # plt.imshow(filtered_df_1,cmap='gray')



    # plt.subplot(324)
    # plt.imshow(dat,cmap='gray')
    # plt.plot(skel_a, 'x',color = 'r')
    
    plt.tight_layout()
    # plt.savefig(dicom_path+filename + '_cluster.png')
    plt.show()
    return()


'''
def spectrum(dat,dicom_path,filename,steps=20,width=5):
    y_size,x_size = dat.shape
    main = pd.DataFrame()

    offset = 50 #50 used to offset skin layer
    for i in range(0+width,x_size,int((x_size-(width*steps))/steps)):
        # main[i] = pd.DataFrame(dat[offset:,i-width:i+width]).mean(axis=1) 
        main[i] = pd.DataFrame(dat[offset:,i-width:i+width]).max(axis=1) 

    last_non_nan = main.apply(pd.Series.last_valid_index) + offset


    # ## add initial threshold to narrow range or guess to remove skin:
    # max_s = main.max().max()
    
    # ## Find Lower bound of range:
    # filtered_df_1 = main[main > max_s*0.3] # nominal value --- need to check across wider dataset -- may need to look at setting based on the grayscale range. 
    # last_non_nan_1 = filtered_df_1.apply(pd.Series.last_valid_index) + offset

    #Find Largest Cluster:
    holder = pd.Series()
    set = []
    for i in range(1,len(last_non_nan_1.index)):
        diffx = last_non_nan_1.index[i] - last_non_nan_1.index[i-1]
        diffy = abs(last_non_nan_1.iloc[i] - last_non_nan_1.iloc[i-1])
        if diffx < 120 and diffy < 50:
            holder[last_non_nan_1.index[i]] = last_non_nan_1.iloc[i]
        else:
            set.append(holder)
            holder = pd.Series()
    set.append(holder)

    sorted_sets = sorted(set, key=len, reverse=True)
    skel_a = sorted_sets[0]



    # for i in range(1,len(filtered_data)):
    #     if filtered_data[i].

    # filtered_df_2 = main[main > max_s*0.4] # nominal value --- need to check across wider dataset -- may need to look at setting based on the grayscale range. 
    # last_non_nan_2 = filtered_df_2.apply(pd.Series.last_valid_index) + offset

    #### Apply curve fit to the xy points generated here. 
    # This could be 2d https://scipython.com/blog/non-linear-least-squares-fitting-of-a-two-dimensional-data/
    # or could be itterative fitting of arcs in blocks of 10 points - if meets set criteria accept. 


    plt.figure()
    # plt.subplot(321)
    # plt.imshow(dat,cmap='gray')
    # plt.plot(last_non_nan_1, 'x',color = 'r')

    # plt.subplot(323)
    # plt.imshow(dat,cmap='gray')
    # for s in set: 
    #     plt.plot(s, 'x')

    # plt.subplot(322)
    # plt.imshow(dat,cmap='gray')

    # plt.subplot(324)
    plt.imshow(filtered_df_1,cmap='gray')



    # plt.subplot(324)
    # plt.imshow(dat,cmap='gray')
    # plt.plot(skel_a, 'x',color = 'r')
    
    plt.tight_layout()
    plt.savefig(dicom_path+filename + '_cluster.png')
    # plt.show()
    return()



    ###
    ### To here -- have defined range (between yellow bounds) now need to find bone landmarks. 
    ###

    
    spect = pd.DataFrame()
    spect['max'] = filtered_df.max(axis=1)
    spect['sum'] = filtered_df.sum(axis=1)
    
    spect['mean'] = main.mean(axis=1)
    spect['diff'] = spect['sum'].diff()
    spect['neg_diff'] = spect['diff']*-1
    spect['acc'] = spect['sum'].diff().diff().abs()

    print(min_base)
    print(max_base)
    plt.figure()

    plt.subplot(321)
    plt.plot(main[50:])
    plt.plot(spect['max'][min_base:max_base],'k',linewidth=2)
    max_max = spect['max'][min_base:max_base].idxmax()

    plt.subplot(323)
    plt.plot(main[50:])
    plt.plot(spect['sum'][min_base:max_base],'k',linewidth=2)
    sum_max = spect['sum'][min_base:max_base].idxmax()

    # mid_y = (max_max + sum_max) / 2


    plt.subplot(122)
    plt.imshow(dat,cmap='gray')
    plt.plot(last_non_nan, 'x',color = 'r')
    plt.hlines(y=max_max,xmin=0,xmax=990,color='g')
    plt.hlines(y=sum_max,xmin=0,xmax=990,color='b')

    plt.hlines(y=min_base,xmin=0,xmax=990,color='y',linestyle='--')
    plt.hlines(y=max_base,xmin=0,xmax=990,color='y',linestyle='--')
    


    # plt.hlines(y=max_max+100,xmin=0,xmax=1000,color='r',linestyle='-')
    # plt.hlines(y=max_max-10,xmin=0,xmax=1000,color='r',linestyle='-')

    plt.tight_layout()
    plt.savefig(dicom_path+filename + '_spect.png')
    # plt.show()
    return()
'''

#test file:
# dicom_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Tracker_TestSet/Heel Hoc_L8/'
dicom_path = lf.ultra_point() + '/1MTP L2-9/'

# print(dicom_path)


# fname = 'DB105_2_CALC_L2-9'
# flist = os.listdir(dicom_path)
flist = [file for file in os.listdir(dicom_path) if os.path.isfile(os.path.join(dicom_path, file)) and '.' not in file]

for filename in flist:
    # load cropped data:
    raw, cropped = load_dat(dicom_path+filename)
    bone_id(cropped,dicom_path,filename,steps=50,width=5)
    
'''
###
# 
# Bone ID - find apex of the bone
# frequency plot at x interval (10 slices)
# find middle of signal range in y direction (where white leve is highest)
# define search field based on this and narrow x and y
#   y based on random guess of 50% down ~2cm depth.
#   x based on middle of image but looking at slices to find highest value/s in y window.  
# replot frequency plots for narrow search 
# find bone segments
#
###


'''