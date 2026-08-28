# Ultrasound_TissueTracking
Analysis for sublayer tissue thickness and bone geometry calculation in static and dynamic tests
This code base is currently under development for assessment of loadbearing tissues in either unloaded or loaded state. 

# Currently in development this is open code for processing and labelling dicom files 
Code currently arranged as scripts with distinct functions: 
* conv_image = generates thumbnail jpeg from DICOM data
* dicom_xarray = builds xarray dataset for multiple dicom files 
* feature_detect = morphology based detection routine
* get_meta_dat = extracts metadata to excel for each file in directory
* us_dicom_data = visual check for xarary data sets
* us_grid = Uses XArray to build 2d stacked grid per participant
* us_image_click = GUI to select points on image, returns excel file with marker co-ordinates 
* us_match = tool to check if dicom files are repeated
* us_spectrum = analysis of layers within tissue 

Author: Dan Parker - University of Salford - 2023 - 2026
d.j.parker1@salford.ac.uk 
