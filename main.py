import pandas as pd
import os
import configreader
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


def read_csv_direct(file_name):
    file = open(file_name, 'r', encoding='utf8')
    return file


root = tk.Tk()
root.withdraw()

allowed_conf = {("Configuration File(.conf)", ".conf")}
allowed_file = {("Accepted Files", ".xlsx .csv")}

conf_path = filedialog.askopenfilename(title="Please select config file", filetypes=allowed_conf, initialdir=".\\configs")
file_path = filedialog.askopenfilename(title="Please select input data", filetypes=allowed_file, initialdir=".\\inputs")

if conf_path == '' or file_path == '':
    exit(2)


data_ran = configreader.run_cfr(conf_path, file_path)

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
