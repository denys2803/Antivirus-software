import json
from tkinter import filedialog
from datetime import datetime
import os


path_scans = './scans.json'
path_event_logs = './event_logs.json'
path_versions_file = './versions.json'
path_app_info = './app_info.json'
path_active_virus = './active_virus.json'
path_quarantine_json = './quarantine.json'


def convert_time(t: str): # Конвертувати час з формату "HH:MM:SS" у формат "X г. Y хв. Z сек."
    h, m, s = map(int, t.split(":"))
    parts = []
    if h > 0:
        parts.append(f"{h} год.")
    if m > 0:
        parts.append(f"{m} хв.")
    if s > 0 or (h == 0 and m == 0):
        parts.append(f"{s} сек.")
    return " ".join(parts)


def json_loading_info(): # Завантажити інформацію з JSON
    try:
        with open(path_scans, 'r', encoding = 'UTF-8') as file:
            file_information = json.load(file)
            information = file_information[f'{len(file_information)}']
            date, threats, duration, files = (information["scan_date"], 
                                            information["threats_found"], 
                                            information["scan_duration"], 
                                            information["files_scanned"])
            return date, threats, duration, files
    except Exception as error:
        print(f"Ошибка при загрузке JSON: {error}")
        return "...", "...", "...", "..."


def json_saving_info(scan_date, threats_found, scan_duration, files_scanned): # Зберегти інформацію у JSON
    try:
        try:
            with open(path_scans, 'r', encoding='UTF-8') as file:
                content = file.read().strip()
            if not content:
                file_information = {}
            else:
                file_information = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            file_information = {}
        file_information[f'{len(file_information) + 1}'] = {
            "scan_date": scan_date,
            "threats_found": threats_found,
            "scan_duration": scan_duration,
            "files_scanned": files_scanned
        }
        with open(path_scans, 'w', encoding = 'UTF-8') as file:
            json.dump(file_information, file)
    except Exception as error:
        print(f"Ошибка при сохранении JSON: {error}")


def json_loading_event_logs():
    try:
        with open(path_event_logs, 'r', encoding = 'UTF-8') as file:
            file_information = json.load(file)
            event_logs = []
            for key in file_information:
                info = file_information[key]
                event_logs.append((info["date"], info["event"]))
            return event_logs
    except Exception as error:
        print(f"Ошибка при загрузке JSON: {error}")
        return []


def json_saving_event_logs(event_date, event_description):
    try:
        try:
            with open(path_event_logs, 'r', encoding='UTF-8') as file:
                content = file.read().strip()
            if not content:
                file_information = {}
            else:
                file_information = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            file_information = {}
        file_information[f'{len(file_information) + 1}'] = {
            "date": event_date,
            "event": event_description
        }
        with open(path_event_logs, 'w', encoding = 'UTF-8') as file:
            json.dump(file_information, file)
    except Exception as error:
        print(f"Ошибка при сохранении JSON: {error}")


def save_file_event_logs():
        file_path = filedialog.asksaveasfilename(defaultextension = ".txt", title = "Зберегти журнал подій як...", initialfile = 'Event_logs.txt',
                                                 filetypes = [("Text files", "*.txt"), 
                                                            ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    loaded_event_logs = json_loading_event_logs()
                    file.write("Журнал подій SentinelGuard Antivirus\n\n\nДата | Подія\n\n")
                    for row_data in loaded_event_logs:
                        file.write(f"{row_data[0]} | {row_data[1]}\n")
                    file.write(f"\n\nЗбережено {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} за допомогою SentinelGuard Antivirus")
            except Exception as e:
                print(f"Помилка при збереженні файлу: {e}")


def json_loading_versions():
    try:
        with open(path_versions_file, 'r', encoding = 'UTF-8') as file:
            versions_info = json.load(file)
            return versions_info
    except Exception as error:
        print(f"Поилка при завантаженні JSON: {error}")
        return {}


def json_loading_app_info():
    try:
        with open(path_app_info, 'r', encoding = 'UTF-8') as file:
            app_info = json.load(file)
            return app_info
    except Exception as error:
        print(f"Ошибка при загрузке JSON: {error}")
        return {}
    

def json_loading_active_virus():
    try:
        with open(path_active_virus, 'r', encoding = 'UTF-8') as file:
            file_information = json.load(file)
            active_virus_list = []
            for key in file_information:
                info = file_information[key]
                active_virus_list.append((info["path"], info["date"], info["concurrence"]))
            return active_virus_list
    except Exception as error:
        print(f"Ошибка при загрузке JSON: {error}")
        return []


def json_saving_active_virus(date, path, concurrence):
    try:
        try:
            with open(path_active_virus, 'r', encoding='UTF-8') as file:
                content = file.read().strip()
            if not content:
                file_information = {}
            else:
                file_information = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            file_information = {}
        file_information[f'{len(file_information) + 1}'] = {
            "date": date,
            "path": path,
            "concurrence": concurrence
        }
        with open(path_active_virus, 'w', encoding = 'UTF-8') as file:
            json.dump(file_information, file)
    except Exception as error:
        print(f"Ошибка при сохранении JSON: {error}")


def get_rows_form_virus_file():
    try:
        try:
            with open(path_active_virus, 'r', encoding='UTF-8') as file:
                content = file.read().strip()
            if not content:
                file_information = {}
            else:
                file_information = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            file_information = {}
        return len(file_information) 
    except Exception as error:
        print(f"Ошибка при загрузке JSON: {error}")


def json_loading_quarantine():
    # if not os.path.exists(path_quarantine_json):
    #     return {}
    # with open(path_quarantine_json, "r", encoding="utf-8") as f:
        # return json.load(f)
    


    try:
        with open(path_quarantine_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Если это список НЕ словарей → конвертируем
        fixed = []
        for entry in data:
            if isinstance(entry, dict):
                fixed.append(entry)
            elif isinstance(entry, list) and len(entry) == 6:
                fixed.append({
                    "id": entry[0],
                    "original_path": entry[1],
                    "quarantine_path": entry[2],
                    "found_time": entry[3],
                    "moved_time": entry[4],
                    "analysis_type": entry[5]
                })
            else:
                print("Неизвестный формат:", entry)
        return fixed
    except:
        return []
    




# def json_loading_quarantine():
#     if not os.path.exists(path_quarantine_json):
#         return {}

#     try:
#         with open(path_quarantine_json, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         if isinstance(data, list):
#             converted = {}
#             for idx, entry in enumerate(data, start=1):
#                 converted[str(idx)] = {
#                     "id": idx,
#                     "original_path": entry[0],
#                     "quarantine_path": entry[0], 
#                     "found_time": entry[1] if len(entry) > 1 else "",
#                     "moved_time": entry[1] if len(entry) > 1 else "",
#                     "analysis_type": entry[2] if len(entry) > 2 else "unknown"
#                 }
#             return converted
#         if isinstance(data, dict):
#             return data

#         return {}

#     except:
#         return {}






    
def json_save_quarantine(data):
    with open(path_quarantine_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)