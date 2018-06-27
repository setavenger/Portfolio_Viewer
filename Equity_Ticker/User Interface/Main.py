
import tkinter as tk


class Main:

    def __init__(self, master):
        self.master = master

        # master.geometry('800x600')
        master.title('Portfolio')

        label01 = tk.Label(master, text='Press the Button add transaction')
        button01 = tk.Button(master, text="Hit me")

        label01.pack()
        button01.pack()


if __name__ == '__main__':
    root = tk.Tk()
    Main(root)
    root.mainloop()
