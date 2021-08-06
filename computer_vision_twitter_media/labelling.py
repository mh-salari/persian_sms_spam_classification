#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
"""

import os
import cv2
import pickle
import argparse

def find_all_images(path):
    images_path_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # if file.endswith((".png", ".jpg")):
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), root, file)
            images_path_list.append(path)

    if not images_path_list:
        raise Exception("Nothing was found! Check your images path.")
    return images_path_list


def labelling(
    images_path_list, labels,
):
    loop = True
    idx = 30_000

    while idx < len(images_path_list):

        image_name = os.path.basename(images_path_list[idx])

        image = cv2.imread(images_path_list[idx])

        if image_name in labels:
            text = f"Label: {labels[image_name]}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            if labels[image_name] == "text":
                color = (0, 255, 0)
            elif labels[image_name] == "other":
                color = (255, 0, 0)
            else:
                color = (0, 0, 255)
            font_thickness = 2
            position = (10, 10)
            x, y = position

            text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
            text_w, text_h = text_size

            cv2.rectangle(image, position, (x + text_w, y + text_h + 5), (0, 0, 0), -1)
            cv2.putText(
                image,
                text,
                (x, int(y + text_h + font_scale - 1)),
                font,
                font_scale,
                color,
                font_thickness,
            )

        if image is None:
            print("Invalid image")
            # os.remove(images_path_list[idx])
            images_path_list.pop(idx)

        else:
            key = 0
            while loop:
                im_num = idx + 1 if idx >= 0 else len(images_path_list) + idx + 1
                cv2.imshow(
                    f"{os.path.basename(os.path.dirname(images_path_list[idx]))}:[{im_num}/{len(images_path_list)}] {os.path.basename(images_path_list[idx])}",
                    image,
                )
                key = cv2.waitKey(0) & 0xFF
                if key == 27 or key == ord("q"):  # 27 == Esc key to stop
                    loop = False
                    idx = len(images_path_list) + 1
                    break
                elif key == ord("l"):
                    idx += 1
                    break
                elif key == ord("k"):
                    idx -= 1
                    break
                elif key == ord("d"):
                    os.remove(images_path_list[idx])
                    images_path_list.pop(idx)
                    break
                elif key == ord("t"):
                    labels[image_name] = "text"
                    num_text_images = len(
                        [label for label in labels.values() if label == "text"]
                    )
                    print(f"Number of sms/text {num_text_images}")
                    idx += 1
                    break
                elif key == ord("o"):
                    labels[image_name] = "other"
                    idx += 1
                    break
            cv2.destroyAllWindows()
    return labels


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Lable SMS Images [t: test, o:other, d:Delete, l&k navigate')

    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_args()
    images_path = args.path



    base_path = os.path.dirname(os.path.realpath(__file__))


    dataset_path = os.path.join(base_path, "dataset")
    labels_output_path = os.path.join(dataset_path, "labels.pkl")

    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)

    if os.path.exists(labels_output_path):
        labels = pickle.load(open(labels_output_path, "rb"))
    else:
        labels = {}

    images_path_list = find_all_images(images_path)
    num_all_images = len(images_path_list)
    print(f"ALL images: {num_all_images}")

    num_previous_labels = len(labels)
    print(f"Labeled images: {num_previous_labels}")

    labels = labelling(images_path_list, labels)

    if labels:
        pickle.dump(
            labels, open(labels_output_path, "wb"),
        )

    num_labels = len(labels)
    print(f"New labels: {num_labels - num_previous_labels}")
    print(f"Remained images: {num_all_images - num_labels}")
