import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from pathlib import Path
from PIL import Image, ImageTk
from itertools import filterfalse
import xarray as xr
import os
import pydicom

class ImageMatcherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Matcher")

        self.j_images = []
        self.current_j_index = 0
        
        self.d_images = []
        self.current_d_index = 0

        self.j_label = tk.Label(self.master, text="Labelled JPEG Image:")
        self.j_label.grid(row=0, column=0,columnspan=2, padx=10, pady=5)

        self.j_label = tk.Label(self.master, text="Unlabelled DICOM Image:")
        self.j_label.grid(row=0, column=3,columnspan=2, padx=10, pady=5)
        
        self.j_name = tk.Label(self.master,text='FileName')
        self.j_name.grid(row=1, column=0,columnspan=2, padx=10, pady=5)

        self.d_name = tk.Label(self.master,text='FileName')
        self.d_name.grid(row=1, column=3,columnspan=2, padx=10, pady=5)
    
        self.j_image_label = tk.Label(self.master)
        self.j_image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        self.d_image_label = tk.Label(self.master)
        self.d_image_label.grid(row=2, column=3, columnspan=2, padx=10, pady=5)
        
        self.load_other_button = tk.Button(self.master, text="Select JPG Folder", command=self.load_jpg_image_folder)
        self.load_other_button.grid(row=3, column=0,columnspan=2, padx=10, pady=5)

        self.load_other_button = tk.Button(self.master, text="Select DICOM Folder", command=self.load_dicom_image_folder)
        self.load_other_button.grid(row=3, column=3, columnspan=2, padx=10, pady=5)

        self.dropdown_var = tk.StringVar(self.master)
        self.dropdown_var.set("CAL")  # set the default option

        self.dropdown = tk.OptionMenu(self.master, self.dropdown_var, "CAL","1ST","5TH","PFA","Vasc")
        self.dropdown.grid(row=3, column=2, padx=10, pady=5)

        self.prev_j_button = tk.Button(self.master, text="Previous", command=self.prev_j_image)
        self.prev_j_button.grid(row=4, column=0, padx=10, pady=5)

        self.next_j_button = tk.Button(self.master, text="Next", command=self.next_j_image)
        self.next_j_button.grid(row=4, column=1, padx=10, pady=5)

        self.match_button = tk.Button(self.master, text="Match", command=self.match_images)
        self.match_button.grid(row=4, column=2, padx=10, pady=5)

        self.prev_d_button = tk.Button(self.master, text="Previous", command=self.prev_d_image)
        self.prev_d_button.grid(row=4, column=3, padx=10, pady=5)

        self.next_d_button = tk.Button(self.master, text="Next", command=self.next_d_image)
        self.next_d_button.grid(row=4, column=4, padx=10, pady=5)

        # self.close_button = tk.Button(self.master, text="Complete", command=self.closeout)
        # self.close_button.grid(row=5, column=2, padx=10, pady=5)
        # 2364


    def load_jpg_image_folder(self):
        j_folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Image Folder")
        if j_folder_path:
            self.load_j_images(j_folder_path)
            self.show_current_j_image()

    def load_dicom_image_folder(self):
        d_folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Image Folder")
        self.d_path = d_folder_path
        if d_folder_path:
            self.load_d_images()
            self.show_current_d_image()
    
    def remove_done(self,folder_path):
        part = folder_path.split('/')[-1][:5]
        self.opath = str(Path(folder_path).parents[2]).replace('\\','/') + '/Xarrays/' + part

        if os.path.exists(self.opath):
            done_list = os.listdir(self.opath)

            for i in range(len(done_list)):
                done_list[i] = done_list[i][:-3]

            flist = os.listdir(folder_path)

            for i in range(len(flist)):
                flist[i] = flist[i][:-4]
                
            olist = list(filterfalse(done_list.__contains__,flist))

        else:
            olist = os.listdir(folder_path)
        return(olist)

                

    def load_j_images(self, folder_path):
        self.j_images.clear()
        flist = self.remove_done(folder_path)

        dvar = self.dropdown_var.get()
        
        for filename in flist:
            if dvar in filename:
                if 'jpg' in filename:
                    image_path = os.path.join(folder_path, filename)
                    print('importing: ' + filename)
                    image = Image.open(image_path)
                    image.thumbnail((600, 600))
                    self.j_images.append((filename, ImageTk.PhotoImage(image)))
    
    def load_d_images(self):
        self.d_images.clear()
        # self.datasets = {}
        flist = os.listdir(self.d_path)
        for filename in flist:
            image_path = os.path.join(self.d_path, filename)
            if os.stat(image_path).st_size < 10485760:
                if os.stat(image_path).st_size > 100000:
                    print('importing: ' + filename)
                    ds = pydicom.dcmread(image_path)
                    pixel_array = ds.pixel_array
                    image = Image.fromarray(pixel_array)
                    image.thumbnail((600, 600))
                    self.d_images.append((filename, ImageTk.PhotoImage(image)))

    def drop_down(self):
        options = ["CAL","1ST","5TH","PFA"]
        clicked = StringVar(self.master) 
        clicked.set( "CAL" ) 
        drop = OptionMenu(self.master , clicked , *options )
        self.drop_button.config( text = clicked.get() ) 

    def prev_j_image(self):
        if self.current_j_index > 0:
            self.current_j_index -= 1
            self.show_current_j_image()

    def next_j_image(self):
        if self.current_j_index < len(self.j_images) - 1:
            self.current_j_index += 1
            self.show_current_j_image()
        else:
            self.current_j_index = 0
            self.show_current_j_image()
            

    def prev_d_image(self):
        if self.current_d_index > 0:
            self.current_d_index -= 1
            self.show_current_d_image()

    def next_d_image(self):
        if self.current_d_index < len(self.d_images) - 1:
            self.current_d_index += 1
            self.show_current_d_image()
        else:
            self.current_d_index = 0
            self.show_current_d_image()

    def show_current_d_image(self):
        fname, img = self.d_images[self.current_d_index]
        self.d_image_label.config(image=img)
        self.d_image_label.image = img
        self.d_name["text"] = fname

    def show_current_j_image(self):
        try:
            fname, img = self.j_images[self.current_j_index]
        except IndexError:
            fname = 'No More Images'
            img = []

        self.j_image_label.config(image=img)
        self.j_image_label.image = img
        self.j_name["text"] = fname

    def match_images(self):
        j_filename = self.j_images[self.current_j_index][0]
        d_filename = self.d_images[self.current_d_index][0]

        # self.o_path = self.d_path + '/output/' 
        # if not os.path.exists(self.o_path):
        #   os.makedirs(self.o_path)


        print("Match found between reference image '{}' and '{}'".format(j_filename, d_filename))
        
        ### Create Xarray file from dicom data:
        image_path = os.path.join(self.d_path, d_filename)
        ds = pydicom.dcmread(image_path)
        pixel_array = ds.pixel_array


        da = xr.DataArray(data=pixel_array.astype(int),dims=['d','w','l']) # Add more attributes as needed
        c_da = da[125:780,400:1050]
        c_da.to_netcdf(self.opath + j_filename[:-4] + '.nc')
        # print('data exported to: ' + o_path + j_filename[:-4] + '.nc') 

        #### Remove matched files from file list
        self.j_images.pop(self.current_j_index)
        self.d_images.pop(self.current_d_index)
        self.next_d_image()
        self.next_j_image()


    def closeout(self):
        # out_file_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Output Folder")
        # combined = xr.concat(self.datasets,dim='files')
        ds = xr.Dataset(self.datasets)
        ds.to_netcdf(self.d_path + '/dicom_labelled.nc')
        print('data exported to: ' + self.d_path + '/dicom_CALC_labelled.nc') 


def main():
    root = tk.Tk()
    app = ImageMatcherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()





# def on_closing():
#     if messagebox.askokcancel('quit','do you want to quit'):
#         root.destroy()
    
