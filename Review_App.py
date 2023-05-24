#@author Joshua Phillips - jp1478
import os
import tkinter as tk
from datetime import datetime
from tkinter import Tk, Button, Label, Scrollbar, Canvas, font, filedialog, ttk
from tkinter.ttk import Notebook, Frame, Style
from PIL import Image, ImageTk
# import psycopg2
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
import atexit

def open_review():
    global root
    root.title("Critical Review")
    root.state('zoomed')
    root.configure(background = "#a9a9af")
    my_font = font.Font(size=10, weight="bold", family = "Gadugi")

    ############## Tabs ##################
    style = Style()
    style.theme_create("MyStyle", settings={
        "TNotebook": {"configure": {"tabmargins": [5, 5, 2, 0]}},
        "TNotebook.Tab": {
            "configure": {"padding": [50, 10], "foreground":"#ffffff", "background":"#727286", "font":("Gadugi", 11)},
            "map":       {"background": [("selected", "#dadada")], "foreground": [("selected", "#000000")] }}})
                          # "expand": [("selected", [1, 1, 1, 0])]

    style.theme_use("MyStyle")

    tabControl = Notebook(root)

    review = Frame(tabControl)
    global notes
    notes = Frame(tabControl)

    tabControl.add(review, text='Image Review')
    tabControl.add(notes, text='Notes')
    tabControl.place(relx=0.01, rely=0.02, relwidth=0.98, relheight=0.96)
    ######################################

    # Buttons
    select = Button(review, text="Select Folder", command=select_folder, font = my_font, bg="#727286", fg="#ffffff")
    select.place(relx=.5, rely=.05, width=120, height=50, anchor=tk.N)

    # Text
    raw_label = Label(review, text="Raw Photos", font = ("Gadugi", 22), bg="#dadada")
    raw_label.place(relx=.25, rely=.05, anchor=tk.N)

    final_label = Label(review, text="Final Photos", font = ("Gadugi", 22), bg="#dadada")
    final_label.place(relx=.75, rely=.05, anchor=tk.N)

    ### Raw Canvas
    global image_canvas
    image_canvas = Canvas(review, bd="3", bg="#d9d9df")
    image_canvas.place(relx=.02, rely=.15, relheight = 550/700, relwidth=1140/1200, anchor=tk.NW)

    # image Canvas Scrolling Function
    image_canvas.yview_moveto(0)
    image_canvas.xview_moveto(0)

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

    image_canvas.delete("all")
    image_canvas.config(scrollregion=[0, 0, 0, max(len(final_images), len(raw_images)) * (height + height_pad + height_pad) + 16])

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
    image_x_pos.append(first_image_position + (width + width_pad) * (group_len+1) + width_pad * 3)

    if bool(raw_images):
        for i in range(len(raw_images)):
            displayed = i + 1
            group_str = "Group " + str(i + 1)
            image_canvas.create_text(52, 30 + (height + height_pad * 2) * i, text=group_str)

            # label = Label(image_canvas, text="Ignore Raws")
            # label.bind("<Button-1>", lambda event, index=i: remove_raws(index))
            # image_canvas.create_window(52, 80 + (height + height_pad * 2) * i, window=label)

            image_canvas.create_line(0, (height + height_pad * 2) + (i * (height + height_pad * 2)), image_canvas.winfo_width(),
                                       (height + height_pad * 2) + (i * (height + height_pad * 2)))
            group_images = raw_images[i]

            for j in range(len(raw_images[i])):
                label = Label(image_canvas, image=group_images[j])
                x_pos = image_x_pos[group_len - len(group_images) + j]
                y_pos = i * (height + height_pad * 2) + int(height / 2) + height_pad
                image_canvas.create_window(x_pos, y_pos, window=label)

        line_x = image_x_pos[len(image_x_pos) - 2] + width / 2 + width_pad * 2
        image_canvas.create_line(line_x, 0, line_x, max(len(final_images), len(raw_images)) * (height + height_pad + height_pad) + 16, width=3)


    if bool(final_images):
        for i in range(len(final_images)):
            final_label = Label(image_canvas, image = final_images[i])
            image_canvas.create_window(image_x_pos[len(image_x_pos)-1],
                                       i * (height + height_pad * 2) + int(height / 2) + height_pad,
                                       window = final_label)


    if message: display_message()

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
    global message
    global raw_images
    global final_images
    global start_time
    global folder_path

    if raw_images and final_images and folder_path and start_time:
        log(os.getlogin(), start_time, datetime.now(),folder_path)
    else:
        print("An error occurred")

    raw_images = list()
    final_images = list()
    message = ""

    folder_path = filedialog.askdirectory()



    #check if folder was selected
    if not bool(folder_path):
        return

    # check if folder is hidden
    if bool(os.stat(folder_path).st_file_attributes & 2):
        print("Hidden!")
        return

    raws_folder = ''
    finals_folder = ''

    for subfolder in os.listdir(folder_path):
        if subfolder in ["Raws", "Raw", "raws", "raw"]:
            raws_folder = subfolder
        elif subfolder in ["Finals", "Final", "finals", "final", "Edited", "edited"]:
            finals_folder = subfolder

    if raws_folder and finals_folder:
        # raws_path = os.path.join(folder_path, raws_folder)
        raw_image_names = [f for f in os.listdir(os.path.join(folder_path, raws_folder)) if f.upper().endswith(".DNG")]
        final_image_names = [f for f in os.listdir(os.path.join(folder_path, finals_folder)) if f.upper().endswith((".JPG", ".JPEG"))]
        note_files = [f for f in os.listdir(os.path.join(folder_path, raws_folder)) if f.upper().endswith(".TXT")]
        # print(note_files)

        if raw_image_names:
            message = fill_raws(raw_image_names, os.path.join(folder_path, raws_folder))
        else:
            try:
                for raws_subfolder in os.listdir(os.path.join(folder_path, raws_folder)):
                    try:
                        raw_image_names = [f for f in os.listdir(os.path.join(folder_path, raws_folder, raws_subfolder)) if f.upper().endswith(".DNG")]
                    except NotADirectoryError:
                        continue
                    # raws_path = os.path.join(folder_path, raws_folder, raws_subfolder)
                    note_files = [os.path.join(raws_subfolder, f) for f in os.listdir(os.path.join(folder_path, raws_folder, raws_subfolder)) if f.upper().endswith(".TXT")]
                    # print(note_files)
                    if raw_image_names:
                        # print(raw_image_names)
                        message = fill_raws(raw_image_names, os.path.join(folder_path, raws_folder, raws_subfolder))
                        break
                    else:
                        message = "Raws folder must contain dng files. "
            except NotADirectoryError:
                message = "Raws folder must contain dng files. "

        if final_image_names:
            if raw_image_names:
                sorted_final_image_names = sort_finals(raw_image_names, final_image_names)
                print("Raws updated")
            message = fill_finals(sorted_final_image_names, os.path.join(folder_path, finals_folder))
        else:
            try:
                finals_subfolder = os.listdir(os.path.join(folder_path, finals_folder))[0]
                final_image_names = [f for f in os.listdir(os.path.join(folder_path, finals_folder, finals_subfolder)) if f.upper().endswith((".JPG", ".JPEG"))]
                if final_image_names:
                    if raw_image_names:
                        sorted_final_image_names = sort_finals(raw_image_names, final_image_names)
                    message = fill_finals(sorted_final_image_names, os.path.join(folder_path, finals_folder, finals_subfolder))
                else:
                    message = "Finals folder must contain jpg files. "
            except NotADirectoryError:
                message = "Finals folder must contain jpg files. "

        #Display notes in tab
        if note_files: # and not message:
            for note in note_files:
                note_text = open(os.path.join(folder_path, raws_folder, note), "r")
                note_string = note_text.read()
                note_label = Label(notes, text=note_string, font=("Gadugi", 10), pady=15, background="#a9a9af")
                note_label.pack()
        else:
            note_label = Label(notes, text="No Notes", font=("Gadugi", 10))
            note_label.pack()

    else:
        message = 'Folder must contain "Raws" and "Finals" subfolders.'

    if raw_images and final_images:
        start_time = datetime.now()

    display_images()

