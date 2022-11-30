import yaml
import save_data as sd
from labeling import man_label as ml
from labeling import label_tasks as lt

def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    print(config["full_img_store_path"])
    lt.start_classification_tasks(config["auto_classify_images_directory"])
    sd.update_db(config["full_img_store_path"], config["db_str"])
    sd.save_all_images(config)
    sd.clear_class_images()

if __name__ == "__main__":
    main()