import pydicom
import pandas as pd
import os
# import openpyxl

#folder
data_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Extracted for manual labelling/'
files = [file for file in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, file)) and '.' not in file]

for file in files:
    # Load the DICOM file
    ds = pydicom.dcmread(data_path + file)

    
    metadata = {elem.name: str(elem.value) for elem in ds}
    df = pd.DataFrame([metadata])

    # df.to_excel(data_path + "full_dicom_metadata.xlsx", index=False)
    for tag in df.keys():
        print(tag + '  : ' + df[tag])
    break

    '''
    # Define a list of common metadata tags to extract
    tags_to_extract = [
        "PatientName", "PatientID", "PatientBirthDate", "PatientSex",
        "StudyDate", "StudyTime", "StudyDescription", "Modality",
        "SeriesDescription", "InstitutionName", "Manufacturer",
        "ReferringPhysicianName", "BodyPartExamined", "ProtocolName"
    ]

    # Extract available metadata
    metadata = {}
    for tag in tags_to_extract:
        value = getattr(ds, tag, "N/A")
        metadata[tag] = str(value)

    # Convert to DataFrame
    df = pd.DataFrame([metadata])

    # Save to Excel
    output_path = "dicom_metadata.xlsx"
    df.to_excel(output_path, index=False)

    print(f"Metadata saved to {output_path}")
    '''