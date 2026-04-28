import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
from tkcalendar import DateEntry

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        
        # Данные расходов
        self.expenses = []
        self.data_file = "expenses.json"
        
        # Загрузка данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        self.update_table()
        
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поля ввода
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=["Еда", "Транспорт", "Развлечения", "Одежда", "Здоровье", "Образование", "Другое"],
                                           width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=15, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                  values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Одежда", "Здоровье", "Образование", "Другое"],
                                                  width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.set("Все")
        
        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, width=15, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.start_date.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="По дату:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, width=15, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.end_date.grid(row=0, column=5, padx=5, pady=5)
        
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.update_table)
        filter_button.grid(row=0, column=6, padx=10, pady=5)
        
        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        clear_filter_button.grid(row=0, column=7, padx=10, pady=5)
        
        # Фрейм для итогов
        summary_frame = ttk.Frame(self.root)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.total_label = ttk.Label(summary_frame, text="Общая сумма: 0.00 руб.", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=20)
        
        clear_all_button = ttk.Button(summary_frame, text="Удалить все записи", command=self.clear_all_expenses)
        clear_all_button.pack(side="right", padx=20)
        
        # Таблица расходов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("amount", text="Сумма (руб.)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("amount", width=150)
        self.tree.column("category", width=200)
        self.tree.column("date", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def validate_input(self, amount_str):
        """Проверка корректности ввода суммы"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительным числом")
            return amount
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную положительную сумму")
            return None
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_entry.get().strip()
        
        # Проверка ввода
        amount = self.validate_input(amount_str)
        if amount is None:
            return
        
        category = self.category_var.get()
        date_str = self.date_entry.get()
        
        # Проверка даты
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
            return
        
        # Добавление расхода
        expense = {
            "amount": amount,
            "category": category,
            "date": date_str
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.update_table()
        
        # Очистка поля суммы
        self.amount_entry.delete(0, tk.END)
        
    def update_table(self, *args):
        """Обновление таблицы с учетом фильтров"""
        # Получение параметров фильтрации
        filter_category = self.filter_category_var.get()
        start_date_str = self.start_date.get()
        end_date_str = self.end_date.get()
        
        # Фильтрация данных
        filtered_expenses = self.expenses.copy()
        
        if filter_category and filter_category != "Все":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == filter_category]
        
        try:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
            end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
            
            filtered_expenses = [
                e for e in filtered_expenses 
                if start_date <= datetime.strptime(e["date"], "%d.%m.%Y") <= end_date
            ]
        except ValueError:
            pass
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        total = 0
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(expense["amount"], expense["category"], expense["date"]))
            total += expense["amount"]
        
        # Обновление итоговой суммы
        self.total_label.config(text=f"Общая сумма за период: {total:.2f} руб.")
    
    def clear_filters(self):
        """Сброс фильтров"""
        self.filter_category_combo.set("Все")
        self.update_table()
    
    def clear_all_expenses(self):
        """Удаление всех записей"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все записи?"):
            self.expenses = []
            self.save_data()
            self.update_table()
    
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить данные: {e}")
                self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
