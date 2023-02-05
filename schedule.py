from tkinter import Tk, Frame, BOTH
from tkinter import messagebox
from tkinter import *


# класс Tl для создания корневого окна
# класс Frame - контейнер для других виджетов

# from tkinter import filedialog

class schedule(Frame):
    # создание атрибутов класса

    # создание методов класса
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        # сохранили ссылку на корневое окно
        self.parent = parent

        self.initUI()

        # self.grid()
        # self.configure(background = "white")
        # self.eng, self.trans = str(), str()

        # self.message.grid(row = 1, column = 0, columnspan = 2, sticky = W + E)

    def initUI(self):
        self.parent.title('Система создания школьного расписания')

        quickmessage = Label(text='test', fg='red')
        quickmessage.place(x=10, y=30)
        quitButton = Button(self, text="Закрыть окно", command=self.quit)
        quitButton.place(x=50, y=100)
        self.pack(fill=BOTH, expand=1)

    def quit(self):
        if messagebox.askyesno("Выйти", "Закрыть программу?"):
            self.parent.destroy()


def main():
    # создаем корневое окно
    root = Tk()
    root.geometry("400x250+0+0")
    app = schedule(root)
    root.mainloop()


if __name__ == '__main__':
    main()

