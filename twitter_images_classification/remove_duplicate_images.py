#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
"""

import duplicates as dup
import os

if __name__ == "__main__":
    folder_of_interest = "/home/hue/Data/codes/samandoon/search_twitter/database/media"
    dataset_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dataset")

    print("Finding duplicate images")
    print("-" * 50)
    df = dup.list_all_duplicates(
        folder_of_interest, to_csv=True, csv_path=dataset_path, fastscan=False
    )

    df_duplicates = df.drop_duplicates(subset=["hash"], keep="last")

    df_remove = df[~df["file"].isin(df_duplicates["file"])]

    print("")
    print("-" * 50)
    print(f"Number of duplicate images: {len(df_remove)}")

    for file in df_remove["file"]:
        try:
            os.remove(file)
        except Exception as e:
            print(e)
