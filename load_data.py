import pickle as pickle
import os
import pandas as pd
import torch
from utils import *


class RE_Dataset(torch.utils.data.Dataset):
    """Dataset 구성을 위한 class."""

    def __init__(self, pair_dataset, labels):
        self.pair_dataset = pair_dataset
        self.labels = labels

    def __getitem__(self, idx):
        item = {
            key: val[idx].clone().detach() for key, val in self.pair_dataset.items()
        }
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def preprocessing_dataset(dataset):
    """처음 불러온 csv 파일을 원하는 형태의 DataFrame으로 변경 시켜줍니다."""
    subject_entity = []
    object_entity = []
    sentence = []
    for i, j, k in zip(
        dataset["subject_entity"], dataset["object_entity"], dataset["sentence"]
    ):
        i_word = i[1:-1].split("', ")[0].split(":")[1].replace("'", "").strip()
        j_word = j[1:-1].split("', ")[0].split(":")[1].replace("'", "").strip()

        i_start = int(i.split("':")[2].split(",")[0])
        i_end = int(i.split("':")[3].split(",")[0])
        j_start = int(j.split("':")[2].split(",")[0])
        j_end = int(j.split("':")[3].split(",")[0])
        i_type = i[1:-1].split("':")[4].replace("'", "").strip()
        j_type = j[1:-1].split("':")[4].replace("'", "").strip()

        sent = entity_marker2(
            k, i_start, i_end, i_type, j_start, j_end, j_type
        )  # from utils.py

        subject_entity.append(i_word)
        object_entity.append(j_word)
        sentence.append(sent)
    out_dataset = pd.DataFrame(
        {
            "id": dataset["id"],
            "sentence": sentence,
            "subject_entity": subject_entity,
            "object_entity": object_entity,
            "label": dataset["label"],
        }
    )
    return out_dataset


def load_data(dataset_dir):
    """csv 파일을 경로에 맡게 불러 옵니다."""
    pd_dataset = pd.read_csv(dataset_dir)
    dataset = preprocessing_dataset(pd_dataset)

    return dataset


def tokenized_dataset(dataset, tokenizer):
    """tokenizer에 따라 sentence를 tokenizing 합니다."""
    concat_entity = []
    for e01, e02 in zip(dataset["subject_entity"], dataset["object_entity"]):
        temp = f"이 문장에서 @{e01}@과 #{e02}#은 어떤 관계일까?"  # multi 방식 사용
        concat_entity.append(temp)
        tokenized_sentences = tokenizer(
            list(dataset["sentence"]),
            concat_entity,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
            add_special_tokens=True,
        )
    return tokenized_sentences
