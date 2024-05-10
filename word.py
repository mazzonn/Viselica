import customtkinter as CTk
import words
from random import *
from PIL import Image
import os
import sys
import sqlite3

class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS counters (
        name TEXT PRIMARY KEY,
        value INTEGER
        )
        """)
        self.conn.commit()
        
        self.counter_name = 'my_counter'
        self.counter_value = self.get_counter(self.counter_name)
        
        self.display_word = []
        
        self.geometry('500x400')
        self.title('Виселица')
        self.resizable(False, False)
        
        self.wOut = CTk.CTkFrame(master=self, fg_color='transparent')
        self.wOut.grid(row=1, column=0, padx=(20, 20), pady=(200, 100), sticky='nsew')

        self.entry_wOut = CTk.CTkLabel(master=self.wOut, text=" ".join(self.display_word), font=("Arial", 24))
        self.entry_wOut.grid(row=0, column =0, padx=(0,20))

        self.wIn = CTk.CTkFrame(master=self, fg_color='transparent')
        self.wIn.grid(row=1, column=1, padx=(20, 20), pady=(200, 100), sticky='nsew')

        self.text_var = CTk.StringVar()
        self.entry_wIn = CTk.CTkEntry(master=self.wOut, width=300, textvariable=self.text_var, placeholder_text='Введите букву')
        self.entry_wIn.grid(row=1, column =0, padx=(0,20))


        self.btn_word = CTk.CTkButton(master=self.wOut, text='Загадать слово', width=100,
                                      command=self.set_word, fg_color='green')
        self.btn_word.grid(row=0, column=1)
        
        self.btn_entry = CTk.CTkButton(master=self.wOut, text='Проверить букву', width=100,
                                      command=self.check, fg_color='green')
        self.btn_entry.grid(row=1, column=1, pady=(10, 10))

        self.setting_frame = CTk.CTkFrame(master=self)
        self.setting_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky='nsew')
        
        self.setting_frame_info = CTk.CTkFrame(master=self)
        self.setting_frame_info.grid(row=1, column=0, padx=(0, 0), pady=10)

        self.difficulty = CTk.CTkOptionMenu(master=self.setting_frame, fg_color='green',
                                            values=['Легкий', "Средний", "Тяжелый"])
        self.difficulty.grid(row=0, column=0, pady=(10, 10))

        self.text = CTk.CTkLabel(master=self.setting_frame, text='Уровень сложности')
        self.text.grid(row=0, column=1, padx=5, pady=5)
        
        self.text_info = CTk.CTkLabel(master=self.setting_frame, text='Всего слов угадано: ' + str(self.counter_value))
        self.text_info.grid(row=0, column=2, padx=5, pady=5)
        
        self.info = CTk.CTkLabel(master=self.setting_frame_info, text='')
        self.info.grid(row=0, column=1, pady=5)
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            filePath = os.path.join(sys._MEIPASS, "vis.png")
        else:
            scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
            filePath = os.path.join(scriptPath, "vis.png")
        
        self.logo = CTk.CTkImage(dark_image=Image.open(filePath), size=(200, 200))
        self.logo_lable = CTk.CTkLabel(master=self, text='', image=self.logo)
        self.logo_lable.place(x=100, y=70)

        self.theme_menu = CTk.CTkOptionMenu(master=self, fg_color='green',
                                            values=['Light', 'Dark', 'System'],
                                            command=self.set_theme)
        self.theme_menu.place(x=135, y=350)
        self.theme_menu.set('System')
        
    def set_theme(self, new_theme):
        CTk.set_appearance_mode(new_theme)
    
    def show_popup(self, text):
        self.popup = CTk.CTkToplevel(self)
        self.popup.geometry('300x55')
        self.popup.title('Всплывающее окно')
        self.popup.resizable(False, False)
        
        self.errror = CTk.CTkLabel(self.popup, text=text)
        self.errror.pack(padx=20, pady=20)
        
        self.popup.update_idletasks() 
        x = self.winfo_rootx() + (self.winfo_width() - self.popup.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - self.popup.winfo_height()) // 2
        self.popup.geometry(f"+{x}+{y}")
        
        self.popup.grab_set()

    
    def set_word(self):
        global chars
        selected_option = self.difficulty.get()
        
        if selected_option == 'Легкий':
            chars = choice(words.words_easy)
            self.entry_wOut.configure(text='_ ' * len(chars))
            self.display_word = ["_"] * len(chars)
            
        elif selected_option == 'Средний':
            chars = choice(words.words_normal)
            self.entry_wOut.configure(text='_ ' * len(chars))
            self.display_word = ["_"] * len(chars)
            
        else:
            chars = choice(words.words_hard)
            self.entry_wOut.configure(text='_ ' * len(chars))
            self.display_word = ["_"] * len(chars)
    
    def get_counter(self, name):
        self.cursor.execute("SELECT value FROM counters WHERE name=?", (name,))
        self.result = self.cursor.fetchone()
        return self.result[0] if self.result else 0
    
    def set_counter(self, name, value):
        self.cursor.execute("INSERT OR REPLACE INTO counters (name, value) VALUES (?, ?)", (name, value))
        self.conn.commit()
        
    def increment_counter(self, name):
        self.current_value = self.get_counter(name)   
        self.set_counter(name, self.current_value + 1)     

    def check(self):
        global letter
        letter = self.entry_wIn.get().lower()
        self.entry_wIn.delete(0, CTk.END)
        if letter in chars:
            for i in range(len(chars)):
                if chars[i] == letter:
                    self.display_word[i] = letter
            self.entry_wOut.configure(text=" ".join(self.display_word))
            if "_" not in self.display_word:
                 self.show_popup('Вы победили!!')
                 self.increment_counter(self.counter_name)
                 self.counter_value = self.get_counter(self.counter_name)
                 self.text_info.configure(text='Всего слов угадано: ' + str(self.counter_value))
                 self.conn.close()
        else:
            self.show_popup('Неверно, попробуйте еще раз.')
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
