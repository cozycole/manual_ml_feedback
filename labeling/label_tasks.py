import os
import shutil
from labeling.man_label import ManualClassifier
from labeling.man_patch_label import PatchManualClassifier
from labeling.instruction_strings import instruct_dict


def start_classification_tasks(shot_dir, db_str=None, false_neg=True):
    # Shot dir is the path to directory containing all image and patch directories
    # Classify full images from distress/no-distress
    img_src_template = "(Drawing images from %s)\n"
    full_img_instructions = instruct_dict["full_img_instruct"] + img_src_template 
    
    tmp_img_path = os.path.join(os.getcwd(), "temp_img_store")
    create_class_subdirs(tmp_img_path)

    # within auto classify images, full imgs must 
    # be in either distress or no_distress directory
    for label in ["distress", "no_distress"]:
        shot_path = os.path.join(shot_dir, label)
        print(f"Task: Labeling full {label} images")
        ManualClassifier(
            shot_path,
            os.path.join(tmp_img_path, "full_images"),
            db_str=db_str,
            task_label=full_img_instructions % shot_path
        ).start_classifier()
    move_incorrect_patches(shot_dir, tmp_img_path)

    # Now individually validate each patch
    for label in ["board", "tarp", "distress"]:
        shot_path = os.path.join(shot_dir, f"{label}_patches")
        patch_instructions = instruct_dict[f"{label}_patch_instruct"] + img_src_template
        print(f"Task: Labeling pre-classified {label} patches")
        ManualClassifier(
            shot_path,
            os.path.join(tmp_img_path, f"{label}_patches"),
            task_label=patch_instructions % shot_path
        ).start_classifier()
    
    # Currently all true and false positives are accounted for
    # Now go through each distress image to extract any distressed tarp/board patches
    # that are false negatives by the model
    # This means we exclude viewing any images if there are patches present in the full distress image
    # for the particular class
    if false_neg:
        # where the full img distress photos are located
        shot_path = os.path.join(tmp_img_path, "full_images", "distress")
        for label in ["board", "tarp"]:
            # needed for excluding an images where there are patches already found 
            print(f"Task: Finding false negative {label} patches")
            label_dir_path = os.path.join(tmp_img_path, f"{label}_patches", "distress")
            distress_imgs = os.listdir(os.path.join(tmp_img_path, "full_images", "distress"))
            distress_img_roots = [img.replace("_0.jpg","").replace(".jpg","") for img in distress_imgs]
            print(distress_img_roots)
            no_check_imgs = set()
            for patch_name in os.listdir(label_dir_path):
                patch_root = patch_name.split("_",1)
                patch_root = f"{patch_root[0]}_{patch_root[1][:22]}"
                print(patch_root)
                # distress images already containing patches for the given class
                if patch_root in distress_img_roots:
                    no_check_imgs.add(patch_root)
            # imgs to actually check for false negatives
            img_roots_to_check = [img_root for img_root in distress_img_roots if img_root not in no_check_imgs]
            imgs_to_check = [img for img in distress_imgs if img.replace("_0.jpg","") in img_roots_to_check]
            print(imgs_to_check)
            patch_instructions = instruct_dict[f"new_{label}_patch_instruct"] + img_src_template
            PatchManualClassifier(
                shot_dir=shot_path,
                class_dir=os.path.join(tmp_img_path, f"{label}_patches"),
                patch_width=500,
                patch_height=400,
                images=imgs_to_check,
                task_label=patch_instructions % shot_path
            ).start_classifier()
    
        # we finally go through all distress and slight distress with patch distress
        # we don't exclude any for the time being (fine having duplicate distress patches for training)
        patch_instructions = instruct_dict["new_distress_patch_instruct"] + img_src_template
        for label in ["distress", "slight_distress"]:
            shot_path = os.path.join(tmp_img_path, "full_images", label)
            print(f"Task: Finding false negative distress patches in {label} images")
            PatchManualClassifier(
                shot_dir=shot_path,
                class_dir=os.path.join(tmp_img_path, "distress_patches"),
                patch_width=200,
                patch_height=200,
                task_label=patch_instructions % shot_path
            ).start_classifier()
            
def move_incorrect_patches(shot_dir, tmp_img_path):
    # Now move all distressed patches into no distress if they are found
    # in a full img marked no distress (i.e. they are erroneously marked distressed)
    for label in ["board", "tarp", "distress"]:
        label_dir_path = os.path.join(shot_dir, f"{label}_patches")
        no_distress_imgs = os.listdir(os.path.join(tmp_img_path, "full_images", "no_distress"))
        no_distress_imgs = [img.replace("_0.jpg","").replace(".jpg","") for img in no_distress_imgs]
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

def create_class_subdirs(src):
    class_dirs = ["distress", "slight_distress", "no_distress", "unknown", "trash"]
    category_dirs = ["board_patches", "tarp_patches", "distress_patches", "full_images"]
    for cat in category_dirs:
        for cls in class_dirs:
            dir_name = os.path.join(src, cat, cls)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
