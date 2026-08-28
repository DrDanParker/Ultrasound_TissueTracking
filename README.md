# Ultrasound\_TissueTracking

Analysis for sublayer tissue thickness and bone geometry calculation in static and dynamic tests
This code base is currently under development for assessment of loadbearing tissues in either unloaded or loaded state.

# Currently in development this is open code for processing and labelling dicom files

Code currently arranged as scripts with distinct functions:

* conv\_image = generates thumbnail jpeg from DICOM data
* dicom\_xarray = builds xarray dataset for multiple dicom files
* feature\_detect = morphology based detection routine
* get\_meta\_dat = extracts metadata to excel for each file in directory
* us\_dicom\_data = visual check for xarary data sets
* us\_grid = Uses XArray to build 2d stacked grid per participant
* us\_image\_click = GUI to select points on image, returns excel file with marker co-ordinates
* us\_match = tool to check if dicom files are repeated
* us\_spectrum = analysis of layers within tissue
* clean\_image = apply filters to reduce speckle noise
* track\_testset = implementation of feature ID and tracking

Author: Dan Parker - University of Salford - 2023 - 2026
d.j.parker1@salford.ac.uk

