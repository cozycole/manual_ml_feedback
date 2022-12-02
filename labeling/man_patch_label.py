"""
This class is used for viewing and labeling patches of full images.
Only distressed ones should be marked (anything else will be trashed)
"""
import os
from PIL import Image, ImageTk
import tkinter as tk
import labeling.man_label as ml

class PatchManualClassifier(ml.ManualClassifier):

    def __init__(self, shot_dir, class_dir, patch_width, patch_height,images = None, db_str=None, task_label=None):
        super().__init__(shot_dir, class_dir, images, db_str=db_str, task_label=task_label)

        self.patch_width = patch_width
        self.patch_height = patch_height
        self.patch_count = 0 # used for naming patch
        self.curr_patch_list = []

    def crop_new_patches(self, img):
        width , height = img.size
        width = min(1000, width)
        height = min(800, height)
        for i in range(0, width, self.patch_width):
            for j in range(0, height, int(self.patch_height/2)):
                cropped_img = img.crop((i,j, i + self.patch_width, j+self.patch_height))
                if j+self.patch_height <= height and i+ self.patch_width <= width:
                    self.curr_patch_list.append(cropped_img)
    
    def start_classifier(self):
        try:
            self.curr_img = self.images.pop()
            if self.curr_img is None:
                raise IndexError
        except Exception:
            print(f"No images to show in {self.shot_dir}")
            self.window.destroy()
            return

        self.curr_img_path = os.path.join(self.shot_dir, self.curr_img)
        self.curr_img_obj = Image.open(self.curr_img_path)
        self.crop_new_patches(self.curr_img_obj) # updates curr_patch_list
        # Note: self.curr_patch_list is a list of PIL Images
        self.curr_patch = self.curr_patch_list.pop()
        dimensions = (800, 800) if self.patch_height == self.patch_width else (1000,800)
        self.curr_patch_obj = ImageTk.PhotoImage(self.curr_patch.resize(dimensions), master=self.window)
        self.label = tk.Label(self.window, image=self.curr_patch_obj)
        self.label.pack()
        self.counter_label = tk.Label(self.window, textvariable=self.counter_text)
        self.counter_text.set(f"""
        COUNTER
        {self.image_count}/{self.total_imgs}
        """)
        self.counter_label.pack(side=tk.BOTTOM)
        self.tk_task_label = tk.Label(self.window, text=self.task_label)
        self.tk_task_label.pack(side=tk.BOTTOM)
        self.window.mainloop()

    def file_action_on_event(self, event):
        patch_name = self.curr_img.replace(".jpg",f"_patch{self.patch_count}.jpg") 
        # move to class dir based on key press
        to_path = os.path.join(self.class_dict[event.keysym], patch_name)
        print(f"Moving patch {patch_name} to {to_path}")
        if event.keysym != "BackSpace":
            self.curr_patch.save(to_path, format="JPEG")
        self.patch_count += 1
        if not len(self.curr_patch_list):
            try:
                self.patch_count = 0
                self.curr_img = self.images.pop()
                self.curr_img_path = os.path.join(self.shot_dir, self.curr_img)
                self.curr_img_obj = Image.open(self.curr_img_path)
                self.crop_new_patches(self.curr_img_obj)
                self.image_count += 1
                self.counter_text.set(f"""
                    COUNTER
                    {self.image_count}/{self.total_imgs}
                    """)
            except IndexError:
                print("No more screenshots! Stopping classifier loop")
                self.window.destroy()
                self.window = None
                return
        self.curr_patch = self.curr_patch_list.pop()
        dimensions = (800, 800) if self.patch_height == self.patch_width else (1000,800)
        self.curr_patch_obj = ImageTk.PhotoImage(self.curr_patch.resize(dimensions))
        self.label.configure(image=self.curr_patch_obj)
        self.label.image = self.curr_patch_obj