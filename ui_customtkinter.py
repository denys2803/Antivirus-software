import customtkinter as tk
from tkinter import filedialog
from tkinter import Text
from tkinter import messagebox

from loading_json import json_loading_info, json_saving_info, json_loading_event_logs, json_saving_event_logs, save_file_event_logs, json_loading_versions, json_loading_app_info, json_loading_active_virus, json_saving_active_virus, get_rows_form_virus_file, json_loading_quarantine, json_save_quarantine
# from signature_scanning import get_sha256_for_files

from system_info import get_system_info
import threading
from queue import Queue

from datetime import datetime
import sqlite3
import hashlib
import os

import shutil
path_quarantine_folder = './virused_files'

import time


entry_path = None
folder_selected = None

# Паралельний процес підрахунку інформації про систему користувача
system_information = None
q = Queue()
def get_system_information():
    global system_information
    q.put(get_system_info())
    system_information = q.get()
thread_sys_info = threading.Thread(target = get_system_information)
thread_sys_info.daemon = True
thread_sys_info.start()


def select_directory():
    global folder_selected
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        if entry_path != None:
            entry_path.delete(0, "end")
        
        else: ...
        
        entry_path.insert(0, folder_selected)    
        

def destroy_widgets():
    # Очищаємо основний фрейм
    for widget in main_frame.winfo_children():
        widget.destroy()


def set_active_button(button_index):
    global active_button_index
    active_button_index = button_index
    # Оновлюємо кольора кнопок
    for i, btn in enumerate(button_list):
        if i == active_button_index:
            btn.configure(fg_color = "#37719f", text_color = "black")  # Активна
        else:
            btn.configure(fg_color = "#354f52", text_color = "white")  # Неактивна


# def open_info_from_file(file, date, concurrence = 'signature'):
#     '''Функция для открытия окна с информацией о файле, возможность удалить файл / отправить в карантин. toplevel'''
#     print(f"Файл: {file}\nДата виявлення: {date}")




def on_quarantine(file_path, analysis_type):
    if not os.path.exists(file_path):
        messagebox.showerror("Помилка", f"Файл не знайдено:\n{file_path}")
        return

    answer = messagebox.askyesno("Карантин", f"Перемістити файл в карантин?\n{file_path}")
    if not answer:
        return

    os.makedirs(path_quarantine_folder, exist_ok=True)
    base_name = os.path.basename(file_path)
    dest_path = os.path.join(path_quarantine_folder, base_name)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(path_quarantine_folder, f"{counter}_{base_name}")
        counter += 1

    try:
        shutil.move(file_path, dest_path)
        remove_virus_row_by_path(file_path)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося перемістити файл:\n{file_path}\nПомилка: {e}")
        print(e)
        return

    # Время нахождения и перемещения
    found_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    moved_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Загружаем текущий JSON и добавляем запись
    quarantine_data = json_loading_active_virus()
    # new_id = str(max([int(k) for k in quarantine_data.keys()], default=0) + 1)
    new_id = len(quarantine_data) + 1
    # quarantine_data[new_id] = {
    #     "original_path": file_path,
    #     "quarantine_path": dest_path,
    #     "found_time": found_time,
    #     "moved_time": moved_time,
    #     "analysis_type": analysis_type
    # }

    # entry = {
    # "id": new_id,
    # "original_path": file_path,
    # "quarantine_path": dest_path,
    # "found_time": found_time,
    # "moved_time": moved_time,
    # "analysis_type": analysis_type
    # }

    quarantine_data.append({
        "id": new_id,
        "original_path": file_path,
        "quarantine_path": dest_path,
        "found_time": found_time,
        "moved_time": moved_time,
        "analysis_type": analysis_type
    })

    # quarantine_data[new_id] = {
    #     "id": new_id,
    #     "original_path": file_path,
    #     "quarantine_path": dest_path,
    #     "found_time": found_time,
    #     "moved_time": moved_time,
    #     "analysis_type": analysis_type
    # }


    json_save_quarantine(quarantine_data)
    
    top.destroy()


    for item in table_frame.get_children():
        values = table_frame.item(item, "values")
        if values[0] == file_path:
            table_frame.delete(item)
            break

    






def restore_from_quarantine(file_id):
    quarantine_data = json_loading_quarantine()
    if file_id not in quarantine_data:
        messagebox.showerror("Помилка", "Файл не знайдено у карантині")
        return

    entry = quarantine_data[file_id]
    original_path = entry["original_path"]
    quarantine_path = entry["quarantine_path"]

    try:
        shutil.move(quarantine_path, original_path)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося відновити файл:\n{e}")
        return

    # Удаляем запись из JSON
    del quarantine_data[file_id]
    json_save_quarantine(quarantine_data)
    


