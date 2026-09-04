# Ultrasound\_TissueTracking

Analysis for sublayer tissue thickness and bone geometry calculation in static and dynamic tests
This code base is currently under development for assessment of loadbearing tissues in either unloaded or loaded state.

# Currently in development this is open code for processing and labelling dicom files

Code currently arranged as scripts with distinct functions:

* skel\_detect = functions for identification of distinct skeletal structures
* us\_filefunctions = functions for handling data and preprocessing dicom images


Prior code being imported or adapted:
* conv\_image = generates thumbnail jpeg from DICOM data
* feature\_detect = morphology based detection routine
* us\_grid = Uses XArray to build 2d stacked grid per participant
* us\_spectrum = analysis of layers within tissue
* clean\_image = apply filters to reduce speckle noise
* track\_testset = implementation of feature ID and tracking
* calc\_proc = application to analysis of calcaneus region images

Author: Dan Parker - University of Salford - 2023 - 2026
d.j.parker1@salford.ac.uk

