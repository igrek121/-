import tkinter as tk
from tkinter import messagebox, filedialog
import random
from PIL import Image, ImageTk
import json
import os

class AdvancedHangman:
    def __init__(self, root):
        self.root = root
        self.root.title("Продвинутая Виселица")
        self.root.geometry("800x600")
        
        # Настройки игры
        self.words_file = "words.json"
        self.images_dir = "hangman_images"
        self.max_attempts = 6
        self.current_attempt = 0
        self.score = 0
        self.high_score = 0
        self.categories = {}
        self.current_category = ""
        self.secret_word = ""
        self.guessed_letters = set()
        
        # Загрузка данных
        self.load_words()
        self.load_high_score()
        
        # Графические элементы
        self.create_widgets()
        self.setup_game()

    def load_words(self):
        """Загрузка слов из JSON-файла по категориям"""
        default_words = {
            "Животные": ["тигр", "слон", "жираф", "кенгуру", "кот", "собака", "конь", "гиена", "лев", "зебка"],
            "Города": ["москва", "париж", "токио", "берлин","пермь","дубай","мадрид","рим","лондон"],
            "Технологии": ["компьютер", "смартфон", "интернет", "сайт", "приложение","система"]
        }
        
        if os.path.exists(self.words_file):
            with open(self.words_file, "r", encoding="utf-8") as f:
                self.categories = json.load(f)
        else:
            self.categories = default_words
            with open(self.words_file, "w", encoding="utf-8") as f:
                json.dump(default_words, f, ensure_ascii=False, indent=4)

    def load_high_score(self):
        """Загрузка рекорда из файла"""
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())

    def save_high_score(self):
        """Сохранение рекорда"""
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def create_widgets(self):
        """Создание интерфейса"""
        # Фреймы для организации элементов
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)
        
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(pady=20)
        
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10)
        
        # Изображение виселицы
        self.canvas = tk.Canvas(self.middle_frame, width=300, height=300, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=20)
        
        # Область слова
        self.word_label = tk.Label(self.middle_frame, text="", font=("Arial", 24))
        self.word_label.pack(side=tk.LEFT, padx=20)
        
        # Статус игры
        self.status_label = tk.Label(self.top_frame, text="", font=("Arial", 14))
        self.status_label.pack()
        
        # Клавиатура
        self.keyboard_frame = tk.Frame(self.bottom_frame)
        self.keyboard_frame.pack()
        
        self.create_keyboard()
        
        # Кнопки управления
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=20)
        
        tk.Button(self.control_frame, text="Новая игра", command=self.setup_game).grid(row=0, column=0, padx=10)
        tk.Button(self.control_frame, text="Выбор категории", command=self.choose_category).grid(row=0, column=1, padx=10)
        tk.Button(self.control_frame, text="Добавить слова", command=self.add_words).grid(row=0, column=2, padx=10)
        tk.Button(self.control_frame, text="Статистика", command=self.show_stats).grid(row=0, column=3, padx=10)
        
        # Отображение счета
        self.score_label = tk.Label(self.top_frame, text=f"Счет: {self.score} | Рекорд: {self.high_score}", font=("Arial", 12))
        self.score_label.pack(pady=10)

    def create_keyboard(self):
        """Создание виртуальной клавиатуры"""
        buttons = [
            'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И',
            'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
            'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь',
            'Э', 'Ю', 'Я'
        ]
        
        for i, letter in enumerate(buttons):
            btn = tk.Button(self.keyboard_frame, text=letter, width=3, height=1,
                           command=lambda l=letter: self.guess_letter(l.lower()))
            btn.grid(row=i//10, column=i%10, padx=2, pady=2)

    def choose_category(self):
        """Выбор категории слов"""
        self.category_window = tk.Toplevel(self.root)
        self.category_window.title("Выбор категории")
        
        for i, category in enumerate(self.categories.keys()):
            tk.Button(self.category_window, text=category, width=20,
                     command=lambda c=category: self.set_category(c)).grid(row=i, column=0, pady=5)

    def set_category(self, category):
        """Установка выбранной категории"""
        self.current_category = category
        self.category_window.destroy()
        self.setup_game()

    def setup_game(self):
        """Настройка новой игры"""
        self.current_attempt = 0
        self.guessed_letters = set()
        
        if not self.current_category:
            self.current_category = random.choice(list(self.categories.keys()))
        
        self.secret_word = random.choice(self.categories[self.current_category])
        self.update_display()
        self.draw_hangman()
        self.status_label.config(text=f"Категория: {self.current_category} | Осталось попыток: {self.max_attempts - self.current_attempt}")

    def update_display(self):
        """Обновление отображения слова"""
        displayed_word = []
        for letter in self.secret_word:
            if letter in self.guessed_letters:
                displayed_word.append(letter)
            else:
                displayed_word.append("_")
        
        self.word_label.config(text=" ".join(displayed_word))
        
        # Проверка на победу
        if "_" not in displayed_word:
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.score_label.config(text=f"Счет: {self.score} | Рекорд: {self.high_score}")
            messagebox.showinfo("Победа!", f"Вы угадали слово: {self.secret_word}")
            self.setup_game()

    def draw_hangman(self):
        """Отрисовка виселицы"""
        self.canvas.delete("all")
        stages = [
            self.draw_head,
            self.draw_body,
            self.draw_left_arm,
            self.draw_right_arm,
            self.draw_left_leg,
            self.draw_right_leg
        ]
        
        for i in range(self.current_attempt):
            if i < len(stages):
                stages[i]()

    def draw_head(self):
        self.canvas.create_oval(125, 50, 175, 100, width=3)

    def draw_body(self):
        self.canvas.create_line(150, 100, 150, 175, width=3)

    def draw_left_arm(self):
        self.canvas.create_line(150, 125, 120, 140, width=3)

    def draw_right_arm(self):
        self.canvas.create_line(150, 125, 180, 140, width=3)

    def draw_left_leg(self):
        self.canvas.create_line(150, 175, 120, 200, width=3)

    def draw_right_leg(self):
        self.canvas.create_line(150, 175, 180, 200, width=3)

    def guess_letter(self, letter):
        """Обработка угадывания буквы"""
        if letter in self.guessed_letters:
            messagebox.showwarning("Внимание", "Вы уже выбирали эту букву!")
            return
            
        self.guessed_letters.add(letter)
        
        if letter not in self.secret_word:
            self.current_attempt += 1
            if self.current_attempt >= self.max_attempts:
                self.game_over()
            else:
                self.status_label.config(text=f"Категория: {self.current_category} | Осталось попыток: {self.max_attempts - self.current_attempt}")
        
        self.update_display()
        self.draw_hangman()

    def game_over(self):
        """Обработка проигрыша"""
        messagebox.showinfo("Игра окончена", f"Вы проиграли! Загаданное слово: {self.secret_word}")
        self.score = max(0, self.score - 5)
        self.score_label.config(text=f"Счет: {self.score} | Рекорд: {self.high_score}")
        self.setup_game()

    def add_words(self):
        """Добавление новых слов"""
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Добавить слова")
        
        tk.Label(self.add_window, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.category_entry = tk.Entry(self.add_window, width=20)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.add_window, text="Слова (через запятую):").grid(row=1, column=0, padx=5, pady=5)
        self.words_entry = tk.Entry(self.add_window, width=40)
        self.words_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(self.add_window, text="Добавить", command=self.save_new_words).grid(row=2, columnspan=2, pady=10)

    def save_new_words(self):
        """Сохранение новых слов"""
        category = self.category_entry.get().strip()
        words = [word.strip().lower() for word in self.words_entry.get().split(",")]
        
        if not category or not words:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
            
        if category in self.categories:
            self.categories[category].extend(words)
        else:
            self.categories[category] = words
            
        with open(self.words_file, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=4)
            
        messagebox.showinfo("Успех", "Слова успешно добавлены!")
        self.add_window.destroy()

    def show_stats(self):
        """Показать статистику"""
        stats = (
            f"Текущий счет: {self.score}\n"
            f"Рекорд: {self.high_score}\n"
            f"Текущая категория: {self.current_category}\n"
            f"Всего категорий: {len(self.categories)}"
        )
        messagebox.showinfo("Статистика", stats)

if __name__ == "__main__":
    root = tk.Tk()
    game = AdvancedHangman(root)
    root.mainloop()