def delete_from_quarantine(file_id):
    quarantine_data = json_loading_quarantine()
    if file_id not in quarantine_data:
        messagebox.showerror("Помилка", "Файл не знайдено у карантині")
        return

    entry = quarantine_data[file_id]
    quarantine_path = entry["quarantine_path"]

    try:
        if os.path.exists(quarantine_path):
            os.remove(quarantine_path)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося видалити файл:\n{e}")
        return

    # Удаляем запись из JSON
    del quarantine_data[file_id]
    json_save_quarantine(quarantine_data)
    return


def show_quarantine_info(entry):
    top = tk.CTkToplevel()
    top.title("Інформація про файл у карантині")
    
    w, h = 500, 180
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    x = root_x + (root_w - w) // 2
    y = root_y + (root_h - h) // 2
    
    top.geometry(f"{w}x{h}+{x}+{y}")
    top.transient(root)
    top.grab_set()

    info_text = (
        f"Оригінальний шлях: {entry['original_path']}\n"
        f"Шлях у карантині: {entry['quarantine_path']}\n"
        f"Знайдено: {entry['found_time']}\n"
        f"Переміщено у карантин: {entry['moved_time']}\n"
        f"Аналіз: {entry['analysis_type']}"
    )

    tk.CTkLabel(top, text=info_text, justify="left", anchor="w").pack(padx=15, pady=15, fill="both")

    tk.CTkButton(top, text="Закрити", width=120, command=top.destroy).pack(pady = (15, 5), padx = 5, fill = "both", side = tk.BOTTOM)


def on_delete(file_path): 
    if not os.path.exists(file_path):
        messagebox.showerror("Помилка", f"Файл не знайдено:\n{file_path}")
        return
    
    answer = messagebox.askyesno("Підтвердження", f"Ви дійсно хочете видалити файл?\n{file_path}")
    
    if answer:
        try:
            os.remove(file_path)

            remove_virus_row_by_path(file_path)

            messagebox.showinfo("Успішно", f"Файл успішно видалено:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося видалити файл:\n{file_path}\n\nПомилка: {e}")
            return
    else:
        return

    top.destroy()


def on_cancel():
    top.destroy()


