from tkinter import *
from tkinter import filedialog
import os
import numpy as np
import re
import sys
from PIL import Image, ImageTk

# Config
# sys.tracebacklimit = 0

colors = {
    "dark_blue": "#222831",
    "gray": "#ececec",
    "royal_blue": "#30475e",
    "orange": "#f2a365",
}


# Functions
def toggle_select_all_files():
    """
        ~Function called when 'select all' checkbox is  toggled
        ~ toggles the listbox items select all/deselect all

        @param--> None

        @return--> None(Modifies the listbox)

    """
    global CheckSelectAll

    if os.path.isdir(folder_path.get()):
        if file_listbox.size() > 0:
            Check_Button_label.configure(text="")
            if CheckSelectAll.get() == 0:
                file_listbox.selection_clear(0, END)

            elif CheckSelectAll.get() == 1:
                file_listbox.select_set(0, END)
        else:
            Check_Button_label.configure(
                text="No files found in the selected directory!"
            )
            Check_Button.deselect()
    else:
        Check_Button_label.configure(text="Please select a Directory first!")
        Check_Button.deselect()


def insert_into_listbox(folder_location):
    """
        ~Empty the present listbox  item  &
        ~Inserts all the files found in a specified folder in the listbox

        @param--> Directory path

        @return--> None(Modifies the listbox)

    """
    file_listbox.delete(0, END)
    Check_Button.deselect()
    sort_by.set(1)
    f_idx = 0
    if os.path.isdir(folder_location):
        for filee in os.listdir(folder_location):
            if os.path.isfile(os.path.join(folder_location, filee)):
                f_idx += 1

                file_listbox.insert(END, f"  {filee}  ")
                file_listbox.itemconfig(
                    END,
                    bg=colors["gray"] if f_idx % 2 == 0 else colors["orange"],
                    fg=colors["royal_blue"],
                )


def do_sort():
    """
        ~ Sort the listbox items according to the selcted Order

        @param---> None

        @return---> None(Modifies the listbox)
    """
    try:
        global folder_path, sort_by
        folder_location = folder_path.get()
        Radio_value = sort_by.get()
        file_details = []
        if os.path.isdir(folder_location):
            for filee in os.listdir(folder_location):
                file_fulpath = os.path.join(folder_location, filee)
                if os.path.isfile(file_fulpath):
                    time_creation = os.path.getctime(file_fulpath)
                    size = os.path.getsize(file_fulpath)
                    file_details.append([filee, time_creation, size])

        file_details = np.array(file_details)

        if Radio_value == 1:
            file_details = file_details[np.argsort(file_details[:, 0])]
        elif Radio_value == 2:
            file_details = file_details[np.argsort(file_details[:, 1])]
        elif Radio_value == 3:
            file_details = file_details[np.argsort(file_details[:, 2])]

        file_listbox.delete(0, END)
        for f_idx, f_details in enumerate(file_details):
            file_listbox.insert(END, f"  {f_details[0]}  ")
            file_listbox.itemconfig(
                END,
                bg=colors["gray"] if f_idx % 2 == 0 else colors["orange"],
                fg=colors["royal_blue"],
            )

    except IndexError as e:
        pass


def browseDIR():
    """
        ~ Browse a directory and calls 'insert_into_listbox' method.

        @param---> None

        @return---> None(Modifies the listbox)
    """
    global folder_path
    folder_path.set(filedialog.askdirectory())
    folder_location = folder_path.get()
    Folder_path_label.config(text=folder_location)

    insert_into_listbox(folder_location)


def find_pattern_rename(file_list,
                        directory,
                        pattern,
                        replacement,
                        isGUI,
                        searchby=3):
    """
        ~ Matches the specified pattern and rename selected files
          which are matching the pattern

        @param--->  List of the selected Files (list),
                    Directory Path where those files resides (str),
                    Specified Pattern (str),
                    Replacement String (str),
                    isGUI- a boolean variable (bool)
                    searchby value (int)

        @returns--->None (Renames Files)

    """
    compiled_pattern = re.compile(pattern)
    idx = 0
    if os.path.isdir(directory):
        for filee in (file_list):
            current_full_filepath = os.path.join(directory, filee)
            if os.path.isfile(current_full_filepath):
                file_name, file_ext = os.path.splitext(filee)

                if searchby == 3:
                    str_to_match = filee
                elif searchby == 2:
                    str_to_match = file_ext
                elif searchby == 1:
                    str_to_match = file_name
                else:
                    raise ValueError("Select a valid \"Search BY\" Option")
                    sys.exit()

                matching_pattern = compiled_pattern.search(str_to_match)
                if not matching_pattern:
                    continue
                try:

                    renamed = matching_pattern.expand(replacement)

                    if searchby == 3:
                        renamed += f"_{idx}{file_ext}"
                    elif searchby == 2:
                        renamed = f"{file_name}.{renamed}"
                    elif searchby == 1:
                        renamed = f"{renamed}_{idx}{file_ext}"

                    renamed_full = os.path.join(directory, renamed)
                except re.error:
                    continue

                if os.path.isfile(renamed_full):
                    print(f"Skipped! File named {renamed_full}"
                          " Already exists!")
                else:
                    idx += 1
                    os.rename(current_full_filepath, renamed_full)
    print(f"{idx} files renamed")
    if isGUI:
        insert_into_listbox(directory)


