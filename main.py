import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

# --- Конфигурация ---
DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Прочее"]
DATE_FORMAT = "%Y-%m-%d"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        self.data = [] # Список словарей с расходами

        # Создаем виджеты
        self.create_widgets()
        
        # Загружаем данные из файла при запуске
        self.load_data()
        self.update_treeview()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # --- Рамка для ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить новый расход", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", pady=2)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=2)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                              values=CATEGORIES, state="readonly", width=13)
        self.category_combobox.current(0) # Выбираем первую категорию по умолчанию
        self.category_combobox.grid(row=1, column=1, sticky="w", pady=2)

        # Дата
        ttk.Label(input_frame, text="Дата:").grid(row=2, column=0, sticky="w", pady=2)
        self.date_entry = DateEntry(input_frame, date_pattern=DATE_FORMAT.replace("%", "-"), width=13)
        self.date_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)


        # --- Таблица расходов ---
        self.tree = ttk.Treeview(self.root, columns=("date", "category", "amount"), show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        
        self.tree.column("date", anchor="center", width=120)
        self.tree.column("category", anchor="center", width=150)
        self.tree.column("amount", anchor="e", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)


        # --- Рамка для фильтрации и подсчета ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация и отчет", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky="w")
        self.filter_cat_var = tk.StringVar()
        
        all_cat_combo = ttk.Combobox(filter_frame, textvariable=self.filter_cat_var, 
                                     values=["Все"] + CATEGORIES, state="readonly", width=15)
        all_cat_combo.current(0) # "Все" по умолчанию
        all_cat_combo.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=2, padx=5)

        # Период для подсчета суммы
        ttk.Label(filter_frame, text="Период для суммы:").grid(row=1, column=0, sticky="w", pady=5)
        
        self.start_date_entry = DateEntry(filter_frame, date_pattern=DATE_FORMAT.replace("%", "-"), width=13)
        self.start_date_entry.grid(row=1, column=1, sticky="w")
        
        ttk.Label(filter_frame, text="по").grid(row=1, column=2)
        
        self.end_date_entry = DateEntry(filter_frame, date_pattern=DATE_FORMAT.replace("%", "-"), width=13)
        self.end_date_entry.grid(row=1, column=3, sticky="w")
        
        ttk.Button(filter_frame, text="Подсчитать сумму", command=self.calculate_total).grid(row=1, column=4, padx=5)

         # Поле для вывода результата суммы
         self.total_label = ttk.Label(filter_frame, text="Сумма: 0 ₽")
         self.total_label.grid(row=2, column=0, columnspan=5, pady=10)


    # --- Логика работы с данными ---
    def add_expense(self):
        """Обработчик кнопки 'Добавить расход'"""
        
        amount_str = self.amount_var.get()
        category = self.category_var.get()
        
         # Валидация суммы
         try:
             amount = float(amount_str)
             if amount <= 0:
                 raise ValueError("Сумма должна быть больше нуля.")
         except ValueError:
             messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректную положительную сумму.")
             return

         # Валидация даты (DateEntry обычно не дает ввести некорректную дату)
         date_str = self.date_entry.get_date().strftime(DATE_FORMAT)
         
         # Добавляем в список данных и обновляем таблицу
         self.data.append({"date": date_str, "category": category, "amount": amount})
         self.update_treeview()
         self.save_data()
         
         # Очищаем поля ввода (кроме даты и категории)
         self.amount_var.set("")
         # Оставляем фокус на поле суммы для быстрого ввода следующего расхода

    def update_treeview(self):
        """Обновление данных в таблице Treeview"""
        
         for i in self.tree.get_children():
             self.tree.delete(i) # Очищаем таблицу

         for expense in self.data:
             self.tree.insert("", "end", values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
         
    def save_data(self):
         """Сохранение данных в JSON файл"""
         
         try:
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump(self.data, f, ensure_ascii=False, indent=4)
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def load_data(self):
         """Загрузка данных из JSON файла"""
         
         if os.path.exists(DATA_FILE):
             try:
                 with open(DATA_FILE, 'r', encoding='utf-8') as f:
                     self.data = json.load(f)
             except (json.JSONDecodeError, FileNotFoundError):
                 self.data = []
                 messagebox.showwarning("Ошибка загрузки", "Файл данных поврежден или пуст. Создан новый список.")
                 self.save_data() # Сохраняем пустой список

    # --- Логика фильтрации и подсчета ---
    def apply_filter(self):
         """Применение фильтра по категории"""
         
         selected_category = self.filter_cat_var.get()
         
         if selected_category == "Все":
             filtered_data = self.data
         else:
             filtered_data = [exp for exp in self.data if exp["category"] == selected_category]
         
         # Обновляем таблицу отфильтрованными данными без изменения основного списка
         for i in self.tree.get_children():
             self.tree.delete(i)
             
         for expense in filtered_data:
             self.tree.insert("", "end", values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
    
    def calculate_total(self):
         """Подсчет общей суммы за выбранный период"""
         
         start_date_str = self.start_date_entry.get_date().strftime(DATE_FORMAT)
         end_date_str = self.end_date_entry.get_date().strftime(DATE_FORMAT)
         
         total = 0.0
         
         for expense in self.data:
             if start_date_str <= expense["date"] <= end_date_str:
                 total += expense["amount"]
                 
         self.total_label.config(text=f"Сумма за период: {total:.2f} ₽")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()