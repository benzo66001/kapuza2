"""
Random Task Generator - Генератор случайных задач
GUI-приложение для генерации и управления задачами

Автор: Капуза Никита
Вариант: №1 Random Task Generator
"""

import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox


class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Генератор задач")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "tasks_history.json"
        self.history = []  # История сгенерированных задач
        self.current_task = None
        
        # Предопределённые задачи по категориям
        self.predefined_tasks = {
            "Учёба": [
                "Прочитать статью по Python",
                "Решить 5 задач по математике",
                "Выучить 10 новых слов на английском",
                "Написать конспект по истории",
                "Сделать домашнее задание",
                "Подготовиться к экзамену",
                "Посмотреть обучающее видео",
                "Повторить пройденный материал"
            ],
            "Спорт": [
                "Сделать зарядку (15 мин)",
                "Пробежать 2 км",
                "Сделать 50 приседаний",
                "Пойти в спортзал",
                "Плавание в бассейне",
                "Йога 20 минут",
                "Отжимания 3 подхода",
                "Растяжка 10 минут"
            ],
            "Работа": [
                "Проверить рабочую почту",
                "Составить план на день",
                "Закончить отчёт",
                "Ответить на сообщения",
                "Провести встречу",
                "Организовать рабочее место",
                "Выполнить срочную задачу",
                "Проверить список дел"
            ],
            "Дом": [
                "Убраться в комнате",
                "Помыть посуду",
                "Полить цветы",
                "Вынести мусор",
                "Приготовить ужин",
                "Сделать уборку",
                "Постирать вещи",
                "Сходить в магазин"
            ],
            "Саморазвитие": [
                "Почитать книгу 30 минут",
                "Посмотреть TED-лекцию",
                "Практиковать медитацию",
                "Изучить новый навык",
                "Послушать подкаст",
                "Написать пост в блог",
                "Заполнить дневник",
                "Планирование целей"
            ]
        }
        
        # Загрузка истории
        self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление отображения истории
        self.refresh_history_display()
    
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === Панель генерации задачи ===
        generate_frame = ttk.LabelFrame(main_frame, text="Генератор задач", padding="15")
        generate_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Выбор категории для генерации
        ttk.Label(generate_frame, text="Выберите категорию:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar(value="Все категории")
        self.category_combo = ttk.Combobox(generate_frame, textvariable=self.category_var, 
                                           values=["Все категории"] + list(self.predefined_tasks.keys()),
                                           width=20, state="readonly")
        self.category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Кнопка генерации
        ttk.Button(generate_frame, text="🎲 Сгенерировать задачу", command=self.generate_task,
                  width=25).grid(row=0, column=2, padx=20, pady=5)
        
        # Отображение текущей задачи
        ttk.Label(generate_frame, text="Текущая задача:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(15, 5))
        
        self.current_task_var = tk.StringVar(value="Нажмите кнопку для генерации задачи")
        self.current_task_label = ttk.Label(generate_frame, textvariable=self.current_task_var, 
                                            font=("Arial", 12), foreground="blue", wraplength=500)
        self.current_task_label.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=(15, 5))
        
        # === Панель добавления новой задачи ===
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(add_frame, text="Название задачи:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.new_task_entry = ttk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.new_task_category = ttk.Combobox(add_frame, values=list(self.predefined_tasks.keys()), width=15)
        self.new_task_category.grid(row=0, column=3, padx=5, pady=5)
        self.new_task_category.set("Учёба")
        
        ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_custom_task).grid(row=0, column=4, padx=10, pady=5)
        
        # === Панель фильтрации ===
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + list(self.predefined_tasks.keys()), 
                                            width=15, state="readonly")
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category.set("Все")
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.filter_history).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(filter_frame, text="🔄 Показать всё", command=self.refresh_history_display).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(filter_frame, text="🗑 Очистить историю", command=self.clear_history).grid(row=0, column=4, padx=5, pady=5)
        
        # === История задач ===
        history_frame = ttk.LabelFrame(main_frame, text="История сгенерированных задач", padding="10")
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Создание списка с прокруткой
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, font=("Arial", 10),
                                          height=12, selectmode=tk.SINGLE)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Контекстное меню для удаления
        self.create_context_menu()
        
        # Информационная панель
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_var = tk.StringVar(value="Статистика: ")
        ttk.Label(info_frame, textvariable=self.stats_var, font=("Arial", 9)).pack(side=tk.LEFT)
        
        # Настройка веса
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
    
    def create_context_menu(self):
        """Создание контекстного меню для списка"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить задачу", command=self.delete_selected_task)
        self.history_listbox.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        if self.history_listbox.curselection():
            self.context_menu.post(event.x_root, event.y_root)
    
    def generate_task(self):
        """Генерация случайной задачи"""
        selected_category = self.category_var.get()
        
        # Сбор всех доступных задач
        available_tasks = []
        
        if selected_category == "Все категории":
            # Собираем задачи из всех категорий
            for category, tasks in self.predefined_tasks.items():
                for task in tasks:
                    available_tasks.append((task, category))
        else:
            # Задачи только из выбранной категории
            if selected_category in self.predefined_tasks:
                for task in self.predefined_tasks[selected_category]:
                    available_tasks.append((task, selected_category))
        
        if not available_tasks:
            messagebox.showwarning("Внимание", "Нет задач в выбранной категории!")
            return
        
        # Выбор случайной задачи
        task, category = random.choice(available_tasks)
        self.current_task = {"task": task, "category": category, "timestamp": self.get_timestamp()}
        
        # Добавление в историю
        self.history.insert(0, self.current_task)  # Добавляем в начало (новые сверху)
        self.save_history()
        
        # Отображение текущей задачи
        self.current_task_var.set(f"🏆 {task} (Категория: {category})")
        
        # Обновление истории
        self.refresh_history_display()
        
        self.update_stats()
    
    def add_custom_task(self):
        """Добавление пользовательской задачи"""
        task_text = self.new_task_entry.get().strip()
        category = self.new_task_category.get()
        
        # Валидация
        if not task_text:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        if len(task_text) > 100:
            messagebox.showerror("Ошибка", "Название задачи не должно превышать 100 символов!")
            return
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return
        
        # Добавление задачи в предопределённый список
        if category not in self.predefined_tasks:
            self.predefined_tasks[category] = []
        
        self.predefined_tasks[category].append(task_text)
        
        # Обновление выпадающих списков
        self.update_comboboxes()
        
        # Очистка полей
        self.new_task_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{category}'!")
    
    def delete_selected_task(self):
        """Удаление выбранной задачи из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу из истории?"):
            index = selection[0]
            del self.history[index]
            self.save_history()
            self.refresh_history_display()
            self.update_stats()
    
    def filter_history(self):
        """Фильтрация истории по категории"""
        category = self.filter_category.get()
        
        if category == "Все":
            self.refresh_history_display()
        else:
            filtered = [item for item in self.history if item.get("category") == category]
            self.display_history(filtered)
            self.stats_var.set(f"📊 Показано задач: {len(filtered)} из {len(self.history)}")
    
    def refresh_history_display(self):
        """Отображение всей истории"""
        self.display_history(self.history)
        self.update_stats()
        # Сброс фильтра
        self.filter_category.set("Все")
    
    def display_history(self, history_list):
        """Отображение задач в списке"""
        self.history_listbox.delete(0, tk.END)
        
        for item in history_list:
            timestamp = item.get("timestamp", "")
            task = item.get("task", "")
            category = item.get("category", "")
            display_text = f"{timestamp} | [{category}] {task}"
            self.history_listbox.insert(tk.END, display_text)
    
    def clear_history(self):
        """Очистка всей истории"""
        if not self.history:
            messagebox.showinfo("Информация", "История уже пуста!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_display()
            self.current_task_var.set("Нажмите кнопку для генерации задачи")
    
    def update_stats(self):
        """Обновление статистики"""
        if not self.history:
            self.stats_var.set("📊 Всего задач: 0")
            return
        
        # Подсчёт по категориям
        stats = {}
        for item in self.history:
            category = item.get("category", "Неизвестно")
            stats[category] = stats.get(category, 0) + 1
        
        stats_text = f"📊 Всего задач: {len(self.history)} | "
        for cat, count in stats.items():
            stats_text += f"{cat}: {count} | "
        
        self.stats_var.set(stats_text)
    
    def update_comboboxes(self):
        """Обновление выпадающих списков категорий"""
        categories = list(self.predefined_tasks.keys())
        
        self.category_combo['values'] = ["Все категории"] + categories
        self.new_task_category['values'] = categories
        self.filter_category['values'] = ["Все"] + categories
    
    def get_timestamp(self):
        """Получение текущей даты и времени"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def load_history(self):
        """Загрузка истории из JSON-файла"""
        if not os.path.exists(self.data_file):
            self.history = []
            return
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.history = []
                    return
                self.history = json.loads(content)
                if not isinstance(self.history, list):
                    self.history = []
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю:\n{str(e)}")
            self.history = []
            # Создание резервной копии
            if os.path.exists(self.data_file):
                backup_file = self.data_file + ".backup"
                try:
                    os.rename(self.data_file, backup_file)
                except:
                    pass
    
    def save_history(self):
        """Сохранение истории в JSON-файл"""
        try:
            temp_file = self.data_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            os.rename(temp_file, self.data_file)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю:\n{str(e)}")
            return False


def main():
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()