import tkinter
import pandas as pd
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.ttk import Combobox
import genetic_algoritm.genetic_operators as ga


class Schedule(Frame):
    # Cоздание атрибутов класса
    number_of_days_in_week = 5

    # Датафреймы с вводными для расписания
    df_teachers = pd.DataFrame
    df_audiences = pd.DataFrame
    df_audiences_lessons = pd.DataFrame
    df_rings = pd.DataFrame
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
        tab_schedule = Frame(tab_control)  # Вкладка с расписанием
        tab_control.add(tab_files, text='Начальные данные')
        tab_control.add(tab_parameters, text='Параметры расписания')
        tab_control.add(tab_schedule, text='Расписание')
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

        frame_rings = LabelFrame(tab_files, text="Расписание звонков", relief=RAISED, borderwidth=1)
        frame_rings.pack(fill=BOTH, expand=True)

        # Создание кнопок для вызова диалогового окна для загрузки
        load_button_a_p = Button(frame_academic_plan, text="Загрузить", command=lambda: load_df('academic_plan'))
        load_button_a_p.pack(side=RIGHT, padx=10, pady=10)

        load_button_t = Button(frame_teachers, text="Загрузить", command=lambda: load_df('teachers'))
        load_button_t.pack(side=RIGHT, padx=10, pady=10)

        load_button_a = Button(frame_audiences, text="Загрузить", command=lambda: load_df('audiences'))
        load_button_a.pack(side=RIGHT, padx=10, pady=10)

        load_button_audiences_lessons = Button(frame_audiences_lessons, text="Загрузить",
                                               command=lambda: load_df('audiences_lessons'))
        load_button_audiences_lessons.pack(side=RIGHT, padx=10, pady=10)

        load_button_c = Button(frame_rings, text="Загрузить", command=lambda: load_df('rings'))
        load_button_c.pack(side=RIGHT, padx=10, pady=10)

        # Сообщения по выгрузке данных
        label_loaded_academic_plan = Label(frame_academic_plan, text=f'Загружен план обучения', fg='#f0f0f0')
        label_loaded_academic_plan.pack(side=LEFT, padx=10, pady=10)
        label_loaded_teachers = Label(frame_teachers, text=f'Загружена информация о учителях', fg='#f0f0f0')
        label_loaded_teachers.pack(side=LEFT, padx=10, pady=10)
        label_loaded_audiences = Label(frame_audiences, text=f'Загружена информация о аудиториях', fg='#f0f0f0')
        label_loaded_audiences.pack(side=LEFT, padx=10, pady=10)
        label_loaded_rings = Label(frame_rings, text=f'Загружена информация о звонках', fg='#f0f0f0')
        label_loaded_rings.pack(side=LEFT, padx=10, pady=10)
        label_loaded_audiences_lessons = Label(frame_audiences_lessons, text=f'Загружена информация о типах аудиторий',
                                               fg='#f0f0f0')
        label_loaded_audiences_lessons.pack(side=LEFT, padx=10, pady=10)
        def load_df(df: str):
            str_save = 'Schedule.df_'+df+' = pd.read_excel(fn)'
            str_message = 'label_loaded_'+df+".configure(fg='Green')"
            str_load = 'label_loaded_'+df+".configure(fg='#f0f0f0')"

            # TODO: Разобраться, почему без этого не работают лейблы
            label_loaded_academic_plan.configure()
            label_loaded_teachers.configure()
            label_loaded_audiences.configure()
            label_loaded_rings.configure()
            label_loaded_audiences_lessons.configure()

            exec(str_load)
            fn = filedialog.Open(self.parent, filetypes=[('Excel files', '.xlsx .xls')]).show()
            # (("Template files", "*.tplate")
            #  , ("HTML files", "*.html;*.htm")
            #  , ("All files", "*.*")))
            # TODO: Добавить другие типы файлов
            if fn == '':
                return
            else:
                exec(str_save)
                exec(str_message)

        # Параметры расписания

        # Количество учебных дней в неделе
        label_days_in_week = Label(tab_parameters, text='Количество учебных дней в неделе')
        label_days_in_week.pack(side=TOP, padx=10, pady=10)
        combo_days_in_week = Combobox(tab_parameters)
        combo_days_in_week['values'] = (4, 5, 6)
        combo_days_in_week.current(1)  # Вариант по умолчанию
        combo_days_in_week.pack(side=TOP, padx=10, pady=10)

        # Вторая смена
        second_shift = IntVar()
        second_shift_checkbutton = ttk.Checkbutton(tab_parameters, text="Вторая смена", variable=second_shift)
        second_shift_checkbutton.pack(side=TOP, padx=10, pady=10)

        # Кнопка загрузки параметров
        def load_parameters_def(self):
            Schedule.number_of_days_in_week = int(combo_days_in_week.get())

        load_parameters = Button(tab_parameters, text="Сохранить параметры", command=lambda: load_parameters_def(self))
        load_parameters.pack(side=BOTTOM, padx=10, pady=10)

        # Выход из программы
        quit_button = Button(self, text="Закрыть", command=lambda: self.quit())
        quit_button.pack(side=RIGHT, padx=10, pady=10)

        # Создание расписания
        frame_table = LabelFrame(tab_schedule, text="Расписание", relief=RAISED, borderwidth=1)
        frame_table.pack(fill=BOTH, expand=True)
        ga_button = Button(tab_schedule, text="Создать расписание",
                           command=lambda: self.create_schedule(tab_schedule, frame_table))
        ga_button.pack(side=BOTTOM, padx=10, pady=10)
        return


    def quit(self):
        if messagebox.askyesno("Выйти", "Закрыть программу?"):
            self.parent.destroy()

    def create_schedule(self, tab_schedule, frame_schedule):
        if Schedule.df_teachers.empty or Schedule.df_audiences.empty or Schedule.df_academic_plan.empty or \
                Schedule.df_rings.empty or Schedule.df_audiences_lessons.empty:
            if messagebox.showinfo("Загрузить", "Введите все начальные данные"):
                return
        first_schedule = ga.get_empty_schedule(Schedule.df_rings, Schedule.number_of_days_in_week)
        first_schedule = ga.create_first_population(first_schedule, Schedule.df_academic_plan, Schedule.df_teachers,
                                                    Schedule.df_audiences_lessons, Schedule.df_audiences)
        # TODO: прописать остальные этапы генетического алгоритма
        self.show_schedule(tab_schedule, frame_schedule, first_schedule)

    @staticmethod
    def show_schedule(tab, frame, schedule: dict):

        # Преобразование расписания
        distinct_classes = sorted(Schedule.df_academic_plan['class'].unique())
        data = [['' for __ in range(len(distinct_classes))] for _ in range(len(schedule))]
        interval_num = 0
        for interval in schedule:
            for audience in schedule[interval]:
                school_class, lesson, teacher = [_ for _ in schedule[interval][audience]]
                item = str(lesson) + ' ' + str(teacher) + ' ' + str(audience)
                data[interval_num][distinct_classes.index(school_class)] = item
            interval_num += 1
        table = []
        interval_num = 0

        for interval in schedule:
            table.append((interval,) + tuple(data[interval_num]))
            interval_num += 1

        # Создание таблицы в Tkinter
        columns = ('',) + tuple(distinct_classes)

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        tree.heading("", text="", anchor=W)
        for i in distinct_classes:
            tree.heading(str(i), text=str(i), anchor=W)

        for interval in table:
            tree.insert("", END, values=interval)

        # Добавление вертикальной прокрутки
        scrollbar_v = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_v.set)
        scrollbar_v.pack(side=RIGHT, fill=Y)

        # Добавление горизонтальной прокрутки
        scrollbar_h = ttk.Scrollbar(frame, orient=HORIZONTAL, command=tree.xview)
        tree.configure(xscrollcommand=scrollbar_h.set)
        scrollbar_h.pack(side=BOTTOM, fill=X)

        tree.pack(fill=BOTH, expand=1)

        def save_schedule_def(schedule_table):
            df = pd.DataFrame(schedule_table)
            df.columns = [''] + distinct_classes
            # TODO: Добавить другие типы файлов
            df.to_excel('./schedule.xlsx', sheet_name='Budgets', index=False)

        # Кнопка загрузки
        save_schedule = Button(tab, text='Сохранить', command=lambda: save_schedule_def(table))
        save_schedule.pack(fill=NONE, expand=1)
        return


def main():
    # Создание корневого окна
    root = Tk()
    root.geometry("800x500+0+0")
    Schedule(root)
    root.mainloop()


if __name__ == '__main__':
    main()
