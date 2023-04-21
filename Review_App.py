#@author jp1478
import os
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Button, Label, Scrollbar, Canvas
# from tkinter import *
# from tkinter.ttk import *
from PIL import Image, ImageTk
from tkinter import font
def open_review():
    review = Tk()
    review.title("Review Page")
    review.state('zoomed')

    myFont = font.Font(size=12, weight="bold")

    # Buttons
    reselect = Button(review, text="Select Folder", command=select_folder, font = myFont, bg="#525266", fg="#ffffff")
    reselect.place(relx=.5, rely=.04, width=120, height=50, anchor=tk.N)

    # Text
    raw_label = Label(review, text="Raw Photos", font = ("Ariel", 22))
    raw_label.place(relx=.3, rely=.1, anchor=tk.NW)
    image_label = Label(review, text="Final Photos", font = ("Ariel", 22))
    image_label.place(relx=.9, rely=.1, anchor=tk.NE)



    ### Raw Canvas
    global image_canvas
    image_canvas = Canvas(review, bd="3", bg="lightgrey")
    image_canvas.place(relx=.02, rely=.2, relheight = 520/700, relwidth=1140/1200, anchor=tk.NW)
    # image_canvas.config(scrollregion=[0, 0, 570, 1000])

    # image Canvas Scrolling Function
    image_canvas.yview_moveto(0)
    image_canvas.xview_moveto(0)

    # Load and display the image images
    if folder_path != "":
        display_images()
    else:
        image_canvas.create_text(730, 250,
                                 text = "Select a folder to review \n \n Folder must have 'raws' and 'finals' sub-folders",
                                 font = ("Arial", 20),
                                 justify="center")


    # Raw Canvas Scrollbar
    ybar = Scrollbar(image_canvas, orient=tk.VERTICAL)
    ybar.place(relx=0, rely=0, relheight = 1, anchor=tk.NW)
    ybar.config(command=image_canvas.yview)
    image_canvas.config(yscrollcommand=ybar.set)

    review.mainloop()

def display_images():
    # Aspect Ratio in px: 1920, 1080

    print(image_canvas.winfo_width() / 2, image_canvas.winfo_height() / 2)

    height = 170
    width = 264
    height_pad = 5
    width_pad = 5

    global raw_images
    global final_images

    image_canvas.delete("all")

    image_canvas.config(scrollregion=[0, 0, 0, len(final_images) * (height + height_pad + height_pad) + 16])

    displayed = 0

    center = int(image_canvas.winfo_width()/2)
    group_len = 0
    for image_group in raw_images:
        if len(image_group) > group_len:
            group_len = len(image_group)

    first_image_position = int( center - ((group_len + 2) * width + (group_len+1) * width_pad) / 2 )

    image_x_pos = list()

    for i in range(0, group_len):
        image_x_pos.append(first_image_position + (width + width_pad) * (i+1))

    image_x_pos.append(first_image_position + (width + width_pad) * (group_len+1) + width_pad)

    line_x = image_x_pos[len(image_x_pos) - 2] + width/2 + width_pad
    image_canvas.create_line(line_x, 0, line_x, image_canvas.winfo_height())

    for i in range(len(final_images)):
        displayed = i + 1
        group_str = "Group " + str(i + 1)
        image_canvas.create_text(42, 30 + (height + height_pad * 2) * i, text=group_str)
        image_canvas.create_line(0, (height + height_pad * 2) + (i * (height + height_pad * 2)), image_canvas.winfo_width(),
                                   (height + height_pad * 2) + (i * (height + height_pad * 2)))
        group_images = raw_images[i]

        for j in range(len(raw_images[i])):
            group_images[j] = group_images[j].resize((width, height), Image.LANCZOS)
            group_images[j] = ImageTk.PhotoImage(group_images[j])
            label = Label(image_canvas, image=group_images[j])
            x_pos = image_x_pos[group_len - len(group_images) + j]
            y_pos = i * (height + height_pad * 2) + int(height / 2) + height_pad
            image_canvas.create_window(x_pos, y_pos, window=label)

        final_images[i] = final_images[i].resize((width, height), Image.LANCZOS)
        final_images[i] = ImageTk.PhotoImage(final_images[i])
        final_label = Label(image_canvas, image = final_images[i])
        image_canvas.create_window(image_x_pos[len(image_x_pos)-1],
                                   i * (height + height_pad * 2) + int(height / 2) + height_pad,
                                   window = final_label)

    print(str(displayed) + " group(s) displayed")

    # image Canvas Scrollbar
    ybar = Scrollbar(image_canvas, orient=tk.VERTICAL)
    ybar.place(relx=0, rely=0, relheight=1, anchor=tk.NW)
    ybar.config(command=image_canvas.yview)
    image_canvas.config(yscrollcommand=ybar.set)

    xbar = Scrollbar(image_canvas, orient=tk.HORIZONTAL)
    xbar.place(relx=1, rely=1, relwidth=1, anchor=tk.SE)
    xbar.config(command=image_canvas.xview)
    image_canvas.config(xscrollcommand=xbar.set)


def select_folder():
    global folder_path
    global raw_images
    global final_images

    folder_path = filedialog.askdirectory()

    # check if folder is hidden
    if bool(os.stat(folder_path).st_file_attributes & 2):
        print("Hidden!")
    else:
        raw_names = [f for f in os.listdir(os.path.join(folder_path, "raws")) if f.endswith((".DNG", ".dng"))]
        # group raws
        for file_name in raw_names:
            group_num = file_name[0:file_name.find('-')]

            group_num = int(group_num)

            if len(raw_images) < group_num:
                for i in range(len(raw_images), group_num):
                    raw_images.append(list())

            raw_images[group_num-1].append(Image.open(os.path.join(folder_path, "raws", file_name)))


        final_names = [f for f in os.listdir(os.path.join(folder_path, "finals")) if f.endswith((".DNG", ".dng"))]
        for raw, final in zip(raw_names, final_names):
            final_images.append(Image.open(os.path.join(folder_path, "finals", final)))

    display_images()

folder_path = ''
raw_images = list()
final_images = list()

open_review()