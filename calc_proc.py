
import os
import cv2
import numpy as np
import pandas as pd
import xarray as xr
from scipy.signal import find_peaks
from scipy import signal
import pydicom as dicom
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import matplotlib


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])


def enhance_contrast(data_array):

    # Convert to NumPy and ensure uint8
    image = data_array.values.astype(np.uint8)

    # Apply histogram equalization
    enhanced_image = cv2.equalizeHist(image)

    # Convert back to Xarray DataArray
    return xr.DataArray(enhanced_image, dims=data_array.dims, coords=data_array.coords)



def detect_edges(data_array: xr.DataArray) -> xr.DataArray:
    # Convert to NumPy and ensure uint8
    image = data_array.values.astype(np.uint8)

    
    blurred = cv2.GaussianBlur(image, (5, 5), 1.4)


    # Setup Dynamic Threshold
    median_val = np.median(image)
    lower = int(max(0, 1 * median_val))
    # upper = int(min(255, 1.75 * median_val))

    # Apply Canny edge detection
    edges = cv2.Canny(image, lower, 255)


    # edges = cv2.Canny(image, threshold1=245, threshold2=255)

    # Convert back to Xarray DataArray
    return xr.DataArray(edges, dims=data_array.dims, coords=data_array.coords)


def map_contours(data_array: xr.DataArray) -> xr.DataArray:
    # Convert to NumPy and ensure uint8
    image = data_array.values.astype(np.uint8)


    # Apply Canny edge detection
    edges = cv2.Canny(image, threshold1=np.max(image)-50, threshold2=np.max(image)*3)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on a copy of the original image
    image_with_contours = cv2.drawContours(image.copy(), contours, -1, (255, 0, 0), 2)

    # Convert back to Xarray DataArray
    return xr.DataArray(edges, dims=data_array.dims, coords=data_array.coords), xr.DataArray(image_with_contours, dims=data_array.dims, coords=data_array.coords)



def gs_enhance(data_array, fig_name):

    
    # enhanced_image = cv2.equalizeHist(data_array)

    # print(type(data_array))


    # Convert to NumPy and ensure uint8
    # image = data_array.values.astype(np.uint8)

    # Apply histogram equalization
    enhanced_image = enhance_contrast(data_array)
    
    # Detect edges
    # edges = detect_edges(data_array)

    # Map contours
    edges, contours = map_contours(data_array)



    plt.figure()
    plt.subplot(2,2,1)
    plt.imshow(data_array,cmap='Greys_r')
    plt.subplot(2,2,2)
    plt.imshow(enhanced_image.values,cmap='Greys_r')


    # Plot original image
    plt.subplot(2, 3, 4)
    plt.imshow(enhanced_image.values, cmap='gray')
    plt.title('Original Image')
    plt.axis('off')

    # Plot edge-detected image
    plt.subplot(2, 3, 5)
    plt.imshow(edges.values, cmap='gray')
    plt.title('Edge Detection')
    plt.axis('off')

    # Plot image with contours
    plt.subplot(2, 3, 6)
    plt.imshow(contours.values, cmap='gray')
    plt.title('Contours Mapped')
    plt.axis('off')

    
    plt.savefig(fig_name)


def import_convert(d_path):

    if os.path.isfile(d_path + 'dicom_greyscale_dataset.nc'):
        print('Importing existing dataset')
        dataset = xr.open_dataset(d_path + 'dicom_greyscale_dataset.nc')
        return(dataset)

    else:
        files = [file for file in os.listdir(d_path) if os.path.isfile(os.path.join(d_path, file)) and '.' not in file]
        print('importing files:')

        outpath = d_path + 'dicom_greyscale_dataset.nc'
        dataset = xr.Dataset()

        for file in files:
            print(file)
            ds = dicom.dcmread(d_path + file)
            ps = ds.pixel_array
            ps_g = rgb2gray(ps) # Convert RGB to Greyscale
            ps_crop = ps_g[130:800,200:1250]
            # Convert the new array to a DataArray
            d_array = xr.DataArray(ps_crop, dims=['x', 'y'],name=ds.PatientName)
            # Add the new DataArray to the Dataset
            dataset[file] = d_array
        dataset.to_netcdf(path=outpath)

    return(dataset)            
    
def bone_geom(x_im,fig_name,start=400,window_size=50):
    ### To be refined works sort of for calc
    # x_size,y_size = x_im.shape
    steps = 5
    b_geo = pd.DataFrame()
    
    for i in range(400,800,steps):
        b_geo[i] = x_im[start-window_size:start+window_size,i]
    
    mx = b_geo.max(axis=0)
    ys = b_geo.idxmax(axis=0)
    ys = ys + start-window_size
    xs = range(400,800,steps)

    vals = pd.DataFrame()
    vals['Grey'] = mx
    vals['Y-Pos'] = ys

    bone = vals.loc[vals['Grey'] > 30]

    plt.figure()
    plt.subplot(121)
    plt.plot(bone['Grey'])
    plt.subplot(122)
    plt.plot(bone['Y-Pos'])
    plt.savefig(fig_name)
    plt.close()

    return(bone)

