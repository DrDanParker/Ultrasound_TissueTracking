import os
from pathlib import Path

folder_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/JPEGS/Diabetes Group/'

print(folder_path)
p = Path(folder_path).parents[1]
print(p)
flist = os.listdir(folder_path)
