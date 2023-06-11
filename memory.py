import os
import csv
from huggingface_hub import Repository

DATASET_REPO_URL = "https://huggingface.co/datasets/FranklinWillemen/persistent-space-dataset"
DATA_FILENAME = "data.csv"
DATA_FILE = os.path.join("data", DATA_FILENAME)
HF_TOKEN = os.environ.get("HF_TOKEN")

repo = Repository(
    local_dir="data", clone_from=DATASET_REPO_URL, use_auth_token=HF_TOKEN
)

def save_to_hf(context):
    with open(DATA_FILE, "a") as csvfile:
        for message in context:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "message"])
            writer.writerow(
                {"name": message['role'], "message": message['content']}
            )
        commit_url = repo.push_to_hub()
        print(commit_url)

