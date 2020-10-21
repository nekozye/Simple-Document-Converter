import pandas as pd
import os
import configreader
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


def read_csv_direct(file_name):
    file = open(file_name, 'r', encoding='utf8')
    return file


def data_sanitize(filename):
    df = pd.read_csv(filename, keep_default_na=False, parse_dates=True, dtype=str)
    for index, row in df.iterrows():
        if (index == 0):
            continue
        for c_index, column in df.iteritems():
            if str(df.at[index, c_index]) == "":
                df.at[index, c_index] = str(df.at[index - 1, c_index])
    moded_file = filename.replace(".csv", "")
    df.astype('string')
    df.to_csv(moded_file + "_copy.csv", encoding="utf-8", index=False)
    return moded_file + "_copy.csv"


def data_sanitize_xlsx(filename):
    df = pd.read_excel(filename, keep_default_na=False, parse_dates=True, dtype=str)
    for index, row in df.iterrows():
        if (index == 0):
            continue
        for c_index, column in df.iteritems():
            if str(df.at[index, c_index]) == "":
                df.at[index, c_index] = str(df.at[index - 1, c_index])
    moded_file = filename.replace(".xlsx", "")
    df.astype('string')
    df.to_excel(moded_file + "_copy.xlsx", encoding="utf-8", index=False)
    return moded_file + "_copy.xlsx"


root = tk.Tk()
root.withdraw()

allowed_conf = {("Configuration File(.conf)", ".conf")}
allowed_file = {("Accepted Files", ".xlsx .csv")}

conf_path = filedialog.askopenfilename(title="Please select config file", filetypes=allowed_conf, initialdir=".\\configs")
file_path = filedialog.askopenfilename(title="Please select input data", filetypes=allowed_file, initialdir=".\\inputs")

if conf_path == '' or file_path == '':
    exit(2)

new_path = None

if file_path.endswith(".csv"):
    new_path = data_sanitize(file_path)
elif file_path.endswith(".xlsx"):
    new_path = data_sanitize_xlsx(file_path)
else:
    exit(2)

data_ran = configreader.run_cfr(conf_path, new_path)

current_time = datetime.now().strftime("%Y_%m%d")

guess_counter = 1
new_guess = current_time+"_"+str(guess_counter)+".xlsx"

output_folder = ".\\output"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

while os.path.exists(output_folder+"\\"+new_guess):
    guess_counter += 1
    new_guess = current_time + "_" + str(guess_counter) + ".xlsx"


data_ran.to_excel(output_folder+"\\"+new_guess, encoding="utf-8", index=False)

os.remove(new_path)
