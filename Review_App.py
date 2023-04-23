#@author Joshua Phillips - jp1478
import os
from tkinter import filedialog
import tkinter as tk
# from tkinter import ttk
from tkinter import Tk, Button, Label, Scrollbar, Canvas
from PIL import Image, ImageTk
from tkinter import font
def open_review():
    global review
    # review = Tk()
    review.title("Review Page")
    review.state('zoomed')

    myFont = font.Font(size=10, weight="bold")

    # Buttons
    raw_select = Button(review, text="Select Folder", command=lambda: select_folder(True), font = myFont, bg="#525266", fg="#ffffff")
    raw_select.place(relx=.25, rely=.1, width=120, height=50, anchor=tk.N)

    final_select = Button(review, text="Select Folder", command=lambda: select_folder(False), font = myFont, bg="#525266", fg="#ffffff")
    final_select.place(relx=.75, rely=.1, width=120, height=50, anchor=tk.N)

    # Text
    raw_label = Label(review, text="Raw Photos", font = ("Ariel", 22))
    raw_label.place(relx=.25, rely=.04, anchor=tk.N)

    final_label = Label(review, text="Final Photos", font = ("Ariel", 22))
    final_label.place(relx=.75, rely=.04, anchor=tk.N)



    ### Raw Canvas
    global image_canvas
    image_canvas = Canvas(review, bd="3", bg="lightgrey")
    image_canvas.place(relx=.02, rely=.2, relheight = 520/700, relwidth=1140/1200, anchor=tk.NW)
    # image_canvas.config(scrollregion=[0, 0, 570, 1000])

    # image Canvas Scrolling Function
    image_canvas.yview_moveto(0)
    image_canvas.xview_moveto(0)

    # Load and display the image images
    # if bool(raw_images):
    #     display_images()
    # else:
    #     image_canvas.create_text(730, 250,
    #                              text = "Select a folder to review \n \n Folder must have 'raws' and 'finals' sub-folders",
    #                              font = ("Arial", 20),
    #                              justify="center")

    display_images()

    # Raw Canvas Scrollbar
    ybar = Scrollbar(image_canvas, orient=tk.VERTICAL)
    ybar.place(relx=0, rely=0, relheight = 1, anchor=tk.NW)
    ybar.config(command=image_canvas.yview)
    image_canvas.config(yscrollcommand=ybar.set)

    review.mainloop()

def display_images():
    # Aspect Ratio in px: 1920, 1080
    global raw_images
    global final_images
    global message
    # global final_message

    image_canvas.delete("all")
    image_canvas.config(scrollregion=[0, 0, 0, max(len(final_images), len(raw_images)) * (height + height_pad + height_pad) + 16])
    # displayed = 0

    # calculate positions
    center = int(image_canvas.winfo_width()/2)
    group_len = 0
    for image_group in raw_images:
        if len(image_group) > group_len:
            group_len = len(image_group)

    first_image_position = int( center - ((group_len + 2) * width + (group_len+1) * width_pad) / 2 )

    image_x_pos = list()

    for i in range(group_len):
        image_x_pos.append(first_image_position + (width + width_pad) * (i+1))

    image_x_pos.append(first_image_position + (width + width_pad) * (group_len+1) + width_pad)

    line_x = image_x_pos[len(image_x_pos) - 2] + width/2 + width_pad
    image_canvas.create_line(line_x, 0, line_x, image_canvas.winfo_height())

    print("message: ", message)

    if bool(raw_images):
        for i in range(len(raw_images)):
            displayed = i + 1
            group_str = "Group " + str(i + 1)
            image_canvas.create_text(42, 30 + (height + height_pad * 2) * i, text=group_str)
            image_canvas.create_line(0, (height + height_pad * 2) + (i * (height + height_pad * 2)), image_canvas.winfo_width(),
                                       (height + height_pad * 2) + (i * (height + height_pad * 2)))
            group_images = raw_images[i]

            for j in range(len(raw_images[i])):
                label = Label(image_canvas, image=group_images[j])
                x_pos = image_x_pos[group_len - len(group_images) + j]
                y_pos = i * (height + height_pad * 2) + int(height / 2) + height_pad
                image_canvas.create_window(x_pos, y_pos, window=label)
    else:
        # if not bool(message):
        message = "Select a raw image folder"

        # image_canvas.create_text(300, 200, text = raw_message, font = ("Arial", 15), anchor = tk.NE)
        display_message()

    if bool(final_images):# and not bool(final_message):
        for i in range(len(final_images)):
            final_label = Label(image_canvas, image = final_images[i])
            image_canvas.create_window(image_x_pos[len(image_x_pos)-1],
                                       i * (height + height_pad * 2) + int(height / 2) + height_pad,
                                       window = final_label)
    else:
        # if not bool(message):
        message = "Select a final image folder"

        # image_canvas.create_text(1100, 200, text = final_message, font = ("Arial", 15), anchor = tk.NW)
        display_message()


    # print(str(displayed) + " group(s) displayed")

    # image Canvas Scrollbar
    ybar = Scrollbar(image_canvas, orient=tk.VERTICAL)
    ybar.place(relx=0, rely=0, relheight=1, anchor=tk.NW)
    ybar.config(command=image_canvas.yview)
    image_canvas.config(yscrollcommand=ybar.set)

    xbar = Scrollbar(image_canvas, orient=tk.HORIZONTAL)
    xbar.place(relx=1, rely=1, relwidth=1, anchor=tk.SE)
    xbar.config(command=image_canvas.xview)
    image_canvas.config(xscrollcommand=xbar.set)


def select_folder(is_raws_param):
    global message
    # global final_message
    folder_path = filedialog.askdirectory()

    #check if folder was selected
    if not bool(folder_path):
        return

    # check if folder is hidden
    if bool(os.stat(folder_path).st_file_attributes & 2):
        print("Hidden!")
        return

    image_names = [f for f in os.listdir(folder_path) if f.upper().endswith(".DNG")]


    if is_raws_param:
        message = fill_raws(image_names, folder_path)
        # print("select_folder", raw_message)
    else:
        message = fill_finals(image_names, folder_path)
        # print("select_folder", final_message)

    display_images()

def is_raws(image_names):
    for file_name in image_names:
        group_num = file_name[0:file_name.find('-')]
        try:
            group_num = int(group_num)
        except ValueError:
            return False

    return True
def fill_raws(raw_names, folder_path):
    global raw_images

    if not is_raws(raw_names):
        return "Images must be grouped"

    for file_name in raw_names:
        group_num = file_name[0:file_name.find('-')]

        group_num = int(group_num)

        if len(raw_images) < group_num:
            for i in range(len(raw_images), group_num):
                raw_images.append(list())

        image = Image.open(os.path.join(folder_path, file_name))
        image = image.resize((width, height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        raw_images[group_num - 1].append(image)

    return ""

def fill_finals(final_names, folder_path):
    global final_images
    for file_name in final_names:
        image = Image.open(os.path.join(folder_path, file_name))
        image = image.resize((width, height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        final_images.append(image)

    return ""

def display_message():
    global message, review
    message_label = Label(review, text=message, font=("Ariel", 12))
    message_label.place(relx=.5, rely=.03, anchor=tk.N)

# raw_folder_path = ''
# final_folder_path = ''

height = 170
width = 264
height_pad = 5
width_pad = 5

raw_images = list()
final_images = list()
message = 'Select a raw image folder'

review = Tk()
# final_message = 'Select an edited image folder'

open_review()