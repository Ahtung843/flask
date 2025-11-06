from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Файл для записи полученных данных
OUTPUT_FILE = "received_file_paths.txt"

@app.route('/receive_files', methods=['POST'])
def receive_files():
    """
    Обрабатывает POST запросы, содержащие список путей к файлам.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415 # Unsupported Media Type

    data = request.get_json()
    file_list = data.get("files", [])

    if not file_list:
        return jsonify({"message": "No files received."}), 200

    print(f"Получено {len(file_list)} файлов от клиента.")
    print("Список полученных файлов:")
    for file_path in file_list:
        print(f"- {file_path}")

    # Записываем полученные пути в файл
    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for file_path in file_list:
                f.write(file_path + "\n")
        print(f"Данные успешно сохранены в файл: {OUTPUT_FILE}")
        return jsonify({"message": f"Successfully received {len(file_list)} file paths."}), 200
    except IOError as e:
        print(f"Ошибка записи в файл {OUTPUT_FILE}: {e}")
        return jsonify({"error": f"Could not write to output file: {e}"}), 500


if __name__ == '__main__':
    # --- Настройки сервера ---
    # Выберите, на каком IP-адресе и порту сервер будет слушать.
    # '0.0.0.0' означает, что сервер будет доступен по всем сетевым интерфейсам.
    # Это важно, чтобы другие компьютеры в сети могли к нему подключиться.
    # '127.0.0.1' (localhost) будет слушать только на текущем компьютере.
    server_ip = '0.0.0.0'
    server_port = 5000 # Можете выбрать другой порт, если этот занят

    print(f"Запуск сервера на {server_ip}:{server_port}")
    print(f"Данные будут сохраняться в: {OUTPUT_FILE}")
    print("Нажмите Ctrl+C для остановки сервера.")
    app.run(host=server_ip, port=server_port, debug=True) # debug=False для продакшена
