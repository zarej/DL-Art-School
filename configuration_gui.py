import tkinter as tk
import os
import sys
import sysconfig
import subprocess
from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fd
import json
from tkinter import messagebox
from PIL import Image, ImageTk,ImageOps,ImageDraw
import glob
#import converters
import shutil
from datetime import datetime
import pyperclip
import random
import customtkinter as ctk
import random
import subprocess
from pathlib import Path
import ast
from ruamel.yaml import YAML
yaml = YAML()
yaml.preserve_quotes = True
yaml.preserve_implicit = True
yaml.boolean_representation = ['false', 'true']
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
#work in progress code, not finished, credits will be added at a later date.

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        #parent of the widget
        #hack to get the master of the app
        
        self.parent = widget.winfo_toplevel()
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 50
        y += self.widget.winfo_rooty() + 50
        # creates a toplevel window
        self.tw = ctk.CTkToplevel(self.widget)
        #self.tw.wm_attributes("-topmost", 1)
        #self.parent.wm_attributes("-topmost", 0)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        #top most 
        
        label = ctk.CTkLabel(self.tw, text=self.text, justify='left',
                       wraplength = self.wraplength)
        label.pack(padx=10, pady=10 )

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class App(ctk.CTk):    
    def __init__(self):
        super().__init__()
        try:
            latest_git_hash = subprocess.check_output(["git", "ls-remote", "https://github.com/152334H/DL-Art-School.git","main"], cwd=Path(__file__).resolve().parent).strip().decode()[0:7]
            #check if configs folder exists
            print("Latest git hash: " + latest_git_hash)
        except:
            pass
        if not os.path.exists("configs"):
            os.makedirs("configs")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.geometry(f"{670}x{620}")
        #self.stableTune_icon =PhotoImage(master=self,file = "resources/stableTuner_icon.png")
        #self.iconphoto(False, self.stableTune_icon)
        self.dark_mode_var = "#1e2124"
        self.dark_purple_mode_var = "#1B0F1B"
        self.dark_mode_title_var = "#7289da"
        self.dark_mode_button_pressed_var = "#BB91B6"
        self.dark_mode_button_var = "#8ea0e1"
        self.dark_mode_text_var = "#c6c7c8"
        self.title("DLAS")
        self.configure(cursor="left_ptr")
        #resizable window
        self.resizable(True, True)
        self.create_default_variables()
        #check if stableTuner.cfg exists
        if not os.path.exists("configs/DLAS_hash.cfg"):
            #create stableTuner.cfg and write the latest git hash
            with open("configs/DLAS_hash.cfg", "w") as f:
                f.write(latest_git_hash)
        else:
            #read stableTuner.cfg
            with open("configs/DLAS_hash.cfg", "r") as f:
                old_git_hash = f.read()
            try:
                #check if the latest git hash is the same as the one in stableTuner.cfg
                if latest_git_hash != old_git_hash:
                    #if not the same, delete the old stableTuner.cfg and create a new one with the latest git hash
                    self.update_available = True
            except:
                self.update_available = False
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")
        #self.logo_img = ctk.CTkImage(Image.open("resources/stableTuner_logo.png").resize((300, 300), Image.Resampling.LANCZOS),size=(80,80))
        #self.logo_img = ctk.CTkLabel(self.sidebar_frame, image=self.logo_img, text='', height=50,width=50, font=ctk.CTkFont(size=15, weight="bold"))
        #self.logo_img.grid(row=0, column=0, padx=20, pady=20)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DLAS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=0, pady=10)
        self.empty_label = ctk.CTkLabel(self.sidebar_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.empty_label.grid(row=1, column=0, padx=0, pady=0)
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame,text='Common Settings',command=self.general_nav_button_event)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=5)
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame,text='Advanced Settings',command=self.training_nav_button_event)
        self.sidebar_button_2.grid(row=3, column=0, padx=20, pady=5)
        #empty label
        self.empty_label = ctk.CTkLabel(self.sidebar_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.empty_label.grid(row=9, column=0, padx=0, pady=0)
        #empty label
        
        if self.update_available:
            self.sidebar_button_11 = ctk.CTkButton(self.sidebar_frame,text='Update Available',fg_color='red',hover_color='darkred',command=self.update_DLAS)
            self.sidebar_button_11.grid(row=12, column=0, padx=20, pady=5)
        else:
            self.empty_label = ctk.CTkLabel(self.sidebar_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
            self.empty_label.grid(row=10, column=0, padx=0, pady=0)
            #empty label
            self.empty_label = ctk.CTkLabel(self.sidebar_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
            self.empty_label.grid(row=11, column=0, padx=0, pady=0)
        #self.sidebar_button_11 = ctk.CTkButton(self.sidebar_frame,text='Caption Buddy',command=self.caption_buddy)
        #self.sidebar_button_11.grid(row=13, column=0, padx=20, pady=5)
        self.sidebar_button_12 = ctk.CTkButton(self.sidebar_frame,text='Start Training!', command=lambda : self.process_inputs(export=False))
        self.sidebar_button_12.bind("<Button-3>", self.create_right_click_menu_export)
        self.sidebar_button_12.grid(row=14, column=0, padx=20, pady=5)
        self.general_frame = ctk.CTkFrame(self, width=140, corner_radius=0,fg_color='transparent')
        self.general_frame.grid_columnconfigure(0, weight=10)
        #self.general_frame.grid_columnconfigure(1, weight=10)
        self.general_frame_subframe = ctk.CTkScrollableFrame(self.general_frame,width=150,height=500, corner_radius=20)
        self.general_frame_subframe.grid(row=2, column=0,sticky="nsew", padx=20, pady=20)
        #self.general_frame_subframe_side_guide = ctk.CTkFrame(self.general_frame,width=250, corner_radius=20)
        #self.general_frame_subframe_side_guide.grid(row=2, column=1,sticky="nsew", padx=20, pady=20)
        self.create_general_settings_widgets()   
        self.apply_general_style_to_widgets(self.general_frame_subframe)
        #self.override_general_style_widgets()
        self.advanced_settings_frame = ctk.CTkFrame(self, width=400, corner_radius=0,fg_color='transparent')
        self.advanced_settings_frame.grid_columnconfigure(0, weight=1)
        self.advanced_settings_frame_subframe = ctk.CTkFrame(self.advanced_settings_frame,width=400, corner_radius=20)
        self.advanced_settings_frame_subframe.grid_columnconfigure(0, weight=1)
        self.advanced_settings_frame_subframe.grid_columnconfigure(1, weight=1)
        self.advanced_settings_frame_subframe.grid(row=2, column=0,sticky="nsew", padx=20, pady=20)
        self.create_advanced_settings_widgets()
        #self.grid_train_settings()
        self.apply_general_style_to_widgets(self.advanced_settings_frame_subframe)
        self.override_training_style_widgets()

        

        self.select_frame_by_name('general') 
        self.update()
        
        if os.path.exists("DLAS_last_run.json"):
            try:
                self.load_config(file_name="DLAS_last_run.json")
                #try loading the latest generated model to playground entry
                self.find_latest_generated_model(self.play_model_entry)
                #convert to ckpt if option is wanted
                if self.execute_post_conversion == True:
                    #construct unique name
                    epoch = self.play_model_entry.get().split(os.sep)[-1]
                    name_of_model = self.play_model_entry.get().split(os.sep)[-2]
                    res = self.resolution_var.get()
                    #time and date
                    #format time and date to %month%day%hour%minute
                    now = datetime.now()
                    dt_string = now.strftime("%m-%d-%H-%M")
                    #construct name
                    name = name_of_model+'_'+res+"_e"+epoch+"_"+dt_string
                    #print(self.play_model_entry.get())
                    #if self.play_model_entry.get() is a directory and all required folders exist
                    if os.path.isdir(self.play_model_entry.get()) and all([os.path.exists(os.path.join(self.play_model_entry.get(), folder)) for folder in self.required_folders]):
                        #print("all folders exist")
                        self.convert_to_ckpt(model_path=self.play_model_entry.get(), output_path=self.output_path_entry.get(),name=name)

                    #self.convert_to_ckpt(model_path=self.play_model_entry.get(), output_path=self.output_path_entry.get(),name=name)
                    #open DLAS_last_run.json and change convert_to_ckpt_after_training to False
                    with open("DLAS_last_run.json", "r") as f:
                        data = json.load(f)
                    data["execute_post_conversion"] = False
                    with open("DLAS_last_run.json", "w") as f:
                        json.dump(data, f, indent=4)
            except Exception as e:
                print(e)
                pass
        else:
            pass

    def create_default_variables(self):
        self.base_config_path = './codes/utils/BASE_gpt.yaml'
        with open(self.base_config_path, 'r') as stream:
            self.base_config = yaml.load(stream)
        print(self.base_config['name'])
        #common variables first
        self.project_name = ''
        self.gpu_ids = '[0]'
        self.enable_checkpointing = True
        self.use_fp16 = False
        self.use_wandb = False
        self.use_tb_logger = True

        #common dataset variables
        self.train_batch_size = 128
        self.valid_batch_size = 128
        self.path_to_lj_dataset = ''

        #common training variables
        self.iterations_number = 50000
        self.warmup_steps = -1
        self.gradient_accumlation = 4
        self.learning_rate = '1e-5'
        self.learning_rate_steps = '[500, 1000, 1400, 1800]'

        #common logger variables
        self.print_status_frequency = 100
        self.save_checkpoint_frequency = 500
        self.visual_debug_rate = 500

        #advanced common variables
        self.model = 'extensibletrainer'
        self.scale = 1
        self.start_step = -1

        #advanced common dataset variables
        self.train_num_workers = 8
        self.valid_num_workers = 1
        self.path_to_ar_model = '../experiments/autoregressive.pth'
        self.path_to_dvae_model = '../experiments/dvae.pth'

        #configurator variables
        self.update_available = False
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.sidebar_button_1.configure(fg_color=("gray75", "gray25") if name == "general" else "transparent")
        self.sidebar_button_2.configure(fg_color=("gray75", "gray25") if name == "training" else "transparent")

        # show selected frame
        if name == "general":
            self.general_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.general_frame.grid_forget()
        if name == "training":
            self.advanced_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.advanced_settings_frame.grid_forget()

    def general_nav_button_event(self):
        self.select_frame_by_name("general")

    def training_nav_button_event(self):
        self.select_frame_by_name("training")


    #create a right click menu for entry widgets
    def create_right_click_menu(self, event):
        #create a menu
        self.menu = Menu(self.master, tearoff=0)
        self.menu.config(font=("Segoe UI", 15))

        #set dark colors for the menu
        self.menu.configure(bg="#2d2d2d", fg="#ffffff", activebackground="#2d2d2d", activeforeground="#ffffff")
        #add commands to the menu
        self.menu.add_command(label="Cut", command=lambda: self.focus_get().event_generate("<<Cut>>"))
        self.menu.add_command(label="Copy", command=lambda: self.focus_get().event_generate("<<Copy>>"))
        self.menu.add_command(label="Paste", command=lambda: self.focus_get().event_generate("<<Paste>>"))
        self.menu.add_command(label="Select All", command=lambda: self.focus_get().event_generate("<<SelectAll>>"))
        #display the menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            #make sure to release the grab (Tk 8.0a1 only)
            self.menu.grab_release()
    def create_right_click_menu_export(self, event):
        #create a menu
        self.menu = Menu(self.master, tearoff=0)
        #set menu size and font size
        self.menu.config(font=("Segoe UI", 15))

        #set dark colors for the menu
        self.menu.configure(bg="#2d2d2d", fg="#ffffff", activebackground="#2d2d2d", activeforeground="#ffffff")
        #add commands to the menu
        self.menu.add_command(label="Export Trainer Command for Windows", command=lambda: self.process_inputs(export='Win'))
        self.menu.add_command(label="Copy Trainer Command for Linux", command=lambda: self.process_inputs(export='LinuxCMD'))
        #display the menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            #make sure to release the grab (Tk 8.0a1 only)
            self.menu.grab_release()
    def create_left_click_menu_config(self, event):
        #create a menu
        self.menu = Menu(self.master, tearoff=0)
        #set menu size and font size
        self.menu.config(font=("Segoe UI", 15))

        #set dark colors for the menu
        self.menu.configure(bg="#2d2d2d", fg="#ffffff", activebackground="#2d2d2d", activeforeground="#ffffff")
        #add commands to the menu
        self.menu.add_command(label="Load Config", command=self.load_config)
        self.menu.add_command(label="Save Config", command=self.save_config)
        #display the menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            #make sure to release the grab (Tk 8.0a1 only)
            self.menu.grab_release()
    def override_training_style_widgets(self):
        for i in self.advanced_settings_frame_subframe.children.values():
            if 'ctkbutton' in str(i):
                i.grid(padx=5, pady=5,sticky="w")
            if 'ctkoptionmenu' in str(i):
                i.grid(padx=10, pady=5,sticky="w")
            if 'ctkentry' in str(i):
                i.configure(width=160)
                i.grid(padx=10, pady=5,sticky="w")
                i.bind("<Button-3>", self.create_right_click_menu)
            if 'ctkswitch' in str(i):
                i.configure(text='')
                i.grid(padx=10, pady=5,sticky="")
            if 'ctklabel' in str(i):
                i.grid(padx=10, pady=5,sticky="w")

    def apply_general_style_to_widgets(self,frame):
        for i in frame.children.values():
            if 'ctkbutton' in str(i):
                i.grid(padx=10, pady=10,sticky="w")
            if 'ctkoptionmenu' in str(i):
                i.grid(padx=10, pady=10,sticky="w")
            if 'ctkentry' in str(i):
                i.configure(width=160)
                i.grid(padx=10, pady=5,sticky="w")
                i.bind("<Button-3>", self.create_right_click_menu)
            if 'ctkswitch' in str(i):
                i.configure(text='')
                i.grid(padx=10, pady=10,sticky="")
            if 'ctklabel' in str(i):
                i.grid(padx=10,sticky="w")

    def grid_train_settings(self):
        #define grid row and column
        self.advanced_settings_frame_subframe.grid_columnconfigure(0, weight=2)
        self.advanced_settings_frame_subframe.grid_columnconfigure(1, weight=1)
        self.advanced_settings_frame_subframe.grid_columnconfigure(2, weight=2)
        self.advanced_settings_frame_subframe.grid_columnconfigure(3, weight=1)
        
        rows = 12
        columns = 4
        widgets = self.advanced_settings_frame_subframe.children.values()
        #organize widgets in grid
        curRow = 0
        curColumn = 0
        #make widgets a list
        widgets = list(widgets)[1:]
        #find ctkcanvas in widgets and remove it
        for i in widgets:
            if 'ctkcanvas' in str(i):
                widgets.remove(i)
        #create pairs of widgets
        pairs = []
        for i in range(0,len(widgets),2):
            pairs.append([widgets[i],widgets[i+1]])
        for p in pairs:
            p[0].grid(row=curRow, column=curColumn, sticky="w",padx=1,pady=1)
            p[1].grid(row=curRow, column=curColumn+1, sticky="w",padx=1,pady=1)
            curRow += 1
            if curRow == rows:
                curRow = 0
                curColumn += 2
    def calculate_batch_sizes(self,entry):
        pass
    def create_general_settings_widgets(self):


        self.general_frame_title = ctk.CTkLabel(self.general_frame, text="Common Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.general_frame_title.grid(row=0, column=0,columnspan=2, padx=20, pady=20)    
        #self.tip_label = ctk.CTkLabel(self.general_frame, text="Tip: Hover over settings for information",  font=ctk.CTkFont(size=14))
        #self.tip_label.grid(row=1, column=0, sticky="nsew")

        self.load_config_button = ctk.CTkButton(self.general_frame_subframe, text="Load/Save Config")
        #bind the load config button to a function
        self.load_config_button.bind("<Button-1>", lambda event: self.create_left_click_menu_config(event))
        self.load_config_button.grid(row=0, column=0, sticky="nsew")
        #create project name label
        self.project_name_label = ctk.CTkLabel(self.general_frame_subframe, text="Project Name")
        project_name_label_ttp = CreateToolTip(self.project_name_label, "The name of the project. This will be used to name the output folder.")
        self.project_name_label.grid(row=1, column=0, sticky="nsew")
        self.project_name_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.project_name_entry.grid(row=1, column=1, sticky="nsew")
        self.project_name_entry.insert(0, self.project_name)
        #create gpu ids label
        self.gpu_ids_label = ctk.CTkLabel(self.general_frame_subframe, text="GPU IDs")
        gpu_ids_label_ttp = CreateToolTip(self.gpu_ids_label, "The GPU IDs to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs, you can specify which ones to use. If you have a single CPU, you can specify which one to use. If you have no CPUs, you can specify which GPU to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs, you can specify which ones to use. If you have a single CPU, you can specify which one to use. If you have no CPUs, you can specify which GPU to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs, you can specify which ones to use. If you have a single CPU, you can specify which one to use. If you have no CPUs, you can specify which GPU to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs, you can specify which ones to use. If you have a single CPU, you can specify which one to use. If you have no CPUs, you can specify which GPU to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs, you can specify which ones to use. If you have a single CPU, you can specify which one to use. If you have no CPUs, you can specify which GPU to use. If you have multiple GPUs, you can specify which ones to use. If you have a single GPU, you can specify which one to use. If you have no GPUs, you can specify which CPU to use. If you have multiple CPUs")
        self.gpu_ids_label.grid(row=2, column=0, sticky="nsew")
        self.gpu_ids_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.gpu_ids_entry.grid(row=2, column=1, sticky="nsew")
        self.gpu_ids_entry.insert(0, self.gpu_ids)
        #create enable checkpointing label
        self.enable_checkpointing_label = ctk.CTkLabel(self.general_frame_subframe, text="Enable Checkpointing")
        enable_checkpointing_label_ttp = CreateToolTip(self.enable_checkpointing_label, "Enable checkpointing. If enabled, the model will be saved after every epoch.")
        self.enable_checkpointing_label.grid(row=3, column=0, sticky="nsew")
        #create enable checkpointing checkbox
        self.enable_checkpointing_var = tk.IntVar()
        self.enable_checkpointing_checkbox = ctk.CTkSwitch(self.general_frame_subframe,variable=self.enable_checkpointing_var)
        self.enable_checkpointing_checkbox.grid(row=3, column=1, sticky="nsew")
        self.enable_checkpointing_var.set(self.enable_checkpointing)
        #create use fp16 checkbox
        self.use_fp16_label = ctk.CTkLabel(self.general_frame_subframe, text="Use FP16")
        use_fp16_label_ttp = CreateToolTip(self.use_fp16_label, "Use FP16. If enabled, the model will be trained using FP16.")
        self.use_fp16_label.grid(row=4, column=0, sticky="nsew")
        #create use fp16 checkbox
        self.use_fp16_var = tk.IntVar()
        self.use_fp16_checkbox = ctk.CTkSwitch(self.general_frame_subframe,variable=self.use_fp16_var)
        self.use_fp16_checkbox.grid(row=4, column=1, sticky="nsew")
        self.use_fp16_var.set(self.use_fp16)
        #create use wandb checkbox
        self.use_wandb_label = ctk.CTkLabel(self.general_frame_subframe, text="Use WandB")
        use_wandb_label_ttp = CreateToolTip(self.use_wandb_label, "Use WandB. If enabled, the model will be logged to WandB.")
        self.use_wandb_label.grid(row=5, column=0, sticky="nsew")
        #create use wandb checkbox
        self.use_wandb_var = tk.IntVar()
        self.use_wandb_checkbox = ctk.CTkSwitch(self.general_frame_subframe,variable=self.use_wandb_var)
        self.use_wandb_checkbox.grid(row=5, column=1, sticky="nsew")
        self.use_wandb_var.set(self.use_wandb)
        #create use tb logger checkbox
        self.use_tb_logger_label = ctk.CTkLabel(self.general_frame_subframe, text="Use TB Logger")
        use_tb_logger_label_ttp = CreateToolTip(self.use_tb_logger_label, "Use TB Logger. If enabled, the model will be logged to TensorBoard.")
        self.use_tb_logger_label.grid(row=6, column=0, sticky="nsew")
        #create use tb logger checkbox
        self.use_tb_logger_var = tk.IntVar()
        self.use_tb_logger_checkbox = ctk.CTkSwitch(self.general_frame_subframe,variable=self.use_tb_logger_var)
        self.use_tb_logger_checkbox.grid(row=6, column=1, sticky="nsew")
        self.use_tb_logger_var.set(self.use_tb_logger)

        #create a label in the middle: "Data"
        self.data_label = ctk.CTkLabel(self.general_frame_subframe, text="Data Settings",font=ctk.CTkFont(size=20, weight="bold"))
        self.data_label.grid(row=7, column=0, sticky="nsew",pady=10)
        #create dataset path label and entry
        self.dataset_path_label = ctk.CTkLabel(self.general_frame_subframe, text="Dataset Path")
        dataset_path_label_ttp = CreateToolTip(self.dataset_path_label, "The path to the dataset to use.")
        self.dataset_path_label.grid(row=8, column=0, sticky="nsew")
        self.dataset_path_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.dataset_path_entry.grid(row=8, column=1, sticky="nsew")
        self.dataset_path_entry.insert(0, self.path_to_lj_dataset)
        #create a button to select the dataset path next to the entry
        self.dataset_path_button = ctk.CTkButton(self.general_frame_subframe,width=10, text="...", command=lambda: self.open_file_dialog(self.dataset_path_entry))
        self.dataset_path_button.grid(row=8, column=2, sticky="nsew")
        
        #create train batch size label and entry
        self.train_batch_size_label = ctk.CTkLabel(self.general_frame_subframe, text="Train Batch Size")
        train_batch_size_label_ttp = CreateToolTip(self.train_batch_size_label, "The batch size to use for training.")
        self.train_batch_size_label.grid(row=9, column=0, sticky="nsew")
        self.train_batch_size_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.train_batch_size_entry.grid(row=9, column=1, sticky="nsew")
        self.train_batch_size_entry.insert(0, self.train_batch_size)
        #add a button to trigger calculation of the batch size
        self.train_batch_size_button = ctk.CTkButton(self.general_frame_subframe,width=10, text="A", command=lambda: self.calculate_batch_sizes(self.train_batch_size_entry))
        self.train_batch_size_button.grid(row=9, column=2, sticky="nsew")
        #create a validation batch size label and entry
        self.val_batch_size_label = ctk.CTkLabel(self.general_frame_subframe, text="Validation Batch Size")
        val_batch_size_label_ttp = CreateToolTip(self.val_batch_size_label, "The batch size to use for validation.")
        self.val_batch_size_label.grid(row=10, column=0, sticky="nsew")
        self.val_batch_size_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.val_batch_size_entry.grid(row=10, column=1, sticky="nsew")
        self.val_batch_size_entry.insert(0, self.valid_batch_size)
        #add a button to trigger calculation of the batch size
        self.val_batch_size_button = ctk.CTkButton(self.general_frame_subframe,width=10, text="A", command=lambda: self.calculate_batch_sizes(self.val_batch_size_entry))
        self.val_batch_size_button.grid(row=10, column=2, sticky="nsew")
        #create a training bold label
        self.training_label = ctk.CTkLabel(self.general_frame_subframe, text="Training Settings",font=ctk.CTkFont(size=20, weight="bold"))
        self.training_label.grid(row=11, column=0, sticky="nsew",pady=10)
        #create steps label and entry
        self.steps_label = ctk.CTkLabel(self.general_frame_subframe, text="Steps")
        steps_label_ttp = CreateToolTip(self.steps_label, "The number of steps to train for.")
        self.steps_label.grid(row=12, column=0, sticky="nsew")
        self.steps_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.steps_entry.grid(row=12, column=1, sticky="nsew")
        self.steps_entry.insert(0, self.iterations_number)
        #create warmup steps label and entry
        self.warmup_steps_label = ctk.CTkLabel(self.general_frame_subframe, text="Warmup Steps")
        warmup_steps_label_ttp = CreateToolTip(self.warmup_steps_label, "The number of warmup steps to use.")
        self.warmup_steps_label.grid(row=13, column=0, sticky="nsew")
        self.warmup_steps_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.warmup_steps_entry.grid(row=13, column=1, sticky="nsew")
        self.warmup_steps_entry.insert(0, self.warmup_steps)
        #create gradient accumulation steps label and entry
        self.gradient_accumulation_steps_label = ctk.CTkLabel(self.general_frame_subframe, text="Gradient Accumulation Steps")
        gradient_accumulation_steps_label_ttp = CreateToolTip(self.gradient_accumulation_steps_label, "The number of gradient accumulation steps to use.")
        self.gradient_accumulation_steps_label.grid(row=14, column=0, sticky="nsew")
        self.gradient_accumulation_steps_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.gradient_accumulation_steps_entry.grid(row=14, column=1, sticky="nsew")
        self.gradient_accumulation_steps_entry.insert(0, self.gradient_accumlation)
        #create learning rate label and entry
        self.learning_rate_label = ctk.CTkLabel(self.general_frame_subframe, text="Learning Rate")
        learning_rate_label_ttp = CreateToolTip(self.learning_rate_label, "The learning rate to use.")
        self.learning_rate_label.grid(row=15, column=0, sticky="nsew")
        self.learning_rate_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.learning_rate_entry.grid(row=15, column=1, sticky="nsew")
        self.learning_rate_entry.insert(0, self.learning_rate)
        #create learning rate steps
        self.learning_rate_steps_label = ctk.CTkLabel(self.general_frame_subframe, text="Learning Rate Steps")
        learning_rate_steps_label_ttp = CreateToolTip(self.learning_rate_steps_label, "The learning rate to use.")
        self.learning_rate_steps_label.grid(row=16, column=0, sticky="nsew")
        self.learning_rate_steps_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.learning_rate_steps_entry.grid(row=16, column=1, sticky="nsew")
        self.learning_rate_steps_entry.insert(0, self.learning_rate_steps)
        #create bold logger label
        self.logger_label = ctk.CTkLabel(self.general_frame_subframe, text="Logger Settings",font=ctk.CTkFont(size=20, weight="bold"))
        self.logger_label.grid(row=17, column=0, sticky="nsew",pady=10)
        #create print status frequency label and entry
        self.print_status_frequency_label = ctk.CTkLabel(self.general_frame_subframe, text="Print Status Frequency")
        print_status_frequency_label_ttp = CreateToolTip(self.print_status_frequency_label, "The frequency to print the status of the training.")
        self.print_status_frequency_label.grid(row=18, column=0, sticky="nsew")
        self.print_status_frequency_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.print_status_frequency_entry.grid(row=18, column=1, sticky="nsew")
        self.print_status_frequency_entry.insert(0, self.print_status_frequency)
        #create save frequency label and entry
        self.save_frequency_label = ctk.CTkLabel(self.general_frame_subframe, text="Save Checkpoint Frequency")
        save_frequency_label_ttp = CreateToolTip(self.save_frequency_label, "The frequency to save the model.")
        self.save_frequency_label.grid(row=19, column=0, sticky="nsew")
        self.save_frequency_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.save_frequency_entry.grid(row=19, column=1, sticky="nsew")
        self.save_frequency_entry.insert(0, self.save_checkpoint_frequency)
        #create visual debug frequency label and entry
        self.visual_debug_rate_label = ctk.CTkLabel(self.general_frame_subframe, text="Visual Debug Frequency")
        visual_debug_rate_label_ttp = CreateToolTip(self.visual_debug_rate_label, "The frequency to save the visual debug images.")
        self.visual_debug_rate_label.grid(row=20, column=0, sticky="nsew")
        self.visual_debug_rate_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.visual_debug_rate_entry.grid(row=20, column=1, sticky="nsew")
        self.visual_debug_rate_entry.insert(0, self.visual_debug_rate)

        
        '''
        self.vae_model_path_label = ctk.CTkLabel(self.general_frame_subframe, text="VAE model path / HuggingFace Repo")
        vae_model_path_label_ttp = CreateToolTip(self.vae_model_path_label, "OPTINAL The path to the VAE model to use. Can be a local path or a HuggingFace repo path.")
        self.vae_model_path_label.grid(row=2, column=0, sticky="nsew")
        self.vae_model_path_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.vae_model_path_entry.grid(row=2, column=1, sticky="nsew")
        self.vae_model_path_entry.insert(0, self.vae_model_path)
        #make a button to open a file dialog
        self.vae_model_path_button = ctk.CTkButton(self.general_frame_subframe,width=30, text="...", command=lambda: self.open_file_dialog(self.vae_model_path_entry))
        self.vae_model_path_button.grid(row=2, column=2, sticky="w")

        self.output_path_label = ctk.CTkLabel(self.general_frame_subframe, text="Output Path")
        output_path_label_ttp = CreateToolTip(self.output_path_label, "The path to the output directory. If it doesn't exist, it will be created.")
        self.output_path_label.grid(row=3, column=0, sticky="nsew")
        self.output_path_entry = ctk.CTkEntry(self.general_frame_subframe)
        self.output_path_entry.grid(row=3, column=1, sticky="nsew")
        self.output_path_entry.insert(0, self.output_path)
        #make a button to open a file dialog
        self.output_path_button = ctk.CTkButton(self.general_frame_subframe,width=30, text="...", command=lambda: self.open_file_dialog(self.output_path_entry))
        self.output_path_button.grid(row=3, column=2, sticky="w")

        self.convert_to_ckpt_after_training_label = ctk.CTkLabel(self.general_frame_subframe, text="Convert to CKPT after training?")
        convert_to_ckpt_label_ttp = CreateToolTip(self.convert_to_ckpt_after_training_label, "Convert the model to a tensorflow checkpoint after training.")
        self.convert_to_ckpt_after_training_label.grid(row=4, column=0, sticky="nsew")
        self.convert_to_ckpt_after_training_var = tk.IntVar()
        self.convert_to_ckpt_after_training_checkbox = ctk.CTkSwitch(self.general_frame_subframe,text='',variable=self.convert_to_ckpt_after_training_var)
        self.convert_to_ckpt_after_training_checkbox.grid(row=4, column=1, sticky="nsew",padx=10)
        
        #use telegram updates dark mode
        self.send_telegram_updates_label = ctk.CTkLabel(self.general_frame_subframe, text="Send Telegram Updates")
        send_telegram_updates_label_ttp = CreateToolTip(self.send_telegram_updates_label, "Use Telegram updates to monitor training progress, must have a Telegram bot set up.")
        self.send_telegram_updates_label.grid(row=6, column=0, sticky="nsew")
        #create checkbox to toggle telegram updates and show telegram token and chat id
        #create telegram token dark mode
        self.telegram_token_label = ctk.CTkLabel(self.general_frame_subframe, text="Telegram Token",  state="disabled")
        telegram_token_label_ttp = CreateToolTip(self.telegram_token_label, "The Telegram token for your bot.")
        self.telegram_token_label.grid(row=7, column=0, sticky="nsew")
        self.telegram_token_entry = ctk.CTkEntry(self.general_frame_subframe,  state="disabled")
        self.telegram_token_entry.grid(row=7, column=1,columnspan=3, sticky="nsew")
        self.telegram_token_entry.insert(0, self.telegram_token)
        #create telegram chat id dark mode
        self.telegram_chat_id_label = ctk.CTkLabel(self.general_frame_subframe, text="Telegram Chat ID",  state="disabled")
        telegram_chat_id_label_ttp = CreateToolTip(self.telegram_chat_id_label, "The Telegram chat ID to send updates to.")
        self.telegram_chat_id_label.grid(row=8, column=0, sticky="nsew")
        self.telegram_chat_id_entry = ctk.CTkEntry(self.general_frame_subframe,  state="disabled")
        self.telegram_chat_id_entry.grid(row=8, column=1,columnspan=3, sticky="nsew")
        self.telegram_chat_id_entry.insert(0, self.telegram_chat_id)
        
        #add a switch to toggle runpod mode
        self.cloud_mode_label = ctk.CTkLabel(self.general_frame_subframe, text="Cloud Training Export")
        cloud_mode_label_ttp = CreateToolTip(self.cloud_mode_label, "Cloud mode will package up a quick trainer session for RunPod/Colab etc.")
        self.cloud_mode_label.grid(row=9, column=0, sticky="nsew")
        self.cloud_mode_var = tk.IntVar()
        self.cloud_mode_checkbox = ctk.CTkSwitch(self.general_frame_subframe,variable=self.cloud_mode_var, command=self.toggle_runpod_mode)
        self.cloud_mode_checkbox.grid(row=9, column=1, sticky="nsew")
    '''
    def toggle_runpod_mode(self):
        toggle = self.cloud_mode_var.get()
        #flip self.toggle
        if toggle == True:
            toggle = False
            self.sidebar_button_12.configure(text='Export for Cloud!')
        else:
            toggle = True
            self.sidebar_button_12.configure(text='Start Training!')
        
    
    def create_advanced_settings_widgets(self):
        self.advanced_settings_frame_title = ctk.CTkLabel(self.advanced_settings_frame, text="Advanced Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.advanced_settings_frame_title.grid(row=0, column=0, padx=20, pady=20)  

        #create label and entry to model type
        self.model_type_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Model Type")
        model_type_label_ttp = CreateToolTip(self.model_type_label, "The model type you're training.")
        self.model_type_label.grid(row=0, column=0, sticky="nsew")
        #create entry to model type
        self.model_type_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.model_type_entry.grid(row=0, column=1, sticky="nsew")
        self.model_type_entry.insert(0, self.model)
        #create scale label and entry
        self.scale_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Scale")
        scale_label_ttp = CreateToolTip(self.scale_label, "The scale of the model.")
        self.scale_label.grid(row=1, column=0, sticky="nsew")
        self.scale_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.scale_entry.grid(row=1, column=1, sticky="nsew")
        self.scale_entry.insert(0, self.scale)
        #create start step label and entry
        self.start_step_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Start Step")
        start_step_label_ttp = CreateToolTip(self.start_step_label, "The step to start training from.")
        self.start_step_label.grid(row=2, column=0, sticky="nsew")
        self.start_step_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.start_step_entry.grid(row=2, column=1, sticky="nsew")
        self.start_step_entry.insert(0, self.start_step)
        #create bold title dataset
        self.dataset_title = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Dataset", font=ctk.CTkFont(size=15, weight="bold"))
        self.dataset_title.grid(row=3, column=0, sticky="nsew")
        #create training workers label and entry
        self.training_workers_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Training Workers")
        training_workers_label_ttp = CreateToolTip(self.training_workers_label, "The number of workers to use for training.")
        self.training_workers_label.grid(row=4, column=0, sticky="nsew")
        self.training_workers_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.training_workers_entry.grid(row=4, column=1, sticky="nsew")
        self.training_workers_entry.insert(0, self.train_num_workers)
        #create validation workers label and entry
        self.validation_workers_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Validation Workers")
        validation_workers_label_ttp = CreateToolTip(self.validation_workers_label, "The number of workers to use for validation.")
        self.validation_workers_label.grid(row=5, column=0, sticky="nsew")
        self.validation_workers_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.validation_workers_entry.grid(row=5, column=1, sticky="nsew")
        self.validation_workers_entry.insert(0, self.valid_num_workers)
        #create path to ar model
        self.ar_model_path_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Path to AR Model")
        ar_model_path_label_ttp = CreateToolTip(self.ar_model_path_label, "The path to the AR model.")
        self.ar_model_path_label.grid(row=6, column=0, sticky="nsew")
        self.ar_model_path_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.ar_model_path_entry.grid(row=6, column=1, sticky="nsew")
        self.ar_model_path_entry.insert(0, self.path_to_ar_model)
        #create path to dvae model
        #self.dvae_model_path_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Path to DVAE Model")
        #dvae_model_path_label_ttp = CreateToolTip(self.dvae_model_path_label, "The path to the DVAE model.")
        #self.dvae_model_path_label.grid(row=7, column=0, sticky="nsew")
        #self.dvae_model_path_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        #self.dvae_model_path_entry.grid(row=7, column=1, sticky="nsew")
        #self.dvae_model_path_entry.insert(0, self.path_to_dvae_model)

        '''
        #add a model variant dropdown
        self.model_variant_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Model Variant")
        model_variant_label_ttp = CreateToolTip(self.model_variant_label, "The model type you're training.")
        self.model_variant_label.grid(row=0, column=0, sticky="nsew")
        self.model_variant_var = tk.StringVar()
        self.model_variant_var.set(self.model_variant)
        self.model_variant_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, values=self.model_variants, variable=self.model_variant_var)
        #add attention optionMenu
        self.attention_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Attention")
        attention_label_ttp = CreateToolTip(self.attention_label, "The attention type to use. Flash Attention may enable lower VRAM training but Xformers will be faster and better for bigger batch sizes.")
        self.attention_label.grid(row=1, column=0, sticky="nsew")
        self.attention_var = tk.StringVar()
        self.attention_var.set(self.attention)
        self.attention_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, values=self.attention_types, variable=self.attention_var)
        #add a batch size entry

        #add a seed entry
        self.seed_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Seed")
        seed_label_ttp = CreateToolTip(self.seed_label, "The seed to use for training.")
        #self.seed_label.grid(row=1, column=0, sticky="nsew")
        self.seed_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        #self.seed_entry.grid(row=1, column=1, sticky="nsew")
        self.seed_entry.insert(0, self.seed_number)
        #create resolution dark mode dropdown
        self.resolution_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Resolution")
        resolution_label_ttp = CreateToolTip(self.resolution_label, "The resolution of the images to train on.")
        #self.resolution_label.grid(row=2, column=0, sticky="nsew")
        self.resolution_var = tk.StringVar()
        self.resolution_var.set(self.resolution)
        self.resolution_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, variable=self.resolution_var, values=self.possible_resolutions)
        #self.resolution_dropdown.grid(row=2, column=1, sticky="nsew")
        
        #create train batch size dark mode dropdown with values from 1 to 60
        self.train_batch_size_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Train Batch Size")
        train_batch_size_label_ttp = CreateToolTip(self.train_batch_size_label, "The batch size to use for training.")
        #self.train_batch_size_label.grid(row=3, column=0, sticky="nsew")
        self.train_batch_size_var = tk.StringVar()
        self.train_batch_size_var.set(self.batch_size)
        #make a list of values from 1 to 60 that are strings
        #train_batch_size_values = 
        self.train_batch_size_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, variable=self.train_batch_size_var, values=[str(i) for i in range(1,61)])
        #self.train_batch_size_dropdown.grid(row=3, column=1, sticky="nsew")

        #create train epochs dark mode 
        self.train_epochs_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Train Epochs")
        train_epochs_label_ttp = CreateToolTip(self.train_epochs_label, "The number of epochs to train for. An epoch is one pass through the entire dataset.")
        #self.train_epochs_label.grid(row=4, column=0, sticky="nsew")
        self.train_epochs_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        #self.train_epochs_entry.grid(row=4, column=1, sticky="nsew")
        self.train_epochs_entry.insert(0, self.num_train_epochs)
        
        #create mixed precision dark mode dropdown
        self.mixed_precision_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Mixed Precision")
        mixed_precision_label_ttp = CreateToolTip(self.mixed_precision_label, "Use mixed precision training to speed up training, FP16 is recommended but requires a GPU with Tensor Cores. TF32 is recommended for RTX 30 series GPUs and newer.")
        #self.mixed_precision_label.grid(row=5, column=0, sticky="nsew")
        self.mixed_precision_var = tk.StringVar()
        self.mixed_precision_var.set(self.mixed_precision)
        self.mixed_precision_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, variable=self.mixed_precision_var,values=["bf16","fp16","fp32","tf32"])
        #self.mixed_precision_dropdown.grid(row=5, column=1, sticky="nsew")

        #create use 8bit adam checkbox
        self.use_8bit_adam_var = tk.IntVar()
        self.use_8bit_adam_var.set(self.use_8bit_adam)
        #create label
        self.use_8bit_adam_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Use 8bit Adam")
        use_8bit_adam_label_ttp = CreateToolTip(self.use_8bit_adam_label, "Use 8bit Adam to speed up training, requires bytsandbytes.")
        #self.use_8bit_adam_label.grid(row=6, column=0, sticky="nsew")
        #create checkbox
        self.use_8bit_adam_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.use_8bit_adam_var,text='')
        #self.use_8bit_adam_checkbox.grid(row=6, column=1, sticky="nsew")
        #create use gradient checkpointing checkbox
        self.use_gradient_checkpointing_var = tk.IntVar()
        self.use_gradient_checkpointing_var.set(self.use_gradient_checkpointing)
        #create label
        self.use_gradient_checkpointing_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Use Gradient Checkpointing")
        use_gradient_checkpointing_label_ttp = CreateToolTip(self.use_gradient_checkpointing_label, "Use gradient checkpointing to reduce RAM usage.")
        #self.use_gradient_checkpointing_label.grid(row=7, column=0, sticky="nsew")
        #create checkbox
        self.use_gradient_checkpointing_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.use_gradient_checkpointing_var)
        #self.use_gradient_checkpointing_checkbox.grid(row=7, column=1, sticky="nsew")
        #create gradient accumulation steps dark mode dropdown with values from 1 to 60
        self.gradient_accumulation_steps_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Gradient Accumulation Steps")
        gradient_accumulation_steps_label_ttp = CreateToolTip(self.gradient_accumulation_steps_label, "The number of gradient accumulation steps to use, this is useful for training with limited GPU memory.")
        #self.gradient_accumulation_steps_label.grid(row=8, column=0, sticky="nsew")
        self.gradient_accumulation_steps_var = tk.StringVar()
        self.gradient_accumulation_steps_var.set(self.accumulation_steps)
        self.gradient_accumulation_steps_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, variable=self.gradient_accumulation_steps_var, values=['1','2','3','4','5','6','7','8','9','10'])
        #self.gradient_accumulation_steps_dropdown.grid(row=8, column=1, sticky="nsew")
        #create learning rate dark mode entry
        self.learning_rate_steps_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Learning Rate")
        learning_rate_steps_label_ttp = CreateToolTip(self.learning_rate_steps_label, "The learning rate to use for training.")
        #self.learning_rate_steps_label.grid(row=9, column=0, sticky="nsew")
        self.learning_rate_steps_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        #self.learning_rate_steps_entry.grid(row=9, column=1, sticky="nsew")
        self.learning_rate_steps_entry.insert(0, self.learning_rate)
        #create learning rate scheduler dropdown
        self.learning_rate_scheduler_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Learning Rate Scheduler")
        learning_rate_scheduler_label_ttp = CreateToolTip(self.learning_rate_scheduler_label, "The learning rate scheduler to use for training.")
        #self.learning_rate_scheduler_label.grid(row=10, column=0, sticky="nsew")
        self.learning_rate_scheduler_var = tk.StringVar()
        self.learning_rate_scheduler_var.set(self.learning_rate_schedule)
        self.learning_rate_scheduler_dropdown = ctk.CTkOptionMenu(self.advanced_settings_frame_subframe, variable=self.learning_rate_scheduler_var, values=["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"])
        #self.learning_rate_scheduler_dropdown.grid(row=10, column=1, sticky="nsew")
        #create num warmup steps dark mode entry
        self.num_warmup_steps_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="LR Warmup Steps")
        num_warmup_steps_label_ttp = CreateToolTip(self.num_warmup_steps_label, "The number of warmup steps to use for the learning rate scheduler.")
        #self.num_warmup_steps_label.grid(row=11, column=0, sticky="nsew")
        self.num_warmup_steps_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        #self.num_warmup_steps_entry.grid(row=11, column=1, sticky="nsew")
        self.num_warmup_steps_entry.insert(0, self.learning_rate_warmup_steps)
        #create use latent cache checkbox
        #self.use_latent_cache_var = tk.IntVar()
        #self.use_latent_cache_var.set(self.do_not_use_latents_cache)
        #create label
        #self.use_latent_cache_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Use Latent Cache")
        #use_latent_cache_label_ttp = CreateToolTip(self.use_latent_cache_label, "Cache the latents to speed up training.")
        #self.use_latent_cache_label.grid(row=12, column=0, sticky="nsew")
        #create checkbox
        #self.use_latent_cache_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.use_latent_cache_var)
        #self.use_latent_cache_checkbox.grid(row=12, column=1, sticky="nsew")
        #create save latent cache checkbox
        #self.save_latent_cache_var = tk.IntVar()
        #self.save_latent_cache_var.set(self.save_latents_cache)
        #create label
        #self.save_latent_cache_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Save Latent Cache")
        #save_latent_cache_label_ttp = CreateToolTip(self.save_latent_cache_label, "Save the latents cache to disk after generation, will be remade if batch size changes.")
        #self.save_latent_cache_label.grid(row=13, column=0, sticky="nsew")
        #create checkbox
        #self.save_latent_cache_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.save_latent_cache_var)
        #self.save_latent_cache_checkbox.grid(row=13, column=1, sticky="nsew")
        #create regnerate latent cache checkbox
        self.regenerate_latent_cache_var = tk.IntVar()
        self.regenerate_latent_cache_var.set(self.regenerate_latents_cache)
        #create label
        self.regenerate_latent_cache_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Regenerate Latent Cache")
        regenerate_latent_cache_label_ttp = CreateToolTip(self.regenerate_latent_cache_label, "Force the latents cache to be regenerated.")
        #self.regenerate_latent_cache_label.grid(row=14, column=0, sticky="nsew")
        #create checkbox
        self.regenerate_latent_cache_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.regenerate_latent_cache_var)
        #self.regenerate_latent_cache_checkbox.grid(row=14, column=1, sticky="nsew")
        #create train text encoder checkbox
        self.train_text_encoder_var = tk.IntVar()
        self.train_text_encoder_var.set(self.train_text_encoder)
        #create label
        self.train_text_encoder_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Train Text Encoder")
        train_text_encoder_label_ttp = CreateToolTip(self.train_text_encoder_label, "Train the text encoder along with the UNET.")
        #self.train_text_encoder_label.grid(row=15, column=0, sticky="nsew")
        #create checkbox
        self.train_text_encoder_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.train_text_encoder_var)
        #self.train_text_encoder_checkbox.grid(row=15, column=1, sticky="nsew")
        #create limit text encoder encoder entry
        self.clip_penultimate_var = tk.IntVar()
        self.clip_penultimate_var.set(self.clip_penultimate)
        #create label
        self.clip_penultimate_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Clip Penultimate")
        clip_penultimate_label_ttp = CreateToolTip(self.clip_penultimate_label, "Train using the Penultimate layer of the text encoder.")
        #create checkbox
        self.clip_penultimate_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.clip_penultimate_var)
        

        self.limit_text_encoder_var = tk.StringVar()
        self.limit_text_encoder_var.set(self.limit_text_encoder)
        #create label
        self.limit_text_encoder_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Limit Text Encoder")
        limit_text_encoder_label_ttp = CreateToolTip(self.limit_text_encoder_label, "Stop training the text encoder after this many epochs, use % to train for a percentage of the total epochs.")
        #self.limit_text_encoder_label.grid(row=16, column=0, sticky="nsew")
        #create entry
        self.limit_text_encoder_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe, textvariable=self.limit_text_encoder_var)
        #self.limit_text_encoder_entry.grid(row=16, column=1, sticky="nsew")
        
        #create checkbox disable cudnn benchmark
        self.disable_cudnn_benchmark_var = tk.IntVar()
        self.disable_cudnn_benchmark_var.set(self.disable_cudnn_benchmark)
        #create label for checkbox
        self.disable_cudnn_benchmark_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="EXPERIMENTAL: Disable cuDNN Benchmark")
        disable_cudnn_benchmark_label_ttp = CreateToolTip(self.disable_cudnn_benchmark_label, "Disable cuDNN benchmarking, may offer 2x performance on some systems and stop OOM errors.")
        #self.disable_cudnn_benchmark_label.grid(row=17, column=0, sticky="nsew")
        #create checkbox
        self.disable_cudnn_benchmark_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.disable_cudnn_benchmark_var)
        #self.disable_cudnn_benchmark_checkbox.grid(row=17, column=1, sticky="nsew")
        #add conditional dropout entry
        self.conditional_dropout_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Conditional Dropout")
        conditional_dropout_label_ttp = CreateToolTip(self.conditional_dropout_label, "Precentage of probability to drop out a caption token to train the model to be more robust to missing words.")
        self.conditional_dropout_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.conditional_dropout_entry.insert(0, self.conditional_dropout)
        #create use EMA switch
        self.use_ema_var = tk.IntVar()
        self.use_ema_var.set(self.use_ema)
        #create label
        self.use_ema_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Use EMA")
        use_ema_label_ttp = CreateToolTip(self.use_ema_label, "Use Exponential Moving Average to smooth the training paramaters. Will increase VRAM usage.")
        #self.use_ema_label.grid(row=18, column=0, sticky="nsew")
        #create checkbox
        self.use_ema_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.use_ema_var)

        #create with prior loss preservation checkbox
        self.with_prior_loss_preservation_var = tk.IntVar()
        self.with_prior_loss_preservation_var.set(self.with_prior_reservation)
        #create label
        self.with_prior_loss_preservation_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="With Prior Loss Preservation")
        with_prior_loss_preservation_label_ttp = CreateToolTip(self.with_prior_loss_preservation_label, "Use the prior loss preservation method. part of Dreambooth.")
        self.with_prior_loss_preservation_label.grid(row=19, column=0, sticky="nsew")
        #create checkbox
        self.with_prior_loss_preservation_checkbox = ctk.CTkSwitch(self.advanced_settings_frame_subframe, variable=self.with_prior_loss_preservation_var)
        self.with_prior_loss_preservation_checkbox.grid(row=19, column=1, sticky="nsew")
        #create prior loss preservation weight entry
        self.prior_loss_preservation_weight_label = ctk.CTkLabel(self.advanced_settings_frame_subframe, text="Weight")
        prior_loss_preservation_weight_label_ttp = CreateToolTip(self.prior_loss_preservation_weight_label, "The weight of the prior loss preservation loss.")
        self.prior_loss_preservation_weight_label.grid(row=19, column=1, sticky="e")
        self.prior_loss_preservation_weight_entry = ctk.CTkEntry(self.advanced_settings_frame_subframe)
        self.prior_loss_preservation_weight_entry.grid(row=19, column=3, sticky="w")
        self.prior_loss_preservation_weight_entry.insert(0, self.prior_loss_weight)
        '''

    def update_DLAS(self):
        #git
        new_version = subprocess.check_output(["git", "ls-remote", "https://github.com/152334H/DL-Art-School.git","main"], cwd=Path(__file__).resolve().parent).strip().decode()[0:7]
        #open the DLAS_hash.cfg file
        #update the DLAS_hash.cfg file
        with open("configs/DLAS_hash.cfg", "w") as f:
            f.write(new_version)
        #update the stabletuner
        #self.update_DLASabletuner()
        #git pull and wait for it to finish
        subprocess.run(["git", "stash"], cwd=Path(__file__).resolve().parent)
        subprocess.run(["git", "pull"], cwd=Path(__file__).resolve().parent)
        print('pulled')
        #restart the app
        restart(self)
    def packageForCloud(self):
        #check if there's an export folder in the cwd and if not create one
        if not os.path.exists("exports"):
            os.mkdir("exports")
        exportDir = self.export_name
        if not os.path.exists("exports" + os.sep + exportDir):
            os.mkdir("exports" + os.sep + exportDir)
        else:
            #remove the old export folder
            shutil.rmtree("exports" + os.sep + exportDir)
            os.mkdir("exports" + os.sep + exportDir)
        self.full_export_path = "exports" + os.sep + exportDir
        os.mkdir(self.full_export_path + os.sep + 'output')
        os.mkdir(self.full_export_path + os.sep + 'datasets')

        #check if self.model_path is a directory
        if os.path.isdir(self.model_path):
            #get the directory name
            model_name = os.path.basename(self.model_path)
            #check if model_name can be an int
            try:
                model_name = int(model_name)
                #get the parent directory name
                model_name = os.path.basename(os.path.dirname(self.model_path))
            except:
                pass
            #create a folder in the export folder with the model name
            if not os.path.exists(self.full_export_path + os.sep + 'input_model'+ os.sep + model_name):
                os.mkdir(self.full_export_path + os.sep + 'input_model'+ os.sep + model_name)
            #copy the model to the export folder
            shutil.copytree(self.model_path, self.full_export_path + os.sep +'input_model'+ os.sep+ model_name + os.sep,dirs_exist_ok=True)
            self.model_path= 'input_model' + '/' + model_name
        if os.path.isdir(self.vae_path):
            #get the directory name
            vae_name = os.path.basename(self.vae_path)
            #create a folder in the export folder with the model name
            if not os.path.exists(self.full_export_path + os.sep + 'input_vae_model'+ os.sep + vae_name):
                os.mkdir(self.full_export_path + os.sep + 'input_vae_model'+ os.sep + vae_name)
            #copy the model to the export folder
            shutil.copytree(self.vae_path, self.full_export_path + os.sep +'input_vae_model'+ os.sep+ vae_name + os.sep + vae_name,dirs_exist_ok=True)
            self.vae_path= 'input_vae_model' + '/' + vae_name
        if self.output_path == '':
            self.output_path = 'output'
        else:
            #get the dirname
            output_name = os.path.basename(self.output_path)
            #create a folder in the export folder with the model name
            if not os.path.exists(self.full_export_path + os.sep + 'output'+ os.sep + output_name):
                os.mkdir(self.full_export_path + os.sep + 'output'+ os.sep + output_name)
            self.output_path = 'output' + '/' + output_name
        #loop through the concepts and add them to the export folder
        concept_counter = 0
        new_concepts = []
        for concept in self.concepts:
            concept_counter += 1
            concept_data_dir = os.path.basename(concept['instance_data_dir'])
            #concept is a dict
            #get the concept name
            concept_name = concept['instance_prompt']
            #if concept_name is ''
            if concept_name == '':
                concept_name = 'concept_' + str(concept_counter)
                
            #create a folder in the export/datasets folder with the concept name
            #if not os.path.exists(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_name):
            #    os.mkdir(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_name)
            #copy the concept to the export folder
            shutil.copytree(concept['instance_data_dir'], self.full_export_path + os.sep + 'datasets'+ os.sep + concept_data_dir ,dirs_exist_ok=True)
            concept_class_name = concept['class_prompt']
            if concept_class_name == '':
                #if class_data_dir is ''
                if concept['class_data_dir'] != '':
                    concept_class_name = 'class_' + str(concept_counter)
                    #create a folder in the export/datasets folder with the concept name
                    if not os.path.exists(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name):
                        os.mkdir(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name)
                    #copy the concept to the export folder
                    shutil.copytree(concept['class_data_dir'], self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name+ os.sep,dirs_exist_ok=True)
            else:
                if concept['class_data_dir'] != '':
                    #create a folder in the export/datasets folder with the concept name
                    if not os.path.exists(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name):
                        os.mkdir(self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name)
                    #copy the concept to the export folder
                    shutil.copytree(concept['class_data_dir'], self.full_export_path + os.sep + 'datasets'+ os.sep + concept_class_name+ os.sep,dirs_exist_ok=True)
            #create a new concept dict
            new_concept = {}
            new_concept['instance_prompt'] = concept_name
            new_concept['instance_data_dir'] = 'datasets' + '/' + concept_data_dir 
            new_concept['class_prompt'] = concept_class_name
            new_concept['class_data_dir'] = 'datasets' + '/' + concept_class_name if concept_class_name != '' else ''
            new_concept['do_not_balance'] = concept['do_not_balance']
            new_concept['use_sub_dirs'] = concept['use_sub_dirs']
            new_concepts.append(new_concept)
        #make scripts folder
        self.save_concept_to_json(filename=self.full_export_path + os.sep + 'stabletune_concept_list.json', preMadeConcepts=new_concepts)
        if not os.path.exists(self.full_export_path + os.sep + 'scripts'):
            os.mkdir(self.full_export_path + os.sep + 'scripts')
        #copy the scripts/trainer.py the scripts folder
        shutil.copy('scripts' + os.sep + 'trainer.py', self.full_export_path + os.sep + 'scripts' + os.sep + 'trainer.py')
        #copy trainer_utils.py to the scripts folder
        shutil.copy('scripts' + os.sep + 'trainer_util.py', self.full_export_path + os.sep + 'scripts' + os.sep + 'trainer_util.py')
        #copy converters.py to the scripts folder
        shutil.copy('scripts' + os.sep + 'converters.py', self.full_export_path + os.sep + 'scripts' + os.sep + 'converters.py')
        #copy model_util.py to the scripts folder
        shutil.copy('scripts' + os.sep + 'model_util.py', self.full_export_path + os.sep + 'scripts' + os.sep + 'model_util.py')
        #copy clip_seg to the scripts folder
        shutil.copy('scripts' + os.sep + 'clip_segmentation.py', self.full_export_path + os.sep + 'scripts' + os.sep + 'clip_segmentation.py')
    
    def aspect_ratio_mode_toggles(self, *args):
        if self.use_aspect_ratio_bucketing_var.get() == 1:
            self.with_prior_loss_preservation_var.set(0)
            self.with_prior_loss_preservation_checkbox.configure(state="disabled")
            self.aspect_ratio_bucketing_mode_label.configure(state="normal")
            self.aspect_ratio_bucketing_mode_option_menu.configure(state="normal")
            self.dynamic_bucketing_mode_label.configure(state="normal")
            self.dynamic_bucketing_mode_option_menu.configure(state="normal")
            

        else:
            self.with_prior_loss_preservation_checkbox.configure(state="normal")
            self.aspect_ratio_bucketing_mode_label.configure(state="disabled")
            self.aspect_ratio_bucketing_mode_option_menu.configure(state="disabled")
            self.dynamic_bucketing_mode_label.configure(state="disabled")
            self.dynamic_bucketing_mode_option_menu.configure(state="disabled")
            
    
    def open_file_dialog(self, entry):
        """Opens a file dialog and sets the entry to the selected file."""
        indexOfEntry = None
        file_path = fd.askdirectory()
        #get the entry name
        
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        #focus on the entry
        entry.focus_set()
        #unset the focus on the button
        #self.master.focus_set()

    def save_config(self, config_file=None):
        #save the configure file
        import json
        #create a dictionary of all the variables
        #ask the user for a file name
        if config_file == None:
            file_name = fd.asksaveasfilename(title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
            #check if json in file name
            if ".json" not in file_name:
                file_name += ".json"
        else:
            file_name = config_file
        configure = {}
        self.update_controlled_seed_sample()
        self.update_sample_prompts()
        self.update_concepts()
        configure["concepts"] = self.concepts
        #print(self.concepts)
        configure["sample_prompts"] = self.sample_prompts
        configure['add_controlled_seed_to_sample'] = self.add_controlled_seed_to_sample
        configure["model_path"] = self.input_model_path_entry.get()
        configure["vae_path"] = self.vae_model_path_entry.get()
        configure["output_path"] = self.output_path_entry.get()
        configure["send_telegram_updates"] = self.send_telegram_updates_var.get()
        configure["telegram_token"] = self.telegram_token_entry.get()
        configure["telegram_chat_id"] = self.telegram_chat_id_entry.get()
        configure["resolution"] = self.resolution_var.get()
        configure["batch_size"] = self.train_batch_size_var.get()
        configure["train_epocs"] = self.train_epochs_entry.get()
        configure["mixed_precision"] = self.mixed_precision_var.get()
        configure["use_8bit_adam"] = self.use_8bit_adam_var.get()
        configure["use_gradient_checkpointing"] = self.use_gradient_checkpointing_var.get()
        configure["accumulation_steps"] = self.gradient_accumulation_steps_var.get()
        configure["learning_rate"] = self.learning_rate_steps_entry.get()
        configure["warmup_steps"] = self.num_warmup_steps_entry.get()
        configure["learning_rate_scheduler"] = self.learning_rate_scheduler_var.get()
        #configure["use_latent_cache"] = self.use_latent_cache_var.get()
        #configure["save_latent_cache"] = self.save_latent_cache_var.get()
        configure["regenerate_latent_cache"] = self.regenerate_latent_cache_var.get()
        configure["train_text_encoder"] = self.train_text_encoder_var.get()
        configure["with_prior_loss_preservation"] = self.with_prior_loss_preservation_var.get()
        configure["prior_loss_preservation_weight"] = self.prior_loss_preservation_weight_entry.get()
        configure["use_image_names_as_captions"] = self.use_image_names_as_captions_var.get()
        configure["auto_balance_concept_datasets"] = self.auto_balance_dataset_var.get()
        configure["add_class_images_to_dataset"] = self.add_class_images_to_dataset_var.get()
        configure["number_of_class_images"] = self.number_of_class_images_entry.get()
        configure["save_every_n_epochs"] = self.save_every_n_epochs_entry.get()
        configure["number_of_samples_to_generate"] = self.number_of_samples_to_generate_entry.get()
        configure["sample_height"] = self.sample_height_entry.get()
        configure["sample_width"] = self.sample_width_entry.get()
        configure["sample_random_aspect_ratio"] = self.sample_random_aspect_ratio_var.get()
        configure['sample_on_training_start'] = self.sample_on_training_start_var.get()
        configure['concepts'] = self.concepts
        configure['aspect_ratio_bucketing'] = self.use_aspect_ratio_bucketing_var.get()
        configure['seed'] = self.seed_entry.get()
        configure['dataset_repeats'] = self.dataset_repeats_entry.get()
        configure['limit_text_encoder_training'] = self.limit_text_encoder_entry.get()
        configure['use_text_files_as_captions'] = self.use_text_files_as_captions_var.get()
        configure['ckpt_version'] = self.ckpt_sd_version
        configure['convert_to_ckpt_after_training'] = self.convert_to_ckpt_after_training_var.get()
        configure['execute_post_conversion'] = self.convert_to_ckpt_after_training_var.get()
        configure['disable_cudnn_benchmark'] = self.disable_cudnn_benchmark_var.get()
        configure['sample_step_interval'] = self.sample_step_interval_entry.get()
        configure['conditional_dropout'] = self.conditional_dropout_entry.get()
        configure["clip_penultimate"] = self.clip_penultimate_var.get()
        configure['use_ema'] = self.use_ema_var.get()
        configure['aspect_ratio_bucketing_mode'] = self.aspect_ratio_bucketing_mode_var.get()
        configure['dynamic_bucketing_mode'] = self.dynamic_bucketing_mode_var.get()
        configure['model_variant'] = self.model_variant_var.get()
        configure['masked_training'] = self.masked_training_var.get()
        configure['normalize_masked_area_loss'] = self.normalize_masked_area_loss_var.get()
        configure['unmasked_probability'] = self.unmasked_probability_var.get()
        configure['max_denoising_strength'] = self.max_denoising_strength_var.get()
        configure['fallback_mask_prompt'] = self.fallback_mask_prompt_entry.get()
        configure['attention'] = self.attention_var.get()
        configure['batch_prompt_sampling'] = int(self.batch_prompt_sampling_optionmenu_var.get())
        configure['shuffle_dataset_per_epoch'] = self.shuffle_dataset_per_epoch_var.get()
        #save the configure file
        #if the file exists, delete it
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, "w",encoding='utf-8') as f:
            json.dump(configure, f, indent=4)
            f.close()
    
    def load_config(self,file_name=None):
        #load the configure file
        #ask the user for a file name
        if file_name == None:
            file_name = fd.askopenfilename(title = "Select file",filetypes = (("yaml files","*.yml"),("all files","*.*")))
        if file_name == "":
            return
        #load the configure file
        with open(file_name, "r") as f:
            configure = yaml.load(f)
        
        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, configure["name"])
        self.gpu_ids_entry.delete(0, tk.END)
        self.gpu_ids_entry.insert(0, configure["gpu_ids"])
        self.enable_checkpointing_var.set(configure["checkpointing_enabled"])
        self.use_fp16_var.set(configure["fp16"])
        self.use_wandb_var.set(configure["wandb"])
        self.use_tb_logger_var.set(configure["use_tb_logger"])
        self.dataset_path_entry.delete(0, tk.END)
        self.dataset_path_entry.insert(0, configure["datasets"]['train']['path'].replace('train.txt',''))
        self.train_batch_size_entry.delete(0, tk.END)
        self.train_batch_size_entry.insert(0, str(configure["datasets"]['train']['batch_size']))
        self.val_batch_size_entry.delete(0, tk.END)
        self.val_batch_size_entry.insert(0, str(configure["datasets"]['val']['batch_size']))
        self.steps_entry.delete(0, tk.END)
        self.steps_entry.insert(0, str(configure["train"]['niter']))
        self.warmup_steps_entry.delete(0, tk.END)
        self.warmup_steps_entry.insert(0, str(configure["train"]['warmup_iter']))
        self.gradient_accumulation_steps_entry.delete(0, tk.END)
        self.gradient_accumulation_steps_entry.insert(0, str(configure["train"]['mega_batch_factor']))
        self.learning_rate_entry.delete(0, tk.END)
        self.learning_rate_entry.insert(0, str(configure["steps"]['gpt_train']['optimizer_params']['lr']))
        self.learning_rate_steps_entry.delete(0, tk.END)
        self.learning_rate_steps_entry.insert(0, str(configure["train"]['gen_lr_steps']))
        self.print_status_frequency_entry.delete(0, tk.END)
        self.print_status_frequency_entry.insert(0, str(configure["logger"]['print_freq']))
        self.save_frequency_entry.delete(0, tk.END)
        self.save_frequency_entry.insert(0, str(configure["logger"]['save_checkpoint_freq']))
        self.visual_debug_rate_entry.delete(0, tk.END)
        self.visual_debug_rate_entry.insert(0, str(configure["logger"]['visual_debug_rate']))

        self.model_type_entry.delete(0, tk.END)
        self.model_type_entry.insert(0, configure["model"])
        self.scale_entry.delete(0, tk.END)
        self.scale_entry.insert(0, str(configure["scale"]))
        self.start_step_entry.delete(0, tk.END)
        self.start_step_entry.insert(0, str(configure["start_step"]))
        self.training_workers_entry.delete(0, tk.END)
        self.training_workers_entry.insert(0, str(configure["datasets"]['train']['n_workers']))
        self.validation_workers_entry.delete(0, tk.END)
        self.validation_workers_entry.insert(0, str(configure["datasets"]['val']['n_workers']))
        self.ar_model_path_entry.delete(0, tk.END)
        self.ar_model_path_entry.insert(0, configure["path"]["pretrain_model_gpt"])
        #self.dvae_model_path_entry.delete(0, tk.END)
        #self.dvae_model_path_entry.insert(0, configure["path"]["pretrain_model_dvae"])
        self.update()
    
    def process_inputs(self,export=None):
        #collect and process all the inputs
        self.project_name = self.project_name_entry.get().replace(' ', '_')
        self.gpu_ids = ast.literal_eval(self.gpu_ids_entry.get())
        self.enable_checkpointing_var = bool(self.enable_checkpointing_var.get())
        self.use_fp16 = bool(self.use_fp16_var.get())
        self.use_wandb = bool(self.use_wandb_var.get())
        self.use_tb_logger = bool(self.use_tb_logger_var.get())
        self.train_batch_size = int(self.train_batch_size_entry.get())
        self.valid_batch_size = int(self.val_batch_size_entry.get())
        self.path_to_lj_dataset = self.dataset_path_entry.get()
        self.path_to_train = os.path.join(self.path_to_lj_dataset, 'train.txt')
        self.path_to_valid = os.path.join(self.path_to_lj_dataset, 'valid.txt')
        self.iterations_number = int(self.steps_entry.get())
        self.warmup_steps = int(self.warmup_steps_entry.get())
        self.gradient_accumlation_steps = int(self.gradient_accumulation_steps_entry.get())
        self.learning_rate = self.learning_rate_entry.get()
        self.learning_rate_steps = ast.literal_eval(self.learning_rate_steps_entry.get())
        self.print_status_frequency = int(self.print_status_frequency_entry.get())
        self.save_frequency = int(self.save_frequency_entry.get())
        self.visual_debug_rate = int(self.visual_debug_rate_entry.get())
        self.model = self.model_type_entry.get()
        self.scale = int(self.scale_entry.get())
        self.start_step = int(self.start_step_entry.get())
        self.train_num_workers = int(self.training_workers_entry.get())
        self.valid_num_workers = int(self.validation_workers_entry.get())
        self.path_to_ar_model = self.ar_model_path_entry.get()
        #self.path_to_dvae_model = self.dvae_model_path_entry.get()
        
        self.base_config['name'] = self.project_name
        self.base_config['gpu_ids'] = 'gpu_ids_val'
        self.base_config['checkpointing_enabled'] = self.enable_checkpointing_var
        self.base_config['fp16'] = self.use_fp16
        self.base_config['wandb'] = self.use_wandb
        self.base_config['use_tb_logger'] = self.use_tb_logger

        #dataset settings
        self.base_config['datasets']['train']['name'] = self.project_name
        self.base_config['datasets']['train']['path'] = self.path_to_train
        self.base_config['datasets']['train']['batch_size'] = self.train_batch_size
        self.base_config['datasets']['train']['n_workers'] = self.train_num_workers
        self.base_config['datasets']['val']['name'] = self.project_name
        self.base_config['datasets']['val']['path'] = self.path_to_valid
        self.base_config['datasets']['val']['batch_size'] = self.valid_batch_size
        self.base_config['datasets']['val']['n_workers'] = self.valid_num_workers

        #path settings
        self.base_config['path']['pretrain_model_gpt'] = self.path_to_ar_model
        #train settings
        self.base_config['train']['niter'] = self.iterations_number
        self.base_config['train']['warmup_iter'] = self.warmup_steps
        self.base_config['train']['mega_batch_factor'] = self.gradient_accumlation_steps
        self.base_config['steps']['gpt_train']['optimizer_params']['lr'] = 'learning_rate_val'
        self.base_config['train']['gen_lr_steps'] = 'multi_step_lr_steps_val'
        #logger settings
        self.base_config['logger']['print_freq'] = self.print_status_frequency
        self.base_config['logger']['save_checkpoint_freq'] = self.save_frequency
        self.base_config['logger']['visual_debug_rate'] = self.visual_debug_rate
        #fix yaml
        # =TaggedString('!!float', str(self.base_config['steps']['gpt_train']['optimizer_params']['lr']))
        #save new config
        import numpy as np

        def format_float(num):
            return np.format_float_positional(num, trim='-')
        #self.base_config['steps']['gpt_train']['optimizer_params']['lr'] = '!!float '+format_float(self.base_config['steps']['gpt_train']['optimizer_params']['lr'])
        #self.base_config['steps']['gpt_train']['optimizer_params']['weight_decay'] = float("{:.8f}".format(self.base_config['steps']['gpt_train']['optimizer_params']['weight_decay']))
        with open('experiments/'+self.project_name+'_config.yaml', 'w') as f:
            yaml.dump(self.base_config, f)
        #fix yaml bullshit, rumel is not saving float and array values correctly
        with open('experiments/'+self.project_name+'_config.yaml', 'r') as f:
            data = f.read()
            data = data.replace('lr: ', 'lr: !!float ')
            data = data.replace('learning_rate_val', str(self.learning_rate))
            data = data.replace('weight_decay: ', 'weight_decay: !!float ')
            data = data.replace('gpu_ids_val', str(self.gpu_ids))
            data = data.replace('multi_step_lr_steps_val', str(self.learning_rate_steps))
            #write the fixed yaml to the config file
            with open('experiments/'+self.project_name+'_config.yaml', 'w') as f:
                f.write(data)
        quit()
        mode = 'normal'
        #leaving this for future cloud export
        '''
        if self.cloud_mode == False and export == None:
            #check if output path exists
            if os.path.exists(self.output_path) == True:
                #check if output path is empty
                if len(os.listdir(self.output_path)) > 0:
                    #show a messagebox asking if the user wants to overwrite the output path
                    overwrite = messagebox.askyesno("Overwrite Output Path", "The output path is not empty. Do you want to overwrite it?")
                    if overwrite == False:
                        return
                    else:
                        #delete the contents of the output path but the logs or 0 directory
                        for file in os.listdir(self.output_path):
                            if file != 'logs' and file != '0':
                                if os.path.isdir(self.output_path + '/' + file) == True:
                                    shutil.rmtree(self.output_path + '/' + file)
                                else:
                                    os.remove(self.output_path + '/' + file)

                        
        if self.cloud_mode == True or export == 'LinuxCMD':
            if export == 'LinuxCMD':
                mode = 'LinuxCMD'
            export='Linux'
            #create a sessionName for the cloud based on the output path name and the time
            #format time and date to %month%day%hour%minute
            now = datetime.now()
            dt_string = now.strftime("%m-%d-%H-%M")
            self.export_name = self.output_path.split('/')[-1].split('\\')[-1] + '_' + dt_string
            self.packageForCloud()
        '''
        
        self.save_config('DLAS_last_run.json')
        
        
        if export == False:
            #save the bat file
            with open("scripts/train.bat", "w", encoding="utf-8") as f:
                f.write(batBase)
            #close the window
            self.destroy()
            #run the bat file
            self.quit()
            train = os.system(r".\scripts\train.bat")
            #if exit code is 0, then the training was successful
            if train == 0:
                app = App()
                app.mainloop()
            #if user closed the window or keyboard interrupt, then cancel conversion
            elif train == 1:
                os.system("pause")
            
            #restart the app
        elif export == 'win':
            with open("train.bat", "w", encoding="utf-8") as f:
                f.write(batBase)
            #show message
            messagebox.showinfo("Export", "Exported to train.bat")
        elif mode == 'LinuxCMD':
            #copy batBase to clipboard
            trainer_index = batBase.find('trainer.py')+11
            batStart = batBase[:trainer_index]
            batCommands = batBase[trainer_index:]
            #split on -- and remove the first element
            batCommands = batCommands.split('--')
            batBase = batStart+' \\\n'
            for command in batCommands[1:]:
                #add the -- back
                if command != batCommands[-1]:
                    command = '  --'+command+'\\'+'\n'
                else:
                    command = '  --'+command
                batBase += command
            pyperclip.copy('!'+batBase)
            shutil.rmtree(self.full_export_path)
            messagebox.showinfo("Export", "Copied new training command to clipboard.")
            return
        elif export == 'Linux' and self.cloud_mode == True:
            notebook = 'resources/stableTuner_notebook.ipynb'
            #load the notebook as a dictionary
            with open(notebook) as f:
                nb = json.load(f)
            #get the last cell
            #find the cell with the source that contains changeMe
            #format batBase so it won't be one line
            #find index in batBase of the trainer.py
            trainer_index = batBase.find('trainer.py')+11
            batStart = batBase[:trainer_index]
            batCommands = batBase[trainer_index:]
            #split on -- and remove the first element
            batCommands = batCommands.split('--')
            batBase = batStart+' \\\n'
            for command in batCommands[1:]:
                #add the -- back
                if command != batCommands[-1]:
                    command = '  --'+command+'\\'+'\n'
                else:
                    command = '  --'+command
                batBase += command
            for i in range(len(nb['cells'])):
                if 'changeMe' in nb['cells'][i]['source']:
                    code_cell = nb['cells'][i]
                    index = i
                    code_cell['source'] = '!'+batBase
                    #replace the last cell with the new one
                    nb['cells'][index] = code_cell
                    break
            
            #save the notebook to the export folder
            shutil.copy('requirements.txt', self.full_export_path)
            #zip up everything in export without the folder itself
            shutil.make_archive('payload', 'zip', self.full_export_path)
            #move the zip file to the export folder
            shutil.move('payload.zip', self.full_export_path)
            #save the notebook to the export folder
            with open(self.full_export_path+os.sep+'stableTuner_notebook.ipynb', 'w') as f:
                json.dump(nb, f)
            #delete everything in the export folder except the zip file and the notebook
            for file in os.listdir(self.full_export_path):
                if file.endswith('.zip') or file.endswith('.ipynb'):
                    continue
                else:
                    #if it's a folder, delete it
                    if os.path.isdir(self.full_export_path+os.sep+file):
                        shutil.rmtree(self.full_export_path+os.sep+file)
                    #if it's a file, delete it
                    else:
                        os.remove(self.full_export_path+os.sep+file)
            #show message
            messagebox.showinfo("Success", f"Your cloud\linux payload is ready to go!\nSaved to: {self.full_export_path}\n\nUpload the files and run the notebook to start training.")
        



def restart(instance):
    instance.destroy()
    #os.startfile(os.getcwd()+'/scripts/configuration_gui.py')
    app = App()
    app.mainloop()
#root = ctk.CTk()
app = App()
app.mainloop()