def doRename():
    """
        ~ Function that is being called when Rename Button is pressed in GUI
        ~ Collects required informations for Rename files such

        @param--->  None

        @returns--->None
        (Collects variable info and calls 'find_pattern_rename' function)
    """

    global folder_path, file_list, folder_path, pattern, replacement
    selected_idx = file_listbox.curselection()
    file_list = [file_listbox.get(x).strip() for x in selected_idx]
    Searching_pattern = pattern.get()
    Replacement_pattern = replacement.get()
    Directory = folder_path.get()
    if len(Replacement_pattern) > 0 and os.path.isdir(Directory):
        find_pattern_rename(file_list,
                            Directory,
                            Searching_pattern,
                            Replacement_pattern,
                            True,
                            search_by.get())


# Collecting system arguments
arguments = list(map(str, sys.argv[1:]))

# Logic that decides whether to run GUI based on arguments provided
# ~arg_list = [<directory path>, <Replace String>, <Searching regex Pattern>]
# ~if length of arg_list greater than zero then GUI will not appear
# ~if length of arg_list less than zero then raise Missing arg error

if len(arguments) > 0:
    if len(arguments) < 2:
        raise ValueError(
            'Missing Required arguments!'
            '\nCommand Format >> '
            'python GUI.py '
            '<Directory_Location> '
            '<Replace With> '
            '<Find Pattern(opt.)>')
        sys.exit()
    else:
        if not (os.path.isdir(arguments[0])):
            raise ValueError("Bad Directory in arguments")
            sys.exit()
        else:
            ldir = os.listdir(arguments[0])
            jpath = os.path.join(arguments[0], f)
            file_list = [f for f in ldir if os.path.isfile(jpath)]
            if len(arguments) == 3:
                find_pattern_rename(file_list,
                                    arguments[0],
                                    arguments[2],
                                    arguments[1],
                                    False)
            elif len(arguments) == 2:
                find_pattern_rename(file_list,
                                    arguments[0], "",
                                    arguments[1], False)
            else:
                raise ValueError("Error Occurred!")
                sys.exit()
