import yaml
import man_label as ml
import label_tasks as lt

def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    lt.start_classification_tasks(config["auto_classify_images_directory"])

if __name__ == "__main__":
    main()