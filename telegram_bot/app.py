#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Oct 04 2020
@author: MohammadHossein Salari
@mail: mohammad.hossein.salari@gmail.com
@website: www.mh-salari.me
@sources:
    - https://github.com/eternnoir/pyTelegramBotAPI
    - https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd
    
This is a telegram bot to add new sms to a mysql dataset
"""
import telebot
from telebot import types
import sqlite3 as sl
import logging as log
import os
import sys
import time
import config

log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "telegram_bot.log")

log.basicConfig(
    level=log.INFO, filename=log_path, format="%(asctime)s %(levelname)s %(message)s"
)


def log_command(message):
    log.info(f"Command {message.text} has been received")


# set the path of database
db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "database",
    "farsi_sms_spam.db",
)

db_connection = sl.connect(db_path)

bot = telebot.TeleBot(config.bot_token, threaded=False, skip_pending=True)

known_users = []  # todo: save these in a file,
user_step = {}  # so they won't reset every time the bot restarts
user_sms = {}


def save_sms(sms_text, sms_label):
    """save the text sms and it's label to the dataset

    Args:
        sms_text (str): sms text
        sms_label (str): 'spam' or 'num_spam'
    """
    sql_command = "INSERT INTO SMS (sms_text, sms_label) values(?, ?)"
    data = [(sms_text, sms_label)]

    with db_connection:
        db_connection.executemany(sql_command, data)
    log.info("new sms saved")


def get_user_step(chat_id):
    """helper function to track user commands

    Args:
        chat_id (int): id of user

    Returns:
        if old user: user step
        if new user: step 0
    """
    if chat_id in user_step:
        return user_step[chat_id]
    else:
        known_users.append(chat_id)
        user_step[chat_id] = 0
        log.info(f'New user[{chat_id}] detected, who hasn\'t used "/start" yet')
        return 0


@bot.message_handler(commands=["start"])
def command_start(message):

    log_command(message)

    bot.send_message(
        message.chat.id,
        "به ربات تلگرامی ایجاد پایگاه داده public پیامک(SMS)های اسپم و تبلیغاتی متنی به زبان فارسی خوش آمدید.\n"
        + "جهت حفظ حریم خصوصی مشارکت کنندگان هیچ گونه اطلاعاتی از فرستنده‌ی پیام در پایگاه داده ذخیره نمی‌شود.\n"
        + "با این وجود دقت نمایید پیامک‌های حاوی اطلاعات حساس همچون نام و نام خانوادگی، کد ملی و ... را ارسال نفرمایید.\n"
        + "\n پ.ن: برای ایجاد دیتاست بالانس لطفا بجز پیامک‌های اسپم و تبلیغاتی پیامک‌های عادی و غیر اسپم رو هم برامون ارسال کنید:)\n",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    # if user hasn't used the "/start" command yet:
    if message.chat.id not in known_users:
        # save user id and his current "command level", so he can use commands
        user_step[message.chat.id] = 0

    # show the new user the help page
    command_help(message)


# get sms
@bot.message_handler(commands=["newsms"])
def newsms(message):

    markup = types.ForceReply(selective=False)

    bot.send_message(message.chat.id, "متن پیامک را وارد کنید", reply_markup=markup)
    user_step[message.chat.id] = 1
    log_command(message)


# get label of sms
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def select_label(message):
    if message.text == "/end":
        command_end(message)
    elif message.text == "/help":
        command_help(message)
    else:
        user_sms[message.chat.id] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 2

        markup.add(
            types.InlineKeyboardButton("اسپم", callback_data="spam"),
            types.InlineKeyboardButton("عادی", callback_data="nun_spam"),
        )

        bot.send_message(
            message.chat.id,
            "نوع پیام را از نظر اسپم و یا پیامک عادی بودن مشخص نمایید:\n"
            + message.text,
            reply_markup=markup,
        )

        user_step[message.chat.id] = 2


# save label of sms
@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 2)
def callback_query(call):

    if user_sms[call.message.chat.id] != "":
        if call.data == "spam":
            bot.answer_callback_query(call.id, "اسپم در پایگاه داده ثبت شد")
        elif call.data == "nun_spam":
            bot.answer_callback_query(call.id, "در پایگاه داده ثبت شد")

        save_sms(user_sms[call.message.chat.id], call.data)

        bot.send_message(
            call.message.chat.id,
            "پیامک شما با موفقیت ثبت شد، جهت ثبت پیامک جدید آن‌را تایپ نمایید در غیر این صورت برای خروج از بات  /end را وارد نمایید.",
            reply_markup=types.ReplyKeyboardRemove(),
        )

        call.message.text = "/newsms"
        user_step[call.message.chat.id] = 0
        user_sms[call.message.chat.id] = ""
        newsms(call.message)
    bot.answer_callback_query(call.id, "")


@bot.message_handler(commands=["end"])
def command_end(message):
    log_command(message)
    user_step[message.chat.id] = 0
    bot.send_message(
        message.chat.id,
        "با سپاس فراوان از مشارکت شما 🌻",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["help"])
def command_help(message):
    log_command(message)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            "ارتباط با توسعه دهنده", url="telegram.me/mh_salari"
        )
    )

    bot.send_message(
        message.chat.id,
        "۱) برای ثبت پیامک (SMS) جدید /newsms را وارد کنید.\n"
        + "۲) جهت اتمام کار /end را وارد نمایید. \n",
        reply_markup=keyboard,
    )


# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=["text"])
def command_default(message):
    log_command(message)
    # this is the standard reply to a normal message
    bot.send_message(
        message.chat.id,
        'دستور نامعتبر است "'
        + message.text
        + '"\nجهت دریافت راهنما  /help را وارد نمایید',
        reply_markup=types.ReplyKeyboardRemove(),
    )


def main_loop():
    log.basicConfig(level=log.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        log.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as err:
        log.error("Bot polling error: {0}".format(err.args))
        bot.stop_polling()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nExiting by user request.\n")
        sys.exit(0)
