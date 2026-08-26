import hashlib
import sqlite3
import os
from customtkinter import CTkLabel, CTkButton
from datetime import datetime


# from loading_json import json_loading_active_virus
# from ui_customtkinter import open_info_from_file

row = 1
def add_scanned_file(master_file, path_file):
    now_time = datetime.now().strftime("%H:%M:%S")

    # Додаємо проскановані файли в колонку "проскановані файли"
    label_time = CTkLabel(master = master_file, text = now_time, 
                    #  font = ("Times New Roman", 20)
                     )
    label_time.grid(row = row, column = 0, padx = 5, pady = 1)

    label_path = CTkLabel(master = master_file, text = path_file, 
                    #  font = ("Times New Roman", 20)
                     )
    label_path.grid(row = row, column = 0, padx = 5, pady = 1)

    row += 1



def add_virus_file(master_virus, path_file):

    from loading_json import json_loading_active_virus
    from ui_customtkinter import open_info_from_file


    now_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    active_virus_list = json_loading_active_virus()
    row_index = len(active_virus_list)

    # Додаємо файли в яких були виявлені віруси в колонку "знайдені загрози"
    # 1. Колонка с №
    asterisk_label = CTkLabel(
        master_virus, 
        text = row_index + 1, 
        fg_color="transparent",
        pady=2 
    )
    asterisk_label.grid(row=row_index, column=0, padx=5, pady=1, sticky="nsew")

    # 2. Колонка "Шлях"
    if len(path_file[0]) > 58:
        row_data_min = path_file[0][:55] + "..."
    else:
        row_data_min = path_file[0]

    path_label = CTkLabel(
        master_virus,
        text = f'   {row_data_min}',
        fg_color="transparent",
        anchor="w",
        wraplength = 370
    )
    path_label.grid(row=row_index, column=1, padx=(1, 5), pady=1, sticky="w")

    # 3. Колонка "Дата"
    date_label = CTkLabel(
        master_virus, 
        text = f'{path_file[1]}', 
        fg_color="transparent",
    )
    date_label.grid(row=row_index, column=2, padx=(5, 1), pady=1, sticky="nsew")

    # 4. Колонка ""Інформація" - Кнопка
    info_button = CTkButton(
        master_virus,
        text = "Додатково",
        width=120,
        height=23,
        command=lambda r=path_file: open_info_from_file(file = r[0], date = r[1])
    )
    info_button.grid(row=path_file, column=3, padx = 1, pady=1)




def get_sha256_for_files(directory_path, scanned_file, frame_scroll_virus_files):

    if not os.path.isdir(directory_path):
        print(f"Ошибка: {directory_path} не является директорией.")
        return []
    
    virus_file = []

    connect = sqlite3.connect('malware_hashes.db')
    cursor = connect.cursor()
    cursor.execute('SELECT hash FROM sha256')
    rows = cursor.fetchall()
    
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Вычисляем SHA256 для файла
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                print(f"Файл: {file_path}")
                for row in rows:
                    if file_hash == row:
                        virus_file.append(file_path)
                add_scanned_file(master_file = scanned_file, path_file = file_path, master_virus = frame_scroll_virus_files)
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")
    connect.close()        
    

    # return virus_file


# virus_file = get_sha256_for_files("D:\\Python")
# print(virus_file)


