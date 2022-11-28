import yaml
import manual_classify as mc

def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    mc.start_classification_tasks(config["auto_classify_images_directory"])

if __name__ == "__main__":
    main()