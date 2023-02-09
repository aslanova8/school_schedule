import pandas as pd
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk


class Schedule(Frame):
    # Cоздание атрибутов класса

    # Датафреймы с вводными для расписания
    df_teachers = pd.DataFrame
    df_audiences = pd.DataFrame
    df_audiences_lessons = pd.DataFrame
    df_calls = pd.DataFrame
    df_academic_plan = pd.DataFrame

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent  # Сохранение ссылки на корневое окно
        self.init_ui()  # Загружаем пользовательский интерфейс

    def init_ui(self):
        # Заголовок окна
        self.parent.title('Система создания школьного расписания')
        self.pack(fill=BOTH, expand=True)

        # Создание вкладок
        tab_control = ttk.Notebook(self)
        tab_files = Frame(tab_control)  # Вкладка с загрузками файлов
        tab_parameters = Frame(tab_control)  # Вкладка с параметрами расписания

        tab_control.add(tab_files, text='Начальные данные')
        tab_control.add(tab_parameters, text='Параметры расписания')
        tab_control.pack(expand=1, fill="both")

        # Добавление фреймов на первую вкладку
        frame_academic_plan = LabelFrame(tab_files, text="Учебный план", relief=RAISED, borderwidth=1)
        frame_academic_plan.pack(fill=BOTH, expand=True)

        frame_teachers = LabelFrame(tab_files, text="Специализация учителей", relief=RAISED, borderwidth=1)
        frame_teachers.pack(fill=BOTH, expand=True)

        frame_audiences = LabelFrame(tab_files, text="Аудитории", relief=RAISED, borderwidth=1)
        frame_audiences.pack(fill=BOTH, expand=True)

        frame_audiences_lessons = LabelFrame(tab_files, text="Соответствие типа аудитории предмету",
                                             relief=RAISED, borderwidth=1)
        frame_audiences_lessons.pack(fill=BOTH, expand=True)

        frame_calls = LabelFrame(tab_files, text="Расписание звонков", relief=RAISED, borderwidth=1)
        frame_calls.pack(fill=BOTH, expand=True)

        # Создание кнопкок для вызова диалогового окна для загрузки
        load_button_a_p = Button(frame_academic_plan, text="Загрузить", command=lambda: load_academic_plan(self))
        load_button_a_p.pack(side=RIGHT, padx=10, pady=10)

        load_button_t = Button(frame_teachers, text="Загрузить", command=lambda: load_teachers(self))
        load_button_t.pack(side=RIGHT, padx=10, pady=10)

        load_button_a = Button(frame_audiences, text="Загрузить", command=lambda: load_audiences(self))
        load_button_a.pack(side=RIGHT, padx=10, pady=10)

        load_button_a_l = Button(frame_audiences_lessons, text="Загрузить",
                                 command=lambda: load_audiences_lessons(self))
        load_button_a_l.pack(side=RIGHT, padx=10, pady=10)

        load_button_c = Button(frame_calls, text="Загрузить", command=lambda: load_calls(self))
        load_button_c.pack(side=RIGHT, padx=10, pady=10)

        # Функции для выгрузки сообщений по результату загрузки
        # TODO: дедублицировать эти функции
        def load_academic_plan(self):
            Schedule.df_academic_plan = self.load_df()
            if not Schedule.df_academic_plan.empty:
                # TODO : исправить вывод сообщения
                label_loaded_academic_plan = Label(frame_academic_plan, fg='Green',
                                              text=f'Загружен план обучения')
                label_loaded_academic_plan.pack(side=LEFT, padx=10, pady=10)

        def load_teachers(self):
            Schedule.df_teachers = self.load_df()
            if not Schedule.df_teachers.empty:
                teacher_count = Schedule.df_teachers.shape[0]
                label_loaded_teachers = Label(frame_teachers, fg='Green',
                                              text=f'Загружены данные о {teacher_count} учителях')
                label_loaded_teachers.pack(side=LEFT, padx=10, pady=10)

        def load_audiences(self):
            Schedule.df_audiences = self.load_df()
            if not Schedule.df_audiences.empty:
                audiences_count = Schedule.df_audiences.shape[0]
                label_loaded_audiences = Label(frame_audiences, fg='Green',
                                               text=f'Загружены данные о {audiences_count} аудиоториях')
                label_loaded_audiences.pack(side=LEFT, padx=10, pady=10)

        def load_audiences_lessons(self):
            Schedule.df_audiences_lessons = self.load_df()
            if not Schedule.df_audiences_lessons.empty:
                label_loaded_audiences_lessons = Label(frame_audiences_lessons, fg='Green',
                                                       text=f'Загружены данные о типах аудиторий')
                label_loaded_audiences_lessons.pack(side=LEFT, padx=10, pady=10)

        def load_calls(self):
            Schedule.df_calls = self.load_df()
            if not Schedule.df_calls.empty:
                label_loaded_calls = Label(frame_calls, fg='Green',
                                           text=f'Загружены данные o звонках')
                label_loaded_calls.pack(side=LEFT, padx=10, pady=10)

        # Выход из программы
        quit_button = Button(self, text="Закрыть", command=lambda: self.quit())
        quit_button.pack(side=RIGHT, padx=10, pady=10)

    def load_df(self):
        fn = filedialog.Open(self.parent, filetypes=[('Excel files', '.xlsx .xls')]).show()
        if fn == '':
            # (("Template files", "*.tplate")
            #  , ("HTML files", "*.html;*.htm")
            #  , ("All files", "*.*")))
            return
        else:
            df = pd.read_excel(fn)
            return df

    def quit(self):
        if messagebox.askyesno("Выйти", "Закрыть программу?"):
            self.parent.destroy()

    def GA(self):
        teacher_count = Schedule.df_teachers.shape[0]


def main():
    # Создание корневого окна
    root = Tk()
    root.geometry("800x500+0+0")
    app = Schedule(root)
    root.mainloop()


if __name__ == '__main__':
    main()
