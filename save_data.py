"""
Functions needed for moving the data from the
temp_img_store to permanent storage.
"""
import os
import shutil
import psycopg2 as pg

def save_all_images(path_configs:dict):
    print("### SAVING IMAGES ###")
    temp_img_store = os.path.join(os.getcwd(), "temp_img_store")
    full_img_path = path_configs["full_img_store_path"]
    save_full_images(os.path.join(temp_img_store, "full_images"), full_img_path)
    for config in ["board", "distress", "tarp"]:
        class_config = path_configs[config]
        class_path = os.path.join(temp_img_store, f"{config}_patches")
        save_patches(class_path, class_config)

def save_full_images(src, dest):
    # src path and dest path contain the 
    # condition directories (distresss, slight_distress, ...)
    for dir in os.listdir(src):
        if dir != "trash":
            print(f"Copying images of {dir} to {dest}")
            src_cond_dir = os.path.join(src, dir)
            dest_cond_dir = os.path.join(dest, dir)
            copy_images(src_cond_dir, dest_cond_dir)

def save_patches(src_path, config: dict):
    store_path1 = config.get("store1_path", None)
    store_path2 = config.get("store2_path", None)
    for dest_pth in (store_path1, store_path2):
        if dest_pth:
            copy_images(os.path.join(src_path,"distress"), os.path.join(dest_pth, config["distress"]))
            copy_images(os.path.join(src_path,"no_distress"), os.path.join(dest_pth, config["no_distress"]))

def clear_class_images():
    src = os.path.join(os.getcwd(), "temp_img_store")
    for dir in os.listdir(src):
        category_path = os.path.join(src, dir)
        for img in os.listdir(category_path):
            shutil.rmtree(os.path.join(category_path,img))
    
def update_db(class_dir, db_str):
        print("updating db")
        conn = pg.connect(db_str)
        curs = conn.cursor()
        for dir in os.listdir(class_dir):
            print(dir)
            if dir[0] != '.':
                dir_path = os.path.join(class_dir, dir)
                print(dir_path)
                for shot in os.listdir(dir_path):
                    update_db_shot(curs, dir, shot)
                conn.commit()

def update_db_shot(curs, dir, shot: str):
    query = f"""
    UPDATE screenshots
    SET distress_class='{dir}'
    WHERE file_str='{shot.replace(".jpg", "")}'
    """
    curs.execute(query)            

def copy_images(src, dest):
    print(f"Copying images of {src} to {dest}")
    if os.path.exists(src):
        for img in os.listdir(src):
            if ".jpg" in img:
                src_path = os.path.join(src, img)
                shutil.copy(src_path, dest)
    else:
        print(f"{src} does not exist")