def layers(x_im,fig_name):
    
    # fname = out_path +folder + '/' + filename

    ### to define intensity of speckle across image
    steps = 10
    main = pd.DataFrame()
    for i in range(100,560,steps):
        main[i] = x_im[:,i]

    spect = pd.DataFrame()
    spect['ave'] = main.mean(axis=1)
    spect['sum'] = main.sum(axis=1)
    spect['diff'] = spect['sum'].diff()
    spect['neg_diff'] = spect['diff']*-1
    spect['acc'] = spect['sum'].diff().diff().abs()

    plt.figure()
    plt.subplot(521)
    plt.plot(spect['ave'][:25])
    plt.subplot(522)
    plt.plot(spect['ave'][25:])
    plt.subplot(523)
    plt.plot(spect['sum'][:25])
    plt.subplot(524)
    plt.plot(spect['sum'][25:])
    plt.subplot(525)
    plt.plot(spect['diff'][:25])
    plt.subplot(526)
    plt.plot(spect['diff'][25:])
    plt.subplot(527)
    plt.plot(spect['neg_diff'][:25])
    plt.subplot(528)
    plt.plot(spect['neg_diff'][25:])
    plt.subplot(529)
    plt.plot(spect['acc'][:25])
    plt.subplot(5,2,10)
    plt.plot(spect['acc'][25:])
    plt.tight_layout()
    plt.savefig(fig_name + 'spect.png')
    plt.close()

    o_data = pd.Series()
    
    ### Range peaks:
    ## RO - Skin_start
    skin_start = spect['ave'][0:50].diff().idxmax()
    
    ## RO - Skin_End
    base = skin_start+30
    ave_skin = spect['neg_diff'][:base].mean()
    skin_peaks, _ = find_peaks(spect['neg_diff'][:base], height=ave_skin*1.5, distance=5)
    skin_peaks = [value for value in skin_peaks if value-skin_start >= 8]
    skin_end = spect['neg_diff'][skin_peaks].idxmax()


    #### Checked To Here - Happy measures are appropriate. 

    ## R1 - Micro
    micro_max = spect['ave'][skin_end+45:skin_end+150].idxmax()
    micro_end = spect['ave'][skin_end+40:micro_max].diff().idxmax()

    ## R2 - Calc
    s_calc_ave = spect['ave'][micro_end+100:-25]
    s_calc_sum = spect['sum'][micro_end+100:-25]
    s_calc_dif = spect['diff'][micro_end+100:-25]
    s_calc_acc = spect['acc'][micro_end+100:-25]

    ## based on sum data 
    ave_cal = s_calc_sum.mean()
    cave_peaks, _ = find_peaks(s_calc_sum, height=ave_cal*1.5, distance=60)
    cave_peaks = cave_peaks + micro_end+100
    if cave_peaks[-1] < 600:
        calc_sum_peak = cave_peaks[-1]
    else:
        calc_sum_peak = cave_peaks[-2]


    ## refine based on acceleration data
    acc_cal = spect['acc'][calc_sum_peak-100:calc_sum_peak+50].mean()
    min_bound = calc_sum_peak-100
    if min_bound < micro_end+100:
        min_bound = micro_end+100
    cacc_peaks, _ = find_peaks(spect['acc'][min_bound:calc_sum_peak+20], height=acc_cal*1.5, distance=60)
    cacc_peaks = cacc_peaks + min_bound
    calc_peak = cacc_peaks[-1]
    



    loc_peaks = [skin_start,skin_end, micro_end,calc_peak]

    o_data['skin_start'] = skin_start
    o_data['skin_end'] = skin_end
    o_data['micro_end'] = micro_end
    o_data['calc'] = calc_peak
    o_data['skin_thickness'] = skin_end - skin_start
    o_data['micro_thickness'] = micro_end - skin_end
    o_data['macro_thickness'] = calc_peak - micro_end
    o_data['tissue_thickness'] = calc_peak - skin_start
    o_data['skin_ratio'] = (skin_end - skin_start)/(calc_peak - skin_start)
    o_data['micro_ratio'] = (micro_end - skin_end)/(calc_peak - skin_start)
    o_data['macro_ratio'] = (calc_peak - micro_end)/(calc_peak - skin_start)

    # ofigname = out_path + filename + '.png'

    fig = plt.figure() 
    ax1 = fig.add_subplot(231)
    # gs = gridspec.GridSpec(2, 1)
    # ax1.set_position(gs[0:2].get_position(fig))

    ax1.plot(spect['sum'],color='k',linestyle='-',linewidth=1)
    ax1.plot(s_calc_sum,color='b',linestyle='-',linewidth=1)
    

    ax1.plot(cave_peaks,s_calc_sum[cave_peaks],'ro', markersize=2)
    ax1.plot(cacc_peaks,s_calc_sum[cacc_peaks],'go', markersize=2)
    ax1.plot(calc_peak,s_calc_sum[calc_peak],'yo', markersize=2)
    # ax1.plot(cdif_peaks,s_calc_sum[cdif_peaks],'go', markersize=4)

    # ax1.plot(skin_start,spect['ave'][skin_start],'go', markersize=3)
    # ax1.plot(skin_end,spect['ave'][skin_end],'bo', markersize=3)
    # ax1.plot(micro_end,spect['ave'][micro_end],'ro', markersize=3)
    # ax1.plot(micro_max,spect['ave'][micro_max],'go', markersize=3)
    
    # ax1.axvline(x=skin_start,color='g',linestyle='--')
    # ax1.axvline(x=skin_end,color='b',linestyle='--')
    
    # ax2 = fig.add_subplot(gs[2])
    ax2 = fig.add_subplot(232)
    ax2.plot(spect['diff'],color='k',linestyle='-',linewidth=1)
    ax2.plot(spect['diff'][min_bound:calc_sum_peak+20],color='b',linestyle='-',linewidth=1)
    
    ax2.plot(cave_peaks,s_calc_dif[cave_peaks],'ro', markersize=2)
    ax2.plot(cacc_peaks,s_calc_dif[cacc_peaks],'go', markersize=2)
    ax2.plot(calc_peak,s_calc_dif[calc_peak],'yo', markersize=2)
    # ax2.plot(cdif_peaks,s_calc_dif[cdif_peaks],'go', markersize=4)
    
    # ax2.plot(skin_start,spect['neg_diff'][skin_start],'go', markersize=3)
    # ax2.plot(skin_end,spect['diff'][skin_end],'bo', markersize=3)
    # ax2.plot(micro_end,spect['diff'][micro_end],'ro', markersize=3)
    
    # ax2.axvline(x=skin_start,color='g',linestyle='--')
    # ax2.axvline(x=skin_end,color='b',linestyle='--')

    ax3 = fig.add_subplot(233)
    ax3.plot(spect['acc'],color='k',linestyle='-',linewidth=1)
    ax3.plot(spect['acc'][min_bound:calc_sum_peak+30],color='b',linestyle='-',linewidth=1)

    ax3.plot(cave_peaks,s_calc_acc[cave_peaks],'ro', markersize=2)
    ax3.plot(cacc_peaks,s_calc_acc[cacc_peaks],'go', markersize=2)
    ax3.plot(calc_peak,s_calc_acc[calc_peak],'yo', markersize=2)
    

    # ax3.plot(cave_peaks,s_calc_acc[cave_peaks],'ro', markersize=2)
    # ax3.plot(cdif_peaks,s_calc_acc[cdif_peaks],'go', markersize=4)

    # ax3.plot(skin_start,spect['neg_diff'][skin_start],'go', markersize=3)
    # ax3.plot(skin_end,spect['acc'][skin_end],'bo', markersize=3)
    # ax3.plot(micro_end,spect['acc'][micro_end],'ro', markersize=3)
    
    # ax3.axvline(x=skin_start,color='g',linestyle='--')
    # ax3.axvline(x=skin_end,color='b',linestyle='--')



    ax4 = fig.add_subplot(212)
    ax4.imshow(x_im,cmap='Greys_r')
    ax4.axhline(y=skin_start,color='g',linestyle='--')
    ax4.axhline(y=skin_end,color='b',linestyle='--')
    ax4.axhline(y=micro_end,color='r',linestyle='--')
    
    ax4.axhline(y=calc_sum_peak,color='r',linestyle='--')
    ax4.axhline(y=calc_peak,color='y',linestyle='--')
    # ax4.axhline(y=micro_end+100,color='g',linestyle='--')
    # ax4.axhline(y=630,color='g',linestyle='--')

    # fig.suptitle(filename)
    plt.tight_layout()
    plt.savefig(fig_name + 'layers.png')
    plt.clf()
    # plt.close()

    return(spect, o_data)



##################
## RUN CODE
##################

# d_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/DICOM/Diabetes Group/DB101/Calc_Sagittal/MAT/'

# d_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Stage 2/DICOM/DB108/Calc/'
dir_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Stage 2/DICOM/'

folders = os.listdir(dir_path)
print(folders)

for folder in folders:
    calc_path = dir_path + folder + '/Calc/'
    print(calc_path)
    if os.path.isdir(calc_path):
        d_set = import_convert(calc_path)

        # processed_data = {}
        for var_name, data_array in d_set.data_vars.items():
            fig_name = calc_path + var_name +'.png'
            gs_enhance(data_array, fig_name)
        #     # processed_data[var_name] = layers(data_array,calc_path,'/Layers/',var_name)
        #     # print(fig_name)
        #     bone = bone_geom(data_array,fig_name,start=400,window_size=50)
        #     # dat = layers(data_array,fig_name)

        # print(processed_data)

    else:
        print('No Calc File in ' + folder)


'''
d_set = import_convert(d_path)

# Cyle through each data array in dataset and apply functions.
processed_data = {}
for var_name, data_array in d_set.data_vars.items():
    processed_data[var_name] = layers(data_array,d_path,'/Layers/',var_name)

'''