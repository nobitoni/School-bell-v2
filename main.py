import customtkinter
from CTkMessagebox import CTkMessagebox
import os
import urllib.request
from datetime import datetime
import json
import time
import pyperclip
from multiprocessing import Process
import winsound
from threading import Thread


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.current_time = None

        # Назначаем процессы для работы в разных потоках
        self.bell = Process(target=self.bell_bell)
        self.time_checker_process = Thread(target=self.time_checker)
        self.time_checker_process.daemon = True  # Завершится вместе с основным потоком
        self.time_checker_process.start()

        # Конфигурация окна
        self.title("Школьный звонок")
        self.geometry(f"{1200}x{600}")
        self.resizable(width=False, height=False)
        self.iconbitmap('resources/ico.ico')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Обработка закрытия программы
        self.current_time = time.strftime("%H:%M:%S")

        # Создаём часы
        self.clock = customtkinter.CTkLabel(self, padx=35, pady=30, font=("Helvetica", 30))

        # Создание окна с расписанием
        txt = self.call_schedule()
        self.textbox = customtkinter.CTkTextbox(self, width=300, height=200, font=("Helvetica", 14), activate_scrollbars=False)
        self.textbox.insert("0.0", txt)

        # Создаём кнопку звонок, для подачи звонка в случае ЧС
        self.btn_call = customtkinter.CTkButton(self, text="Звонок", font=("Helvetica", 30),
                                                command=self.first_step_bell)

        # Упаковка
        self.clock.pack(anchor="ne")
        self.textbox.pack(anchor="center")
        self.btn_call.pack(anchor="se", pady=130, padx=30)

        # Вызываем метод для первоначального обновления времени
        self.how_time()

    def first_step_bell(self):
        self.bell = Process(target=self.bell_bell)
        self.bell.start()

    @staticmethod
    def call_schedule() -> str:
        txt =("""
    1 смена                            2 смена
1 урок:6:24-8:40           1 урок:14:00-14:40
2 урок:8:45-9:25           2 урок:14:55-15:10
3 урок:9:40-10:20         3 урок:15:50-16:00
4 урок:10:35-11:15       4 урок:16:35-17:15
5 урок:11:30-12:10       5 урок:17:20-18:00
6 урок:12:25-13:05       6 урок:18:05-18:45
7 урок:13:10-13:50

            """)
        return txt

    def time_checker(self) -> None:
        # Считываем расписание звонков с json файла
        from_lesson = []
        to_lesson = []
        with open('resources/timetable.json', 'r') as file:
            timetable = json.load(file)
        for shift in timetable.values():
            for lesson_info in shift:
                time_range = lesson_info["time"]
                start_time, end_time = time_range.split(" - ")
                to_lesson.append(start_time)
                from_lesson.append(end_time)
        while True:
            current_time = str(time.strftime("%H:%M"))[1:]
            if current_time in to_lesson or current_time in from_lesson:
                self.bell.start()
                time.sleep(50)
            time.sleep(10)

    def how_time(self) -> None:
        # Обновляем время в clock (label)
        self.current_time = time.strftime("%H:%M")
        self.clock.configure(text=self.current_time)
        self.after(100, self.how_time)

    @staticmethod
    def bell_bell() -> None:
        winsound.PlaySound('resources/Bell.wav', winsound.SND_FILENAME)

    def on_closing(self) -> None:
        close_msg = CTkMessagebox(title="Выход?", message="Вы хотите закрыть программу?",
                                  icon="question", option_1="Нет", option_2="Да")
        close_response = close_msg.get()
        if close_response == "Да":
            try:
                self.bell.terminate()
            except AttributeError:
                pass
            finally:
                time.sleep(1)
                exit()


def main() -> None:
    # Получение текущей даты
    current_date = datetime.now()

    # Получение текущего года
    year = current_date.year

    # Читаем календарь
    # Получение номера текущего месяца
    current_month = current_date.month

    # Чтение JSON-файла
    with open('resources/calendar.json', 'r') as file:
        data = json.load(file)

    # Проверка на существование файла и соответствие года
    if not (os.path.exists('resources/calendar.json')) or not (int(data["year"]) == year):
        download_calendar(year)

    # Извлечение информации о днях в месяце с номером 4
    month_week_days = None
    for entry in data["months"]:
        if entry["month"] == current_month:
            month_week_days = entry["days"].split(',')
            break

    # Получение текущего календарного числа
    current_day = current_date.day
    day_of_week = current_date.weekday()  # 0 - понедельник, 6 - воскресенье.

    # Проверка на выходной день
    if (current_day in month_week_days) or (day_of_week > 5):
        week_msg = CTkMessagebox(title="Exit?", message=f"Сегодня выходной день.\nЗакрыть программу?",
                                 icon="question", option_1="Нет", option_2="Да")
        response = week_msg.get()
        if response == "Да":
            exit()
        else:
            application_start()
    else:
        application_start()


def application_start() -> None:
    customtkinter.set_appearance_mode("system")
    app = App()
    app.mainloop()


def download_calendar(year) -> None:
    # Скачиваем календарь
    url = f'https://xmlcalendar.ru/data/ru/{year}/calendar.json'
    project_folder = 'resources'
    file_name = 'calendar.json'

    # Сформируем путь сохранения, объединив путь к проекту и имя файла
    destination_path = os.path.join(project_folder, file_name)

    # Создадим директорию, если её нет
    os.makedirs(project_folder, exist_ok=True)

    # Скачиваем файл и сохраняем его
    urllib.request.urlretrieve(url, destination_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        error_msg = CTkMessagebox(title="Error", message=f"Ошибка: {error}",
                                  icon="cancel", option_1="Скопировать", option_2="OK")
        error_response = error_msg.get()
        if error_response == "Скопировать":
            pyperclip.copy(str(error))
        time.sleep(0.1)
        exit()