def is_raws(image_names):
    for file_name in image_names:
        group_num = file_name[0:file_name.find('-')]
        try:
            group_num = int(group_num)
        except ValueError:
            return False
    return True

def remove_raws(index):
    global message
    global raw_images
    del raw_images[index]
    message = "Some groups are missing finals"
    # display_images()

def fill_raws(raw_names, folder_path):
    global raw_images
    raw_images = list()

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
    final_images = list()

    for file_name in final_names:
        image = Image.open(os.path.join(folder_path, file_name))
        image = image.resize((width, height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        final_images.append(image)

    return ""


def sort_finals(raws_param, finals_param):
    raws_2d = list()
    sorted_finals = list()

    for raw in raws_param:
        group_num = int(raw[:raw.find('-')])
        if len(raws_2d) < group_num:
            for i in range(len(raws_2d), group_num):
                raws_2d.append(list())

        raws_2d[group_num - 1].append(raw)

    removed = 0
    for raw_group in raws_2d:
        added = False
        for raw in raw_group:
            name = raw[raw.find('-') + 1:-4]
            for final in finals_param:
                if name in final:
                    sorted_finals.append(final)
                    added = True
                    break
            if added: break
        if not added:
            print("raw group is missing finals")
            remove_raws(int(raw_group[0][:raw_group[0].find('-')]) - removed - 1)
            removed += 1
            # for raw in raw_group:
            #     raws_param.remove(raw)

    return sorted_finals

# import pandas as pd

def log(name, start_time_param, end_time_param, file_folder):
    try:
        # Establish a connection to the PostgreSQL database
        password = quote_plus('postgresAloh0mor@')
        engine = create_engine(f'postgresql://postgres:{password}@localhost/inuahub')
        conn = engine.connect()

        # Create a DataFrame from the log data
        columns = ['name', 'time_opened', 'time_finished_review', 'file_folder']
        data = [[name, start_time_param, end_time_param, file_folder]]
        df = pd.DataFrame(data, columns=columns)

        # Write the DataFrame to the PostgreSQL database
        df.to_sql('logs', conn, if_exists='append', index=False, method='multi', chunksize=1000)

        # Close the database connection
        conn.close()

        print("Data logged successfully.")

    except Exception as e:
        print(f"An error occurred while logging the data: {e}")


def display_message():
    global message
    alert = Tk()
    message_label = Label(alert, text=message, font=("Gadugi", 12), padx=20, pady=10, background="#d9d9df")
    message_label.pack()
    button = Button(alert, text = "Close", command = lambda: alert.destroy())
    button.pack()

def on_exit():
    if raw_images and final_images and folder_path and start_time:
        log(os.getlogin(), start_time, datetime.now(), folder_path)
    else:
        print("An error occurred")

#global variables
image_size_mult = 1.5
height = int(170 * image_size_mult)
width = int(264 * image_size_mult)
height_pad = 5
width_pad = 5
global start_time
folder_path = ''


raw_images = list()
final_images = list()
message = ""    #'Select an editor\'s folder. Folder should contain "Raws" and "Finals" subfolders. '
root = Tk()

atexit.register(on_exit)

open_review()