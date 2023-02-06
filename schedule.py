import pandas as pd
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk


class Schedule(Frame):
    # Cоздание атрибутов класса

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent  # Сохранение ссылки на корневое окно
        self.init_ui()  # Загружаем пользовательский интерфейс
        # self.grid()
        # self.configure(background = "white")
        # self.eng, self.trans = str(), str()

        # self.message.grid(row = 1, column = 0, columnspan = 2, sticky = W + E)

    def init_ui(self):
        # Заголовок окна
        self.parent.title('Система создания школьного расписания')
        self.pack(fill=BOTH, expand=True)

        # Создаем вкладки
        tab_control = ttk.Notebook(self)
        tab_files = Frame(tab_control)  # Вкладка с загрузками файлов
        tab_parameters = Frame(tab_control)  # Вкладка с параметрами расписания

        tab_control.add(tab_files, text='Начальные данные')
        tab_control.add(tab_parameters, text='Параметры расписания')
        tab_control.pack(expand=1, fill="both")

        # Добавляем фреймы на первую вкладку
        frame_academic_plan = LabelFrame(tab_files, text="Учебный план", relief=RAISED, borderwidth=1)
        frame_academic_plan.pack(fill=BOTH, expand=True)

        frame_teachers = LabelFrame(tab_files, text="Специализация учителей", relief=RAISED, borderwidth=1)
        frame_teachers.pack(fill=BOTH, expand=True)

        frame_audiences = LabelFrame(tab_files, text="Аудитории", relief=RAISED, borderwidth=1)
        frame_audiences.pack(fill=BOTH, expand=True)

        frame_audiences_lessons = LabelFrame(tab_files, text="Соответствие типа аудитории предмету", relief=RAISED, borderwidth=1)
        frame_audiences_lessons.pack(fill=BOTH, expand=True)

        frame_calls = LabelFrame(tab_files, text="Расписание звонков", relief=RAISED, borderwidth=1)
        frame_calls.pack(fill=BOTH, expand=True)

        # Выход из программы
        quit_button = Button(self, text="Закрыть", command=self.quit)
        quit_button.pack(side=RIGHT, padx=10, pady=10)

    def load_df(self):
        fn = filedialog.Open(self.parent, filetypes=[('*.csv files', '.csv')]).show()
        if fn == '':
            return
        else:
            df = pd.read_csv(fn)

    def quit(self):
        if messagebox.askyesno("Выйти", "Закрыть программу?"):
            self.parent.destroy()


def main():
    # создаем корневое окно
    root = Tk()
    root.geometry("400x250+0+0")
    app = Schedule(root)
    root.mainloop()


if __name__ == '__main__':
    main()
