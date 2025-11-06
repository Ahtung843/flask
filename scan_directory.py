import os
import requests
import json # Для отправки данных в формате JSON

def scan_directory_and_send(start_dir, server_url):
    """
    Сканирует указанную директорию и ее поддиректории,
    собирает полные пути к файлам и отправляет их на сервер.

    Args:
        start_dir (str): Путь к начальной директории для сканирования.
        server_url (str): URL сервера, на который будут отправляться данные.
                          Пример: "http://192.168.1.100:5000/receive_files"
    """
    print(f"Сканирование директории: {start_dir}")
    found_files = [] # Список для хранения найденных файлов

    try:
        for current_dir, subdirs, files in os.walk(start_dir):
            for file in files:
                file_path = os.path.join(current_dir, file)
                print(f"Найден файл: {file_path}")
                found_files.append(file_path)

        print("\nСканирование завершено.")

        # Отправка данных на сервер, если есть найденные файлы
        if found_files:
            print(f"Отправка {len(found_files)} файлов на сервер: {server_url}")
            try:
                # Отправляем список файлов в формате JSON
                response = requests.post(server_url, json={"files": found_files})
                response.raise_for_status() # Вызовет исключение для плохих статусов (4xx или 5xx)
                print(f"Данные успешно отправлены. Ответ сервера: {response.status_code}")
                print(f"Сообщение сервера: {response.text}")
            except requests.exceptions.ConnectionError:
                print(f"Ошибка: Не удалось подключиться к серверу по адресу {server_url}.")
                print("Убедитесь, что сервер запущен и доступен.")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при отправке данных на сервер: {e}")
        else:
            print("Файлы не найдены. Отправлять нечего.")

    except FileNotFoundError:
        print(f"Ошибка: Директория '{start_dir}' не найдена.")
    except PermissionError:
        print(f"Ошибка: Отказано в доступе к директории '{start_dir}' или ее поддиректориям.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    # --- Настройки клиента ---
    # Запрашиваем у пользователя директорию
    directory_to_scan = input("Введите полный путь к директории для сканирования (или нажмите Enter для текущей директории): ")
    if not directory_to_scan:
        directory_to_scan = "." # Если ввод пустой, сканируем текущую директорию

    # !!! ВАЖНО: Укажите URL вашего сервера !!!
    # Если сервер запущен на том же компьютере: http://127.0.0.1:5000/receive_files
    # Если сервер на другом компьютере в локальной сети: http://<IP-адрес-сервера>:5000/receive_files
    # Если сервер доступен через интернет: http://<публичный-IP-или-домен>:5000/receive_files
    server_address = input("Введите URL сервера для отправки данных (например, http://127.0.0.1:5000/receive_files): ")
    if not server_address:
        print("URL сервера не указан. Невозможно отправить данные.")
    else:
        scan_directory_and_send(directory_to_scan, server_address)

