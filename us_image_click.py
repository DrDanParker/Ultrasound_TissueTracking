import os

import tkinter as tk
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

from itertools import filterfalse
from pathlib import Path
from openpyxl import load_workbook
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk


class XArrayImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XArray Image App")
        self.root.geometry("800x600")
        
        self.directory = None
        self.data = None
        self.locations = []
        self.cross_ids = []
        self.xarrays = []
        self.current_x_index = 0

        # add function to select label group based on file name
        self.region = 'Calc'
        self.layers = ['Outer Skin','Inner Skin','Outer Micro','Micro-Macro','Calc']
        self.labels = [(self.region,layer) for layer in self.layers]
        
        o_index = pd.MultiIndex.from_tuples(self.labels, names=["Region", "Point"])
        self.output = pd.DataFrame(index=o_index)
        
        frame = ttk.Frame(self.root)
        frame.pack(pady=20)
        
        self.select_dir_button = ttk.Button(frame, text="Select Folder", command=self.select_directory)
        self.select_dir_button.grid(row=0,column=0, columnspan=2, padx=5,pady=5)

        self.prev_x_button = tk.Button(frame, text="Previous", command=self.prev_x_image)
        self.prev_x_button.grid(row=1, column=0, padx=10, pady=5)

        #self.next_x_button = tk.Button(frame, text="Save", command=self.save)
        #self.next_x_button.grid(row=1, column=1, padx=10, pady=5)

        self.next_x_button = tk.Button(frame, text="Next", command=self.next_x_image)
        self.next_x_button.grid(row=1, column=2, padx=10, pady=5)

        self.image_name = tk.Label(frame,text='FileName')
        self.image_name.grid(row=2, column=1,columnspan=2, padx=10, pady=5)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()
        
        for i in range(len(self.labels)):
            button = tk.Button(self.buttons_frame, text=self.labels[i][1], command=lambda i=i: self.select_point(i))
            button.grid(row=3, column=i, padx=5, pady=5)
        
        self.selected_button = None
        self.current_button = None

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack()



        
    def select_directory(self):
        self.folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Xarray Folder")
        #self.folder_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/Xarrays/DB101/'

        if self.folder_path:
            self.select_dir_button["text"] = 'Select New Folder'
            self.open_current_sheet()
            self.load_xarray()
            self.show_current_image()

    def remove_done(self):
        ################################# this isnt working correctly ##################### 
        try:
            done_list = list(self.current_sheet.columns)
            print('Existing data for ',len(done_list), ' files:')
            for f in done_list:
                print(' ',f)
            flist = os.listdir(self.folder_path)
            olist = list(filterfalse(done_list.__contains__,flist))
            print('Importing ', len(olist), ' unmeasured files:')
        except:
            olist = os.listdir(self.folder_path)
        return(olist)



    def load_xarray(self):
        self.xarrays.clear()
        
        flist = self.remove_done()
        

        for filename in flist:
            print(' ', filename)
            xarray_path = os.path.join(self.folder_path, filename)
            xr_f = xr.open_dataarray(xarray_path)
            image = Image.fromarray(np.array(xr_f[:,:,0]))
            self.xarrays.append((filename, ImageTk.PhotoImage(image)))
        

    def open_current_sheet(self):

        fdir = str(Path(self.folder_path).parents[1]).replace('\\','/') + '/Output.xlsx'
        sheetname = self.folder_path.split('/')[-1].split('_')[0] + '_' + self.region
        print(sheetname)
                                                          
        try:
            self.current_sheet = pd.read_excel(fdir,sheet_name=sheetname,index_col=[0,1])
            

            print('Sheet exists for this directory and region')
            print(self.current_sheet)
            
        except:
            print('No data for: ', sheetname)


    def merge_output(self):
        try:
            for col in self.current_sheet:
                for mcol in self.output:
                    if col == mcol:
                        self.output = self.output.rename(columns={mcol: mcol+'_'})
            self.output = pd.concat([self.current_sheet,self.output],axis=1)
            print(self.output)
        except:
            print('No data to merge')

            
    def save(self):

        fdir = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/Output.xlsx'
        sheetname = self.xarrays[self.current_x_index][0].split('_')[0] + '_' + self.region

        self.merge_output()

        with pd.ExcelWriter(fdir, mode="a", if_sheet_exists="replace") as writer:
            self.output.to_excel(writer, sheet_name=sheetname)

        del writer


        

    def prev_x_image(self):
        if self.current_x_index > 0:
            self.current_x_index -= 1
            self.show_current_image()
            if self.locations: 
                self.output[self.xarrays[self.current_x_index][0]] = self.locations
                self.save()
                self.locations=[]
            self.locations=[]
            print(self.output)

    def next_x_image(self):
        if self.current_x_index < len(self.xarrays) - 1:
            self.current_x_index += 1
            self.show_current_image()
            if self.locations: 
                self.output[self.xarrays[self.current_x_index][0]] = self.locations
                self.save()
                self.locations=[]
            self.locations=[]
            print(self.output)
        else:
            self.current_x_index = 0
            self.show_current_image()
            if self.locations: 
                self.output[self.xarrays[self.current_x_index][0]] = self.locations
                self.save()
                self.locations=[]
            self.locations=[]
            print(self.output)
            
    def show_current_image(self):
        fname, img = self.xarrays[self.current_x_index]
        self.canvas.config(width=img.width(), height=img.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.image_name["text"] = fname

    def on_canvas_click(self, event):
        if self.selected_button is not None:
            x, y = event.x, event.y
            self.locations[self.current_button] = (x, y)
            print(f"{self.selected_button} selected at ({x}, {y})")
            self.update_crosses()
            
    def select_point(self, index):
        self.selected_button = self.labels[index]
        self.current_button = index
        if len(self.locations) <= index:
            self.locations.extend([None] * (index + 1 - len(self.locations)))

    def update_crosses(self):
        # Clear existing crosses
        for cross_id in self.cross_ids:
            self.canvas.delete(cross_id)
        self.cross_ids = []

        # Draw new crosses at selected locations
        for (i, loc) in enumerate(self.locations):
            if loc is not None:
                x, y = loc
                cross_size = 5
                cross_id1 = self.canvas.create_line(x - cross_size, y, x + cross_size, y, fill='red', width=2)
                cross_id2 = self.canvas.create_line(x, y - cross_size, x, y + cross_size, fill='red', width=2)
                self.cross_ids.extend([cross_id1, cross_id2])


'''
    def image_click(self):
        print('clicked')

    def plot_data(self):
        if self.data is None:
            messagebox.showerror("Error", "No data to plot.")
            return
        
        fig, ax = plt.subplots()
        fname, img = self.xarrays[self.current_x_index]

        self.im = ax.imshow(img) 
        self.fig_canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes:
            if self.current_marker < 5:
                x, y = int(event.xdata), int(event.ydata)
                self.coords.append((x, y))
                self.coord_labels[self.current_marker].config(text=f"Coord {self.current_marker + 1}: ({x}, {y})")
                self.current_marker += 1
                self.update_plot(x, y)

    def update_plot(self, x, y):
        self.im.axes.plot(x, y, 'rx')
        self.fig_canvas.draw()


'''


if __name__ == "__main__":
    root = tk.Tk()
    app = XArrayImageApp(root)
    root.mainloop()
