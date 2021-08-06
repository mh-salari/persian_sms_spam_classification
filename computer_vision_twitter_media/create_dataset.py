#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
"""

import os
import shutil
import pickle
import random
import argparse
from tqdm import tqdm
import numpy as np


def split_and_save_images(images_name, label, images_path, dataset_outout_path):

    # split images to 70% train, 15% val, 15% test
    splits = np.split(
        images_name, [int(0.7 * len(images_name)), int(0.85 * len(images_name))]
    )

    for idx, sub_dir in enumerate(["train", "val", "test"]):

        output_path = os.path.join(dataset_outout_path, sub_dir, label)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for image_name in tqdm(splits[idx]):
            shutil.copyfile(
                os.path.join(images_path, image_name),
                os.path.join(output_path, image_name),
            )


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='Lable SMS Images [t: test, o:other, d:Delete, l&k navigate')

    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_args()
    dataset_path = args.path
   

    images_path = os.path.join(dataset_path, "media")
    labels_path = os.path.join(dataset_path, "labels.pkl")

    dataset_outout_path = os.path.join(dataset_path, "classification_images")

    # delete old dataset
    try:
        shutil.rmtree(dataset_outout_path)
    except OSError as e:
        print(f"Error: {e.filename} - { e.strerror}.")

    images_name_list = []
    for root, dirs, files in os.walk(images_path):
        for file in files:
            images_name_list.append(file)

    labels = pickle.load(open(labels_path, "rb"))

    shuffled_labels = {}
    for image_name, label in labels.items():
        if image_name in images_name_list:
            shuffled_labels[image_name] = label
    keys = list(shuffled_labels.keys())
    random.shuffle(keys)
    shuffled_labels = dict([(key, shuffled_labels[key]) for key in keys])

    message_images = [
        name for name, label in shuffled_labels.items() if label == "text"
    ]
    other_images = [name for name, label in shuffled_labels.items() if label == "other"]

    print(f"Number of message images: {len(message_images)}")
    print(f"Number of other images: {len(other_images)}")

    # eq_labels = {}
    # num_inside = 0
    # num_outside = 0
    # eq_num = len(message_images)

    # for name, label in shuffled_labels.items():
    #     if label== "text":
    #         num_inside +=1
    #         eq_labels[name]=label
    #     if num_inside == eq_num:
    #         break
    # for name, label in shuffled_labels.items():
    #     if label== "other":
    #         num_outside +=1
    #         eq_labels[name]=label
    #     if num_outside == eq_num:
    #         break
    # print(len(eq_labels))

    split_and_save_images(message_images, "message", images_path, dataset_outout_path)
    split_and_save_images(other_images, "other", images_path, dataset_outout_path)