def open_info_from_file(file, date, concurrence = 'signature'):
    global top

    top = tk.CTkToplevel()
    top.title("Дія з файлом")

    window_top_x = 500; window_top_y = 380
    w_top = (top.winfo_screenwidth() // 2) - (window_top_x // 2)
    h_top = (top.winfo_screenheight() // 2) - (window_top_y // 2)

    top.geometry(f"{window_top_x}x{window_top_y}+{w_top}+{h_top}") 
  
    top.resizable(False, False)

    if concurrence == 'signature':
        text_concurrence = 'сигнатурного'
    elif concurrence == 'heuristic ':
        text_concurrence = 'евристичного'

    text = f"""
    Увага! Виявлено підозрілий файл на вашій системі.

    Шлях до файлу: {file}

    Файл був знайдений за допомогою {text_concurrence} аналізу антивірусної бази.

    Дата виявлення: {date}

    Рекомендується негайно виконати одну з доступних дій:
    - Перемістити файл в карантин
    - Видалити файл
    - Скасувати і залишити файл без змін

    Будьте обережні! Файл може містити шкідливий код.
    """
    
    text_label = tk.CTkLabel(
        top,
        text=text,
        wraplength=480,
        justify="left",
        font=("Times New Roman", 14)
    )
    text_label.pack(padx=10, pady=20, fill="both", expand=True)

    button_frame = tk.CTkFrame(top, fg_color="transparent")
    button_frame.pack(side="bottom", fill="x", pady=10, padx=5)

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    
    
    btn_quarantine = tk.CTkButton(
        button_frame,
        text="Перемістити в карантин",
        command = lambda: on_quarantine(file_path = file, analysis_type = concurrence)
    )
    btn_quarantine.grid(row=0, column=0, sticky="ew", padx=5)
    
    btn_delete = tk.CTkButton(
        button_frame,
        text="Видалити",
        command = lambda: on_delete(file)
    )
    btn_delete.grid(row=0, column=1, sticky="ew", padx=5)
    
    btn_cancel = tk.CTkButton(
        button_frame,
        text="Скасувати",
        command=on_cancel
    )
    btn_cancel.grid(row=0, column=2, sticky="ew", padx=5)
    
    top.grab_set()
    top.focus_force()


def save_event_log(event_date, event_description): 
    json_saving_event_logs(event_date = event_date, event_description = event_description)


def remove_virus_row_by_path(path):
    if path not in virus_rows:
        return

    for widget in virus_rows[path]:
        widget.destroy()

    del virus_rows[path]


    # active_virus = json_loading_active_virus()
    # for item in active_virus:
    #     if item['path'] == path:
    #         active_virus.pop(item)
    # os.remove('active_virus.json')
    # for i in active_virus:
    #     json_saving_active_virus(date = i['date'], path = i['path'], concurrence = 'concurrence')



def create_titles(master, headers):
    header_font = tk.CTkFont("Times New Romans", 13, weight = "bold")
    for col_index, header_text in enumerate(headers):
        header_label = tk.CTkLabel(
            master = master, 
            text=header_text, 
            font=header_font,
            fg_color=("gray70", "gray30"),
            corner_radius=5,
        )
        header_label.grid(row = 0, column = col_index, padx = 1, pady = (1, 0), sticky = "nsew")


stop_timer = False
elapsed_time = 0
def update_timer():
    global elapsed_time, stop_timer, result
    if stop_timer:
        return

    days = elapsed_time // 86400
    hours = (elapsed_time % 86400) // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60

    result = ""
    if days > 0:
        result += f"{days} дн. "
    if hours > 0 or days > 0:
        result += f"{hours} г. "
    if minutes > 0 or hours > 0 or days > 0:
        result += f"{minutes} хв. "
    result += f"{seconds} сек."

    elapsed_time += 1 
    
    timer_label.configure(text=f"Сканування триває: {result}")
    timer_label.after(1000, update_timer)
    

virus_rows = {}  
def add_rows_virus_table(master, row_index, row_data):
    global virus_rows
    full_path = row_data[0]

    # 1. Колонка "№"
    asterisk_label = tk.CTkLabel(
        master, 
        text = row_index + 1, 
        fg_color="transparent",
        pady=2 
    )
    asterisk_label.grid(row=row_index + 1, column=0, padx=5, pady=1, sticky="nsew")

    # 2. Колонка "Шлях"
    if len(row_data[0]) > 52:
        row_data_min = row_data[0][:49] + "..."
    else:
        row_data_min = row_data[0]

    path_label = tk.CTkLabel(
        master,
        text = f'   {row_data_min}',
        fg_color="transparent",
        anchor="w",
        wraplength = 370
    )
    path_label.grid(row=row_index + 1, column=1, padx=(1, 5), pady=1, sticky="w")

    # 3. Колонка "Дата"
    date_label = tk.CTkLabel(
        master, 
        text = f'{row_data[1]}', 
        fg_color="transparent",
    )
    date_label.grid(row=row_index + 1, column=2, padx=(5, 1), pady=1, sticky="nsew")

    # 4. Колонка ""Інформація" - Кнопка
    info_button = tk.CTkButton(
        master,
        text = "Додатково",
        width=120,
        height=23,
        command=lambda r=row_data: open_info_from_file(file = r[0], date = r[1])
    )
    info_button.grid(row=row_index + 1, column=3, padx = 1, pady=1)


    virus_rows[full_path] = [
        asterisk_label,
        path_label,
        date_label,
        info_button
    ]



    root.update_idletasks()
    master._parent_canvas.yview_moveto(1)


def update_progressbar_and_button():
    if progress == 1:
        progress_bar.stop()
        progress_bar.configure(mode = 'determinate')
        progress_bar.set(1)

        but_stop_file_scanning.configure(text = 'Повернутися')
        timer_label.configure(text = f'Сканування тривало: {result}')

        if count_vir == 0:
            messagebox.showinfo(title = 'Успіх!', message = f'Сканування успішно завершено!\n\nСканування тривало: {result}\nФайлів проскановано: {count}\nЗнайдено загроз: {count_vir}')
        else:
            messagebox.showerror(title = 'Знайдено помилки!', message = f'Сканування завершено. Було знайдено загрози!\n\nСканування тривало: {result}\nФайлів проскановано: {count}\nЗнайдено загроз: {count_vir}')

        return
    table_frame.after(200, update_progressbar_and_button)


def update_scrollerbar_virus_file():
    # global row_add_virused_file
    if not hasattr(update_scrollerbar_virus_file, "row_counter"):
        update_scrollerbar_virus_file.row_counter = get_rows_form_virus_file()

    active_virus_file_list = json_loading_active_virus()
    existing_paths = set()
    for v in active_virus_file_list:
        existing_paths.add(v[0])

    with buffer_lock_vir_file:
        while virused_files_buffer:
            file_path = virused_files_buffer.pop(0)
            if file_path in existing_paths:
                print("YES")
                continue
            time_now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            json_saving_active_virus(date=time_now, path=file_path, concurrence='signature')
            data = (file_path, time_now, 'signature')
            add_rows_virus_table(master=table_frame, row_index=update_scrollerbar_virus_file.row_counter, row_data=data)
            update_scrollerbar_virus_file.row_counter += 1

            existing_paths.add(file_path)
    table_frame.after(200, update_scrollerbar_virus_file)


def create_table_ui(row_frame, size_font):
    active_virus_file_list = json_loading_active_virus()
    global table_frame

    table_frame = tk.CTkScrollableFrame(main_frame, label_text="Знайдені загрози!", 
                                        width = window_x-20-225-20-15, 
                                        # height = 200,
                                        label_font = ("Times New Roman", size_font, "bold")
                                        )
    table_frame.grid(row = row_frame, column=0, padx=15, pady = (1, 15), sticky = 's', columnspan = 3)
    
    table_frame.grid_columnconfigure(0, weight=0) # Колонка с №
    table_frame.grid_columnconfigure(1, weight=3, minsize = 140) # Колонка "Шлях" (широка)
    table_frame.grid_columnconfigure(2, weight=0, minsize = 140) # Колонка "Дата"
    table_frame.grid_columnconfigure(3, weight=1) # Колонка "Інформація"


    # Створення заголовків
    headers = ["№", "Шлях", "Дата", "Інформація"]
    create_titles(master = table_frame, headers = headers)


    # Створення строк даних для знайдених загроз
    for row_index, row_data in enumerate(active_virus_file_list):
        add_rows_virus_table(master = table_frame, row_index = row_index, row_data = row_data)



row_add_scanned_file = 1
def add_scanned_file(path, master):
    global row_add_scanned_file
    time_now = datetime.now().strftime("%H:%M:%S")
    
    # 1. Колонка "Дата"
    date_label = tk.CTkLabel(
        master, 
        text = f'{time_now}', 
        fg_color="transparent",
    )
    date_label.grid(row=row_add_scanned_file, column=0, padx=(5, 1), pady=1, sticky="nsew")

    # 2. Колонка шлях
    path_label = tk.CTkLabel(
        master,
        text = f'{path}',
        fg_color="transparent",
        anchor="w",
        wraplength = window_x - 225 - 20 - 15 - 140 - 30,
        justify = "left"
    )
    path_label.grid(row=row_add_scanned_file, column=1, padx=(7, 5), pady=1, sticky="w", columnspan = 3)

    row_add_scanned_file += 1

    root.update_idletasks()
    master._parent_canvas.yview_moveto(1)






def stop_file_scanning(value):
    global stop_timer
    stop_timer = True

    global threat_stop_scan
    threat_stop_scan = True

    global elapsed_time
    elapsed_time = 0

    if value == 0:
        scan_files()
        enable_all_buttons_menu()
    elif value == 1:
        ...


def exit_program():
    global scanner_thread
    stop_file_scanning(1)

    if scanner_thread and scanner_thread.is_alive():
        scanner_thread.join(timeout = 1)

    if thread_sys_info and thread_sys_info.is_alive():
        thread_sys_info.join(timeout = 1)

    root.destroy()
    

def update_scrollerbar_from_buffer():
    global row_add_scanned_file
    with buffer_lock:
        while scanned_files_buffer:
            file_path = scanned_files_buffer.pop(0)
            add_scanned_file(path=file_path, master=frame_scroll_scanned_file)
    frame_scroll_scanned_file.after(100, update_scrollerbar_from_buffer)


def disable_all_buttons_menu():
    for btn in button_list:
        btn.configure(state = "disabled")


def enable_all_buttons_menu():
    for btn in button_list:
        btn.configure(state = "normal")


def messagebox_eroor(text):
    messagebox.showerror("ERROR", text)


def scan(path_folder):
    virus_file = []

    connect = sqlite3.connect('malware_hashes.db')
    cursor = connect.cursor()
    cursor.execute('SELECT hash FROM sha256')
    rows = cursor.fetchall()    
    
    global count, count_vir
    count = 0
    count_vir = 0
    try:
        for root, dirs, files in os.walk(path_folder):
            if "virused_files" in dirs:
                dirs.remove("virused_files")
            if threat_stop_scan:
                break
            for file in files:
                if threat_stop_scan:
                    break
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    print(f"Файл: {file_path}")
                    for (hash_value,) in rows:
                        if file_hash == hash_value:
                            virus_file.append(file_path)
                            print("VIRUS")
                            with buffer_lock_vir_file:
                                virused_files_buffer.append(file_path)
                            count_vir += 1
                    with buffer_lock:
                        scanned_files_buffer.append(file_path)
                    scaned_file__label.after(0, lambda: scaned_file__label.configure(
                        text = f"Проскановано файлів: {count}") if scaned_file__label.winfo_exists() else None)
                    count += 1
                except PermissionError:
                    print(f"Пропущено файл через відсутність доступу: {file_path}")
                except Exception as error:
                    print(f"Помилка при скануванні файлу: {file_path}: {error}")
                    messagebox_eroor(text = 'Виникла помилка при скануванні файлу!\n\nСпробуйте знову.')
        else: ...
    except Exception as error:
        print(f"Помилка при скануванні файлів: {file_path}: {error}")
        messagebox_eroor(text = 'Виникла помилка при скануванні файлів!\n\nСпробуйте знову.')

    global stop_timer
    stop_timer = True

    json_saving_info(scan_date = datetime.now().strftime("%d.%m.%Y"), threats_found = count_vir, scan_duration = result, files_scanned = count)
    global progress
    progress = 1

    enable_all_buttons_menu()

    connect.close()  


def ui_scan():
    main_frame.rowconfigure(0, weight = 0)
    main_frame.rowconfigure(1, weight = 0)
    main_frame.rowconfigure(2, weight = 0)
    main_frame.rowconfigure(3, weight = 0)
    main_frame.rowconfigure(4, weight = 1)
    main_frame.rowconfigure(5, weight = 1)
    main_frame.columnconfigure(0, weight = 1)

    global progress_bar
    progress_bar = tk.CTkProgressBar(main_frame, orientation = "horizontal", mode = "indeterminate", width = 500)
    progress_bar.grid(row = 0, column = 0, pady = (20, 20), padx = 15, sticky = 'w')
    progress_bar.start()  # Прогрес бар

    time_scanning, files_scanned = '...', '...'

    global timer_label
    timer_label = tk.CTkLabel(main_frame, text = f"Сканування триває: {time_scanning}", font = ("Times New Roman", 20), justify = "left")
    timer_label.grid(row = 1, column = 0, padx = 15, pady = (10, 2), sticky = "w")

    global scaned_file__label
    scaned_file__label = tk.CTkLabel(main_frame, text = f"Проскановано файлів: {files_scanned}", font = ("Times New Roman", 20), justify = "left")
    scaned_file__label.grid(row = 2, column = 0, padx = 15, pady = (2, 10), sticky = "w")

    global but_stop_file_scanning
    but_stop_file_scanning = tk.CTkButton(main_frame, text = 'Зупинити сканування', font = ("Times New Roman", 19), text_color = 'black', command = lambda: stop_file_scanning(0), width = 150, height = 30)
    but_stop_file_scanning.grid(row = 3, column = 0, padx = 15, pady = 10, sticky = "w")

    global frame_scroll_scanned_file
    frame_scroll_scanned_file = tk.CTkScrollableFrame(main_frame, label_text = 'Проскановані файли', label_font = ("Times New Roman", 17, "bold"))
    frame_scroll_scanned_file.grid(row = 4, column = 0, padx = 15, pady = 10, sticky = 'ew')

    frame_scroll_scanned_file.grid_columnconfigure(0, weight = 1) # Колонка "Час"
    frame_scroll_scanned_file.grid_columnconfigure(1, weight = 4, minsize = 140) # Колонка "Файл" (широка)

    # headers = ["Час", "Файл"]
    # create_titles(master = frame_scroll_scanned_file, headers = headers)
    create_table_ui(row_frame = 5, size_font = 17)


scanner_thread = None
def start_file_scanning():
    if entry_path != None:
        path_folder = entry_path.get()
        if path_folder != '':
            if not os.path.isdir(path_folder):
                print(f"Помилка: {path_folder} не є директорією.")
                return []
        else: 
            messagebox_eroor(text = "Ви не вказали ніякий шлях або вказали пустий рядок замість шляху у папку сканування.\n\nВкажіть шлях до папки, яку треба сканувати.")
            return
    else:
        messagebox_eroor(text = "Ви не вказали ніякий шлях до папки сканування.\n\nВкажіть шлях до папки, яку треба сканувати.")
        return
    print('true')


    destroy_widgets()

    global threat_stop_scan, stop_timer, elapsed_time
    threat_stop_scan = False
    stop_timer = False
    elapsed_time = 0
    
    global scanned_files_buffer, buffer_lock, virused_files_buffer, buffer_lock_vir_file, scanner_thread
    scanned_files_buffer = []
    buffer_lock = threading.Lock()
    virused_files_buffer = []
    buffer_lock_vir_file = threading.Lock()

    scanner_thread = threading.Thread(target = scan, args = (path_folder, ))
    scanner_thread.daemon = True
    scanner_thread.start()
    
    ui_scan()

    update_scrollerbar_from_buffer()
    update_scrollerbar_virus_file()
    update_timer()
    global progress
    progress = 0
    update_progressbar_and_button()

    disable_all_buttons_menu()


    














###################################


def scan_files():
    set_active_button(0)
    destroy_widgets()
    

    # progress_bar = tk.CTkProgressBar(main_frame, orientation = "horizontal", mode = "indeterminate", width = 400)
    # progress_bar.pack(pady = 20)
    # progress_bar.start()  # Запуск анимации прогресс-бара
    global entry_path
    date, threats, duration, files = json_loading_info()
    # json_saving_info(1, 2, "00:05:23", 1200)


    def empty_values(value, default = ''):
        if value == "...":
            return 'інформація відсутня' + default
        return value
    

    label = tk.CTkLabel(main_frame, text = f"Останнє завершене сканування: {empty_values(value = date, default = '.')}\nЗнайдено загроз: {empty_values(value = threats)}.\nПеревірка тривала: {empty_values(value = duration, default = '.')}\nПеревірено файлів: {empty_values(value = files)}.", font = ("Times New Roman", 20), justify = "left")
    label.grid(row = 0, column = 0, padx = 15, pady = (10, 10), sticky = "w")

    entry_path = tk.CTkEntry(main_frame, width = 450, font = ("Times New Roman", 20), height = 30)
    entry_path.grid(row = 1, column = 0, padx = 15, pady = (10, 10), sticky = "ew")

    button_path = tk.CTkButton(main_frame, text = "Обрати папку", font = ("Times New Roman", 19), 
                            #    fg_color = "#23AEC7", 
                               text_color = 'black', command = lambda: select_directory(), width = 150, height = 30)
    button_path.grid(row = 1, column = 1, padx = 15, pady = (10, 10))

    button_check = tk.CTkButton(main_frame, text = "Почати сканування", font = ("Times New Roman", 22), 
                                # fg_color = "#23AEC7", 
                                text_color = 'black', command = lambda: start_file_scanning(), width = 240, height = 40)
    button_check.grid(row = 2, column = 0, padx = 15, pady = (10, 10), sticky = "w")

    create_table_ui(row_frame = 3, size_font = 20)


def event_log():
    set_active_button(1)
    destroy_widgets()

    button_save_event_log = tk.CTkButton(main_frame, text = "Зберегти журнал подій у файл", font = ("Times New Roman", 19), text_color = 'black', command = lambda: save_file_event_logs(), height = 30)
    button_save_event_log.pack(pady = (10, 10), padx = 15, fill = 'both', side = 'bottom')

    scroll_bar = tk.CTkScrollableFrame(main_frame, label_text = "Журнал подій", label_font = ("Times New Roman", 20, "bold"))
    scroll_bar.pack(fill = "both", pady = (10, 10), padx = 15, expand = True)

    scroll_bar.grid_columnconfigure(0, weight=0) # Колонка "Дата"
    scroll_bar.grid_columnconfigure(1, weight=3, minsize = 140) # Колонка "Подія" (широка)

    # --- Створення заголовків ---
    headers = ["Дата", "Подія"]
    create_titles(master = scroll_bar, headers = headers)

    loaded_event_logs = json_loading_event_logs()
    if loaded_event_logs == []:
        tk.CTkLabel(scroll_bar, text = "Журнал подій порожній.", fg_color = "transparent", font = ("Times New Roman", 24, "bold")).grid(row = 1, column = 0, padx = 5, pady = 15, sticky = "nsew", columnspan = 2)
        return
    for row_index, row_data in enumerate(loaded_event_logs):
        # 1. Колонка "Дата"
        date_label = tk.CTkLabel(
            scroll_bar, 
            text = f'{row_data[0]}', 
            fg_color="transparent",
        )
        date_label.grid(row=row_index + 1, column=0, padx=(5, 10), pady=1, sticky="nsew")

        # 2. Колонка "Подія"
        event_label = tk.CTkLabel(
            scroll_bar, 
            text = f'{row_data[1]}', 
            fg_color="transparent",
            anchor="w",
            wraplength = window_x-225-20-15-140-30,
            justify = "left"
            )
        event_label.grid(row=row_index + 1, column=1, padx=(5, 5), pady=1, sticky="w")


def quarantine():
    set_active_button(2)
    destroy_widgets()

    scroll_bar = tk.CTkScrollableFrame(main_frame, label_text="Карантин", label_font=("Times New Roman", 20, "bold"))
    scroll_bar.pack(fill="both", expand=True, padx=15, pady=10)

    # Настройка колонок
    scroll_bar.grid_columnconfigure(0, weight=0)  # №
    scroll_bar.grid_columnconfigure(1, weight=4)  # Путь
    scroll_bar.grid_columnconfigure(2, weight=1)  # Кнопка info
    scroll_bar.grid_columnconfigure(3, weight=1)  # Восстановить
    scroll_bar.grid_columnconfigure(4, weight=1)  # Удалить

    headers = ["№", "Шлях", "Інфо", "Відновити", "Видалити"]
    create_titles(scroll_bar, headers)

    quarantine_data = json_loading_quarantine()
    # for idx, (file_id, entry) in enumerate(quarantine_data.items()):
    for idx, entry in enumerate(quarantine_data):
        file_id = entry["id"]
        # №
        tk.CTkLabel(scroll_bar, text=str(idx+1), fg_color="transparent").grid(row=idx+1, column=0, padx=5, pady=1)

        # Путь
        tk.CTkLabel(scroll_bar, text=entry["original_path"], fg_color="transparent", anchor="w", wraplength=400).grid(row=idx+1, column=1, sticky="w")

        # Info кнопка
        tk.CTkButton(scroll_bar, text="Додатково", width=100, height=25,
                     command=lambda: show_quarantine_info(entry)).grid(row=idx+1, column=2)

        # Восстановить
        tk.CTkButton(scroll_bar, text="Відновити", width=100, height=25,
                     command=lambda: restore_from_quarantine(file_id)).grid(row=idx+1, column=3)

        # Удалить
        tk.CTkButton(scroll_bar, text="Видалити", width=100, height=25,
                     command=lambda: delete_from_quarantine(file_id)).grid(row=idx+1, column=4)
    

def system_info():
    set_active_button(3)
    destroy_widgets()

    scroll_bar = tk.CTkScrollableFrame(main_frame, label_text = "Інформація про систему", label_font = ("Times New Roman", 20, "bold"))
    scroll_bar.pack(fill = "both", pady = (10, 10), padx = 15, expand = True)
    scroll_bar.grid_columnconfigure(0, weight=1, minsize = 140) # Колонка "Назва"
    scroll_bar.grid_columnconfigure(1, weight=3, minsize = 140) # Колонка "Значення" (широка)

    headers = ["Назва", "Значення"]
    create_titles(master = scroll_bar, headers = headers)

    # 1 Звичайні поля
    row = 1
    for key, value in system_information.items():
        if key not in ("Disks", "IP Addresses"):
            tk.CTkLabel(scroll_bar, text=key, anchor="w").grid(
                row=row, column=0, sticky="w", padx = (10, 5), pady=2)
            if key == 'Logged Users':
                tk.CTkLabel(scroll_bar, text=", ".join(value), anchor="w", wraplength=450).grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
            else:
                tk.CTkLabel(scroll_bar, text=str(value), anchor="w", wraplength=450).grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
            row += 1
            continue

        # 2 DISKS
        if key == "Disks":
            tk.CTkLabel(scroll_bar, text="Disks", font=("Arial", 14, "bold"), anchor="w").grid(
                row = row, column = 0, sticky = "w", padx = 5, pady = (10, 2))
            row += 1

            for disk, disk_info in value.items():
                # Назва диску
                tk.CTkLabel(scroll_bar, text=f"• {disk}", anchor="w").grid(
                    row=row, column=0, sticky="w", padx=15, pady=2)
                row += 1

                # Значення диску
                for param, param_value in disk_info.items():
                    tk.CTkLabel(scroll_bar, text=f"   {param}", anchor="w").grid(
                        row=row, column=0, sticky="w", padx=25, pady=1)
                    tk.CTkLabel(scroll_bar, text=str(param_value), anchor="w").grid(
                        row=row, column=1, sticky="w", padx=10, pady=1)
                    row += 1
            continue

        # 3. IP Addresses
        if key == "IP Addresses":
            tk.CTkLabel(scroll_bar, text="IP Addresses", font=("Arial", 14, "bold"), anchor="w").grid(
                row=row, column=0, sticky="w", padx=5, pady=(10, 2))
            row += 1

            for iface, ip_list in value.items():
                tk.CTkLabel(scroll_bar, text=f" {iface}", anchor="w").grid(
                    row=row, column=0, sticky="w", padx=15, pady=2)
                
                tk.CTkLabel(scroll_bar, text=", ".join(ip_list), anchor="w").grid(
                    row=row, column=1, sticky="w", padx=10, pady=2)
                row += 1


def update_app():
    set_active_button(4)
    destroy_widgets()

    scroll_bar = tk.CTkScrollableFrame(main_frame, label_text = "Інформація про оновлення", label_font = ("Times New Roman", 20, "bold"))
    scroll_bar.pack(fill = "both", pady = (10, 10), padx = 15, expand = True)
    scroll_bar.grid_columnconfigure(0, weight = 1) # Колонка "Версія"
    scroll_bar.grid_columnconfigure(1, weight = 1) # Колонка "Дата"
    scroll_bar.grid_columnconfigure(2, weight = 2, minsize = 140) # Колонка "Зміни" (широка)

    headers = ["Версія", "Дата", "Зміни"]
    create_titles(master = scroll_bar, headers = headers)

    loaded_versions = json_loading_versions()
    if loaded_versions == {}:
        tk.CTkLabel(scroll_bar, text = "Інформація про оновлення відсутня.", fg_color = "transparent", font = ("Times New Roman", 24, "bold")).grid(row = 1, column = 0, padx = 5, pady = 15, sticky = "nsew", columnspan = 4)
        return
    else:
        row = 1
        for ver in loaded_versions:
            # 1. Колонка "Версія"
            tk.CTkLabel(
                    scroll_bar, 
                    text = f'{ver}', 
                    fg_color="transparent",
                    anchor = 'center',
                    font = ("Times New Roman", 14)
                ).grid(row=row, column=0, padx=(1, 1), pady=1, sticky="nsew")
            
            # Отримуємо дату та зміни
            date, changes = (loaded_versions[ver]['date'], loaded_versions[ver]['changes'])

            # 2. Колонка "Дата"
            tk.CTkLabel(
                scroll_bar, 
                text = f'{date}', 
                fg_color="transparent",
                anchor = 'center',
                font = ("Times New Roman", 14)
            ).grid(row=row, column=1, padx=(1, 1), pady=1, sticky="nsew")

            # 3. Колонка "Зміни"
            tk.CTkLabel(
                scroll_bar, 
                text = f'{changes}', 
                fg_color="transparent",
                anchor="w",
                wraplength = window_x-225-20-15-140-30,
                font = ("Times New Roman", 14),
                justify = "left"
            ).grid(row=row, column=2, padx=(5, 5), pady=1, sticky="w")
            row += 1
    

def settings():
    set_active_button(5)
    destroy_widgets()

    label = tk.CTkLabel(main_frame, text = 'Наразі, налаштування відсутні.', font = ('Times New Roman', 20, 'bold'))
    label.pack(padx = 15, pady = 15, fill = 'both')
    

def about():
    set_active_button(6)
    destroy_widgets()

    # Створюємо звичайний tk.Text (замість CTkTextbox) для підтримки форматування
    textbox = Text(main_frame, wrap = "word", bg = "#cad2c5", fg = "black", font = ("Times New Roman", 14), borderwidth = 0, highlightthickness = 0)
    textbox.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'nsew')

    # Налаштування шрифту для тексту
    bold_font = ("Times New Roman", 14, "bold")
    textbox.tag_config("bold", font = bold_font)
    font_program_name = ('Times New Roman', 24, "bold")
    textbox.tag_config("font_program_name", font = font_program_name)
    
    app_info = json_loading_app_info()
    if app_info == {}:
        main_frame.grid_columnconfigure(0, weight = 1)
        tk.CTkLabel(main_frame, text = "Інформація про програмне забезпечення відсутня.", fg_color = "transparent", font = ("Times New Roman", 24, "bold")).grid(row = 0, column = 0, ipadx = 5, pady = 10, sticky = "nsew")
        return
    else:
        main_frame.grid_columnconfigure(0, weight = 0)
        info = app_info["SentinelGuard Antivirus"]

        program_name = list(app_info.keys())[0] # Виводимо назву програмного забезпечення
        textbox.insert("0.0", program_name + '\n\n', "font_program_name")

        for key, value in info.items():
            if key == "Можливості:":
                textbox.insert("end", f"{key}\n", "bold")
                for item in value:
                    textbox.insert("end", f"• {item}\n")
                textbox.insert("end", "\n")
            else:
                if key == "Опис:":
                    textbox.insert("end", f"\n{key} ", "bold")
                    textbox.insert("end", f"{value}\n\n")
                else:
                    textbox.insert("end", f"{key} ", "bold")
                    textbox.insert("end", f"{value}\n")
    textbox.configure(state="disabled")  # Заборона зміни тексту користувачем




root = tk.CTk()
window_x = 1000; window_y = 580
w = (root.winfo_screenwidth() // 2) - (window_x // 2)
h = (root.winfo_screenheight() // 2) - (window_y // 2)

root.geometry(f"{window_x}x{window_y}+{w}+{h}") 
root.resizable(False, False)
root.title("SentinelGuard Antivirus")

tk.set_appearance_mode("Light")
tk.set_default_color_theme("blue")

menu_frame = tk.CTkFrame(root, fg_color = "#2f3e46", width = 225, corner_radius = 0)
menu_frame.pack(side = "left", fill = "y")
menu_frame.pack_propagate(False)

buttons_data = [
    ("Сканування файлів", scan_files),
    ("Журнал подій", event_log),
    ("Карантин", quarantine),
    ("Інформація про систему", system_info),
    ("Оновлення", update_app),
    ("Налаштування", settings),
    ("Про програму", about)
]

button_list = []  # Список для хранения кнопок, чтобы обновлять их цвета
active_button_index = None  # Индекс активной кнопки


def create_menu_buttons(text, command, pady = (2, 2), value_button = 0):
    btn = tk.CTkButton(menu_frame, text = text, fg_color = "#354f52", text_color = "white", command = command, height = 40, width = 75)
    btn.pack(fill = "x", pady = pady, padx = (2, 2))
    btn.pack_propagate(False)
    if value_button == 1:
        ...
    else:
        button_list.append(btn)


for i, (text, command) in enumerate(buttons_data):
    if i == 0:
        create_menu_buttons(text = text, command = command, pady = (3, 2))
    else:
        create_menu_buttons(text = text, command = command)
create_menu_buttons(text = "Вихід", command = lambda: exit_program(), pady = (window_y-(len(buttons_data) * 44)-44, 3), value_button = 1)

main_frame = tk.CTkFrame(root, fg_color = "#cad2c5", corner_radius = 0)
main_frame.pack(side = "right", expand = True, fill = "both")
main_frame.grid_rowconfigure(0, weight=0)  # верх - фиксированный
main_frame.grid_rowconfigure(1, weight=0)
main_frame.grid_rowconfigure(2, weight=0)
main_frame.grid_rowconfigure(3, weight=1)  # таблица тянется вниз

scan_files()


root.mainloop()


