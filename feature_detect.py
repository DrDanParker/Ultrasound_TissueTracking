import pydicom
import cv2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.optimize import curve_fit, minimize 
from skimage import feature, filters, morphology, measure


def quadratic_polynomial(len_x, a, b, c):
    # Define a quadratic polynomial function
    return a * (np.arange(len_x) - b) ** 2 + c


'''
def objective_function(params, x_values, y_values):
    # Objective function for optimization
    a, b, c, delta_y, delta_x, slope_adjust = params
    adjusted_x_values = x_values - delta_x
    adjusted_y_values = y_values - delta_y
    adjusted_y_values /= slope_adjust
    fitted_curve = quadratic_polynomial(adjusted_x_values, a, b, c)
    return np.sum((fitted_curve - adjusted_y_values) ** 2)

def fit_and_adjust_curve(image):
    # Get the dimensions of the image
    rows, cols = image.shape

    print(rows)
    print(cols)

    # Initial guess for curve fitting parameters
    initial_guess = [0.001, cols / 2, 400.0, 0, 0, 1.0]

    # Optimize the parameters to find the best fit
    result = minimize(
        objective_function,
        initial_guess,
        args=(x_flat, z_flat),
        method='Powell',  # You can try other optimization methods
    )
    

    # # Generate x and y values based on the pixel coordinates
    # x_values, y_values = np.meshgrid(np.arange(cols), np.arange(rows))
    
    # # Flatten the coordinate arrays for curve fitting
    # x_flat = x_values.flatten()
    # y_flat = y_values.flatten()
    # z_flat = image.flatten()
    
    
    
    # Get the optimized parameters
    optimized_params = result.x
    
    # Apply the optimized parameters to the parabolic curve
    a, b, c, delta_y, delta_x, slope_adjust = optimized_params
    adjusted_x_values = x_flat - delta_x
    adjusted_y_values = y_flat - delta_y
    adjusted_y_values /= slope_adjust
    fitted_curve = quadratic_polynomial(adjusted_x_values, a, b, c)
    
    # Reshape the fitted curve to the original image shape
    fitted_curve_image = fitted_curve.reshape((rows, cols))
    
    return fitted_curve_image

def plot_results(original_image, fitted_curve_image):
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(original_image, cmap='gray')
    plt.title('Original Image')
    
    plt.subplot(1, 2, 2)
    plt.imshow(fitted_curve_image, cmap='gray')
    plt.title('Fitted Curve to Image')
    
    plt.show()

def fit_curve_to_image(image):
    # Get the dimensions of the image
    rows, cols = image.shape
    
    # # Generate x values based on the number of columns
    # x_values = np.arange(cols)
    

    # Generate x and y values based on the pixel coordinates
    x_values, y_values = np.meshgrid(np.arange(cols), np.arange(rows))
    
    # Flatten the coordinate arrays for curve fitting
    x_flat = x_values.flatten()
    y_flat = y_values.flatten()
    z_flat = image.flatten()
    
    print(len(x_flat))

    # Perform the curve fitting
    initial_guess = [0.001, len(x_flat)/2, 400.0] # Initial guess for curve fitting parameters
    popt, pcov = curve_fit(modified_curvature_curve, x_flat, z_flat, p0=initial_guess)
    
    # Reshape the fitted curve to the original image shape
    fitted_curve = modified_curvature_curve(x_flat, *popt).reshape((rows, cols))
    
    return fitted_curve

def plot_results(original_image, fitted_curve):
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(original_image, cmap='gray')
    plt.title('Original Image')
    
    plt.subplot(1, 2, 2)
    plt.imshow(fitted_curve, cmap='gray')
    plt.title('Fitted Curve to Image')
    
    plt.show()
'''

# Load DICOM file
file_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/2023 - October/26.10.23/__093417/'

d_file = ['NAQB01OC','NAQB01OE','NAQB01OG','NAQB01PG','NAQB01PM']

# fig = plt.figure()
# gs1 = gridspec.GridSpec(len(d_file), 2)

fig, ax = plt.subplots(len(d_file),2,gridspec_kw={'width_ratios': [1, 2]})

fn = 1

for f in d_file:
    
    dicom_file = file_path + f
    dicom_data = pydicom.dcmread(dicom_file)

    # Extract pixel data from DICOM
    image_array = dicom_data.pixel_array

    # Thresholding to create a binary mask
    _, binary_mask = cv2.threshold(image_array[130:800,400:1050,0], thresh=100, maxval=255, type=cv2.THRESH_BINARY)

    bmax = np.sum(binary_mask,axis=1)

    for i in range(len(bmax[::-1])):
        if bmax[::-1][i] >= 0.5:
            break
    bmax_skel = i

    ROI_Skel = binary_mask[bmax_skel-200:bmax_skel,:]

    poly_y = quadratic_polynomial(650, 0.001, 650 / 2, 100.0)

    a = len(d_file)

    print(fn)

    # plt.subplot(a,2,(fn*2)-1)
    ax1 = fig.add_subplot(a,2,(fn*2)-1)
    ax1.imshow(binary_mask)
    ax1.plot(650/2,bmax_skel,'x')
    
    # plt.subplot(a,2,fn*2)
    ax2 = fig.add_subplot(a,2,(fn*2))
    ax2.imshow(ROI_Skel)
    ax2.plot(poly_y)

    fn +=1



# plt.subplots_adjust(wspace=0)
plt.tight_layout()
plt.show()




# plt.figure()
# plt.imshow(binary_mask[200:400,:])
# plt.show()

# fitted_curve_image = fit_and_adjust_curve(binary_mask)
# plot_results(image_array[130:800,400:1050,0], fitted_curve_image)

# fitted_curve_image = fit_curve_to_image(binary_mask)
# plot_results(image_array[130:800,400:1050,0], fitted_curve_image)


'''
# Apply edge detection (example: Sobel filter)

# edges_sobel = filters.sobel(image_array[130:800,400:1050,0])
edges_canny = feature.canny(binary_mask, sigma=0.01)

# Find contours in the edge-detected image
contours_canny = measure.find_contours(edges_canny, level=0.1)
# contours_sobel = measure.find_contours(edges_sobel, level=0.9)



# Apply morphological operations (example: skeletonization)
# skeleton = morphology.skeletonize(edges > 0)

# Display the processed image with skeletal structures
plt.figure(figsize=(10, 10))
plt.subplot(131)
plt.imshow(image_array[130:800,400:1050,0], cmap='gray')

plt.subplot(132)
plt.imshow(binary_mask, cmap='gray')


plt.subplot(133)
plt.imshow(edges_canny, cmap='jet')
for contour in contours_canny:
    plt.plot(contour[:, 1], contour[:, 0], linewidth=2, color='red')


# plt.subplot(133)
# plt.imshow(skeleton, cmap='jet')
# plt.title('Ultrasound Image with Skeletal Structures')
plt.show()
'''