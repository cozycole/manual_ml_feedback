import os
from PIL import Image, ImageTk
import tkinter as tk

class ManualClassifier:
    def __init__(self, shot_dir, class_dir, images=None, db_str=None, task_label=None):
        self.shot_dir = shot_dir
        self.class_dir = class_dir
        self.task_label = task_label
        self.db_str = db_str
        
        if images:
            self.images = images
        else:
            self.images = [f for f in os.listdir(self.shot_dir) if (f.endswith(".jpg") or f.endswith(".png"))]
        
            self.img_count = len(self.images)
        self.images.sort()
        self.window = tk.Tk()

        self.curr_img = None
        self.label = None
        self.curr_img_obj = None

        self.window.bind("<Up>", self.file_action_on_event)
        self.window.bind("<Down>", self.file_action_on_event)
        self.window.bind("<Right>", self.file_action_on_event)
        self.window.bind("<Left>", self.file_action_on_event)
        self.window.bind("<Left>", self.file_action_on_event)
        self.window.bind("<BackSpace>", self.file_action_on_event)

        self.class_dict = {
            "Up" : os.path.join(self.class_dir, "distress"),
            "Down" : os.path.join(self.class_dir, "slight_distress"),
            "Left" : os.path.join(self.class_dir, "unknown"),
            "Right" : os.path.join(self.class_dir, "no_distress"),
            "BackSpace" : os.path.join(self.class_dir, "trash")
        }
        # creates dirs if not already created
        self.check_class_dir()

    def start_classifier(self):
        try:
            self.curr_img = self.images.pop()
            if self.curr_img is None:
                raise IndexError
        except Exception:
            print(f"No images to show in {self.shot_dir}")
            self.window.destroy()
            return
        
        curr_img_path = os.path.join(self.shot_dir, self.curr_img)
        print(curr_img_path)
        img = Image.open(curr_img_path).convert("RGB")
        dimensions = (800, 800) if img.size[0] == img.size[1] else (1000,800)
        self.curr_img_obj = ImageTk.PhotoImage(img.resize(dimensions))
        self.label = tk.Label(self.window, image=self.curr_img_obj)
        self.label.pack()
        self.tk_task_label = tk.Label(self.window, text=self.task_label)
        self.tk_task_label.pack(side=tk.BOTTOM)
        self.window.mainloop()
            
    def file_action_on_event(self, event):
        try:
            # path of shot you were looking at
            curr_img_path = os.path.join(self.shot_dir, self.curr_img)
            # move to class dir based on key press
            to_path = os.path.join(self.class_dict[event.keysym], self.curr_img)
            print(f"Moving img from {curr_img_path} to {to_path}")
            os.rename(curr_img_path, to_path)
            
            new_img = self.images.pop()
            new_shot_img_path = os.path.join(self.shot_dir, new_img)
            img = Image.open(new_shot_img_path).convert("RGB")
            dimensions = (800, 800) if img.size[0] == img.size[1] else (1000,800)
            self.curr_img_obj = ImageTk.PhotoImage(img.resize(dimensions))
            self.label.configure(image=self.curr_img_obj)

            # don't entirely understand why, but you need
            # to create a reference to the curr_img_obj
            # otherwise it gets garbage collected
            self.label.image = self.curr_img_obj
            self.curr_img = new_img
        except IndexError:
            print("No more screenshots! Stopping classifier loop")
            self.window.destroy()
        
    def check_class_dir(self):
        for dir in self.class_dict.values():
            if not os.path.exists(dir):
                os.makedirs(dir)