else:
    # Running The GUI

    # GUI Preliminary Configuration
    root = Tk(className=" Bulk File Rename Tool")
    root.geometry("800x600")
    root.configure(bg=colors["dark_blue"])
    photo = Image.open(os.path.join(os.getcwd(), 'icon.jpg'))
    photo = ImageTk.PhotoImage(photo)
    root.iconphoto(False, photo)

    # Variables
    file_list = []
    CheckSelectAll = IntVar()
    sort_by = IntVar()
    search_by = IntVar()
    search_by.set(3)
    pattern = StringVar()
    replacement = StringVar()
    folder_path = StringVar()
    folder_path.set(f"{'-' * 20} No Directory Choosen {'-' * 20}")

    # Application Heading
    APP_NAME_LABEL = Label(
        root,
        fg=colors["orange"],
        bg=colors["dark_blue"],
        text="Bulk File Rename Tool",
        font=("calibre", 25, "bold"),
    )
    APP_NAME_LABEL.place(relx=0.5, rely=0.1, anchor=CENTER)

    # Frame containing 'pattern and replacement input'
    input_frame = Frame(root, bg=colors["dark_blue"])
    input_frame.place(relx=0.5, rely=0.2, anchor=CENTER)

    Pattern_label = Label(
        input_frame,
        bg=colors["dark_blue"],
        fg=colors["orange"],
        text="Find Pattern >>",
        font=("calibre", 10, "bold"),
    )

    Pattern = Entry(input_frame,
                    textvariable=pattern,
                    bg=colors['gray'],
                    font=("calibre", 10, "normal"),
                    highlightcolor=colors['orange'],
                    highlightthickness=2)

    Replacement_label = Label(
        input_frame,
        bg=colors["dark_blue"],
        fg=colors["orange"],
        text="Replacement >>",
        font=("calibre", 10, "bold"),
    )

    Replacement = Entry(input_frame,
                        textvariable=replacement,
                        bg=colors['gray'],
                        font=("calibre", 10, "normal"),
                        highlightcolor=colors['orange'],
                        highlightthickness=2)

    Redundant_label = Label(
        input_frame,
        bg=colors["dark_blue"],
        fg=colors["orange"],
        text="    |    ",
        font=("calibre", 16, "bold"),
    )

    Pattern_label.grid(row=0, column=0)
    Replacement_label.grid(row=0, column=3)
    Pattern.grid(row=0, column=1)
    Replacement.grid(row=0, column=4)
    Redundant_label.grid(row=0, column=2)

    # Frame containing ListBox, Scrollbars, Directory_Browser
    file_frame = Frame(root, bg=colors['dark_blue'], )
    file_frame.place(relx=0.5, rely=0.45, anchor=CENTER)

    # listbox
    file_listbox = Listbox(
        file_frame,
        selectmode="multiple",
        bg=colors["royal_blue"],
        borderwidth=5,
        width=100,
        highlightcolor=colors["orange"],
        relief=FLAT,

    )

    # Horizontal and Vertical Scrollbar
    file_scrollbary = Scrollbar(file_frame)
    file_scrollbarx = Scrollbar(file_frame, orient=HORIZONTAL)

    # Directory Browser Frame
    browse_dir = Frame(file_frame)

    Folder_path_label = Label(
        browse_dir,
        text=folder_path.get(),
        width=60,
        font=("calibre", 10, "bold"),
        bg=colors['gray']
    )
    button_explore = Button(browse_dir,
                            text="Browse Directory",
                            command=browseDIR,
                            bg=colors["orange"],
                            fg=colors["dark_blue"],
                            relief=FLAT,
                            padx=20,
                            font=("calibre", 9, "bold"),
                            activebackground=colors["dark_blue"],
                            activeforeground=colors["orange"])

    # placement of all the Widgets in the 'Frame' containing
    # 'ListBox, Scrollbars, Directory_Browser'
    browse_dir.pack(side=TOP, fill=BOTH, expand=False)
    file_scrollbarx.pack(side=BOTTOM, fill=X, expand=True)
    file_listbox.pack(side=LEFT, fill=BOTH, expand=True)
    file_scrollbary.pack(side=RIGHT, fill=BOTH, expand=True)

    # placement of the widgets in the browser frame
    Folder_path_label.pack(side=LEFT, expand=False)
    button_explore.pack(side=RIGHT, expand=False)

    # Configure/Attachment of Scrollbars with the Listbox
    file_scrollbary.config(command=file_listbox.yview)
    file_scrollbarx.config(command=file_listbox.xview)
    file_listbox.config(
        yscrollcommand=file_scrollbary.set,
        xscrollcommand=file_scrollbarx.set
    )

    # Frame for checkbox--> select all
    CheckBox_Frame = Frame(root, bg=colors["dark_blue"])
    CheckBox_Frame.place(relx=0.5, rely=0.7, anchor=CENTER)
    Check_Button = Checkbutton(
        CheckBox_Frame,
        bg=colors["dark_blue"],
        fg=colors["orange"],
        text="Select All Files",
        variable=CheckSelectAll,
        onvalue=1,
        offvalue=0,

        width=10,
        command=toggle_select_all_files,
    )
    Check_Button_label = Label(
        CheckBox_Frame,
        bg=colors["dark_blue"],
        fg="red",
        text="",
        font=("calibre", 10, "normal"),
    )
    Check_Button_label.grid(row=1, column=0)
    Check_Button.grid(row=0, column=0)

    # Frame for Search by Radios
    search_by_frame = Frame(root, bg=colors["dark_blue"])
    search_by_frame.place(relx=.5, rely=.75, anchor=CENTER)
    search_by_label = Label(
        search_by_frame,
        bg=colors["dark_blue"],
        fg=colors["gray"],
        text="Search In >>",
        font=("calibre", 10, "bold"),
    )
    search_by_label.grid(row=0, column=0)
    Radio = {"File Name Only": "1",
             "File Extension Only": "2",
             "Both": "3",
             }
    for (text, value) in Radio.items():
        Radiobutton(search_by_frame,
                    text=text,
                    variable=search_by,
                    value=value,
                    bg=colors["dark_blue"],
                    fg=colors["orange"]
                    ).grid(row=0, column=value)

    # Frame for Radio Button
    radio_frame = Frame(root, bg=colors["dark_blue"])
    radio_frame.place(relx=.5, rely=.79, anchor=CENTER)
    Radio_label = Label(
        radio_frame,
        bg=colors["dark_blue"],
        fg=colors["gray"],
        text="Sort By >>",
        font=("calibre", 10, "bold"),
    )
    Radio_label.grid(row=0, column=0)
    Radio = {"Alphabetical Order": "1",
             "Time Created": "2",
             "Size": "3",
             }
    for (text, value) in Radio.items():
        Radiobutton(radio_frame,
                    text=text,
                    variable=sort_by,
                    value=value,
                    bg=colors["dark_blue"],
                    fg=colors["orange"],
                    command=do_sort
                    ).grid(row=0, column=value)

    Step_text = "Step 1: Enter 'Find Pattern'   |"
    Step_text += "    Step 2: Enter 'Replace with'   |"
    Step_text += "   Step 3: Browse Directory & select files   |"
    Step_text += "    Step 4: Rename"
    Steps_label = Label(
        root,
        bg=colors["dark_blue"],
        fg=colors['gray'],
        text=Step_text,
        font=("calibre", 10, "normal"),
    )
    Steps_label.place(relx=0.5, rely=0.85, anchor=CENTER)

    # Rename Button
    Rename_btn = Button(
        root,
        text="Rename",
        command=doRename,
        padx=20,
        pady=5,
        font=("calibre", 12, "bold"),
        activebackground=colors["royal_blue"],
        activeforeground=colors["orange"],
        relief=FLAT,
        bg=colors["orange"],
        fg=colors["royal_blue"]
    ).place(relx=0.5, rely=0.93, anchor=CENTER)

    root.mainloop()
