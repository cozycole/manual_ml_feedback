import os
import shutil
from PIL import Image, ImageTk
import tkinter as tk
import psycopg2 as pg
import instruction_strings as inst_str

class ManualClassifier:
    def __init__(self, shot_dir, class_dir, db_str=None, task_label=None):
        self.shot_dir = shot_dir
        self.class_dir = class_dir
        self.task_label = task_label
        self.db_str = db_str
        self.images = [f for f in os.listdir(self.shot_dir) if (f.endswith(".jpg") or f.endswith(".png"))]
        if not self.images: raise Exception("No files found in shot_dir")
        self.img_count = len(self.images)
        print(self.images)
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
        except IndexError:
            pass
        
        curr_img_path = os.path.join(self.shot_dir, self.curr_img)
        img = Image.open(curr_img_path).convert("RGB")
        dimensions = (800, 800) if img.size[0] == img.size[1] else (1000,800)
        self.curr_img_obj = ImageTk.PhotoImage(img.resize(dimensions))
        self.label = tk.Label(self.window, image=self.curr_img_obj)
        self.label.pack()
        task_label = tk.Label(self.window, text=self.task_label)
        task_label.pack(side=tk.BOTTOM)
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
            if self.db_str:
                print("Updating shot classes in db")
                self.update_db()
        
    def update_db(self):
        print("updating db")
        conn = pg.connect(self.db_str)
        curs = conn.cursor()
        for dir in os.listdir(self.class_dir):
            print(dir)
            if dir[0] != '.':
                dir_path = os.path.join(self.class_dir, dir)
                print(dir_path)
                for shot in os.listdir(dir_path):
                    self.update_db_shot(curs, dir, shot)
                conn.commit()

    def update_db_shot(self, curs, dir, shot: str):
        query = f"""
        UPDATE screenshots
        SET distress_class='{dir}'
        WHERE file_str='{shot.replace(".jpg", "")}'
        """
        curs.execute(query)

    def check_class_dir(self):
        for dir in self.class_dict.values():
            if not os.path.exists(dir):
                os.makedirs(dir)

def start_classification_tasks(shot_dir):
    # Classify full images from distress/no-distress
    img_src_template = "(Drawing images from %s)\n"
    full_img_instructions = inst_str.full_img_instruct + img_src_template 
    tmp_img_path = os.path.join(os.getcwd(), "temp_img_store")
    # within auto classify images, full imgs must 
    # be in either distress or no_distress directory
    for label in ["distress", "no_distress"]:
        shot_path = os.path.join(shot_dir, label)
        ManualClassifier(
            shot_path,
            os.path.join(tmp_img_path, "full_images"),
            task_label=full_img_instructions % shot_path
        ).start_classifier()

    # Now move all distressed patches into no distress if they are found
    # in a full img marked no distress (i.e. they are erroneously marked distressed)
    for label in ["board", "tarp", "distress"]:
        label_dir_path = os.path.join(shot_dir, f"{label}_patches")
        no_distress_imgs = os.listdir(os.path.join(tmp_img_path, "full_images", "no_distress"))
        no_distress_imgs = [img.replace("_0.jpg","") for img in no_distress_imgs]
        err_counter = 0
        for patch_name in os.listdir(label_dir_path):
            # full img is of form [0-9]+_[a-zA-Z0-9-_]{22}_0.jpg
            # patches of form [0-9]+_[a-zA-Z0-9-_]{22}_0_patch[0-9].jpg
            patch_root = patch_name.split("_",1)
            patch_root = f"{patch_root[0]}_{patch_root[1][:22]}"
            if patch_root in no_distress_imgs:
                err_counter += 1
                patch_path = os.path.join(label_dir_path, patch_name)
                dest_dir = os.path.join(tmp_img_path, f"{label}_patches", "no_distress")
                shutil.move(patch_path, dest_dir)
            print(f"Moved {err_counter} {label} patches to no distress")
            