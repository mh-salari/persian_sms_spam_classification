#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 5 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
@source: https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd
"""

import sqlite3 as sl
import os

if __name__ == "__main__":

    db_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "farsi_sms_spam.db"
    )

    if not os.path.exists(db_path):

        con = sl.connect(db_path)

        with con:
            con.execute(
                """
                CREATE TABLE SMS (
                    sms_text TEXT,
                    sms_label TEXT
                );
            """
            )

        # sql = "INSERT INTO SMS (sms_text, sms_label) values( ?, ?)"
        # data = [("", "")]

        # with con:
        #     con.executemany(sql, data)


# with con:
#     data = con.execute("SELECT * FROM SMS")
#     with open("db.csv", "w") as f:
#         for count, row in enumerate(data):
#             print(count, row)
#             f.write("\x1e".join(row).replace("\n", " &newline "))
#             f.write("\n")
