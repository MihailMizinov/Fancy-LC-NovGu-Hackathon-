from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import sys
import os
import datetime
import shutil
from rag_system import RAGSystem


class NeuroHelpApp:
    def __init__(self):
        self.main_app = Tk()
        self.main_app.title("NeuroHelp")
        self.main_app.geometry("1100x750")
        self.main_app.configure(bg='#0f0f0f')
        self.main_app.minsize(900, 600)

        # Премиальная цветовая схема
        self.colors = {
            'background': '#0f0f0f',
            'surface': '#1a1a1a',
            'surface_light': '#2a2a2a',
            'primary': '#8b5cf6',
            'primary_light': '#a78bfa',
            'accent': '#06d6a0',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'user_message': '#8b5cf6',
            'ai_message': '#2a2a2a',
            'border': '#333333',
            'hover': '#333333',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'input_bg': '#1a1a1a',
            'input_border': '#8b5cf6'
        }

        self.main_app.configure(bg=self.colors['background'])

        try:
            self.main_app.iconphoto(True, PhotoImage(file="neutral.png"))
        except:
            pass

        # Данные пользователей
        self.users_file = "users.json"
        self.chats_file = "chats.json"
        self.sources_dir = "data/documents"
        self.current_user = None
        self.users = self.load_users()
        self.chats = self.load_chats()

        # Создаем папку sources если её нет
        if not os.path.exists(self.sources_dir):
            os.makedirs(self.sources_dir)

        # Инициализация RAG системы
        self.rag_system = RAGSystem()
        self.rag_initialized = self.rag_system.initialize_system()

        if not self.rag_initialized:
            print("⚠️ RAG система не инициализирована. Будет использоваться простой режим.")

        self.show_login_screen()

    def load_chats(self):
        if os.path.exists(self.chats_file):
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    chats = json.load(f)

                # Исправляем структуру чатов, если нужно
                for username, chat_data in chats.items():
                    if 'messages' not in chat_data:
                        chat_data['messages'] = []
                    if 'created' not in chat_data:
                        chat_data['created'] = datetime.datetime.now().isoformat()

                return chats
            except Exception as e:
                print(f"Error loading chats: {e}")
                return {}
        return {}

    def save_chats(self):
        with open(self.chats_file, 'w', encoding='utf-8') as f:
            json.dump(self.chats, f, ensure_ascii=False, indent=2)

    def get_user_chat(self):
        if self.current_user not in self.chats:
            self.chats[self.current_user] = {
                'messages': [],
                'created': datetime.datetime.now().isoformat()
            }
            self.save_chats()
        else:
            # Гарантируем, что структура правильная
            if 'messages' not in self.chats[self.current_user]:
                self.chats[self.current_user]['messages'] = []
            if 'created' not in self.chats[self.current_user]:
                self.chats[self.current_user]['created'] = datetime.datetime.now().isoformat()

        return self.chats[self.current_user]

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"admin": {"password": "admin", "is_admin": True}}
        else:
            return {"admin": {"password": "admin", "is_admin": True}}

    def save_users(self):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def show_login_screen(self):
        self.clear_window()

        # Премиальный экран входа
        container = Frame(self.main_app, bg=self.colors['background'])
        container.pack(expand=True, fill=BOTH)

        # Градиентный фон
        bg_frame = Frame(container, bg=self.colors['background'], height=300)
        bg_frame.pack(fill=X)

        # Центрируем форму входа
        center_frame = Frame(container, bg=self.colors['background'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Логотип и заголовок
        logo_frame = Frame(center_frame, bg=self.colors['background'])
        logo_frame.pack(pady=(0, 40))

        title = Label(logo_frame, text="NEUROHELP",
                      font=("Arial", 32, "bold"),
                      bg=self.colors['background'],
                      fg=self.colors['primary'])
        title.pack()

        subtitle = Label(logo_frame, text="AI Assistant",
                         font=("Arial", 14),
                         bg=self.colors['background'],
                         fg=self.colors['text_secondary'])
        subtitle.pack(pady=(5, 0))

        # Карточка входа
        login_card = Frame(center_frame, bg=self.colors['surface'],
                           relief='flat', padx=40, pady=40)
        login_card.pack(padx=20, pady=20)

        # Поля ввода с цветной границей
        self.login_entry = Entry(login_card,
                                 font=("Arial", 12),
                                 width=22,
                                 justify='left',
                                 bg=self.colors['input_bg'],
                                 fg=self.colors['text_primary'],
                                 relief='solid',
                                 bd=1,
                                 highlightthickness=1,
                                 highlightcolor=self.colors['input_border'],
                                 highlightbackground=self.colors['input_border'],
                                 insertbackground=self.colors['text_primary'])
        self.login_entry.pack(pady=12, ipady=10, fill=X)
        self.login_entry.insert(0, "Логин")
        self.login_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Логин"))

        self.password_entry = Entry(login_card,
                                    font=("Arial", 12),
                                    width=22,
                                    justify='left',
                                    show="•",
                                    bg=self.colors['input_bg'],
                                    fg=self.colors['text_primary'],
                                    relief='solid',
                                    bd=1,
                                    highlightthickness=1,
                                    highlightcolor=self.colors['input_border'],
                                    highlightbackground=self.colors['input_border'],
                                    insertbackground=self.colors['text_primary'])
        self.password_entry.pack(pady=12, ipady=10, fill=X)
        self.password_entry.insert(0, "Пароль")
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Пароль"))

        # Кнопка входа
        login_btn = Button(login_card, text="ВОЙТИ",
                           font=("Arial", 12, "bold"),
                           bg=self.colors['primary'],
                           fg='white',
                           relief='flat',
                           width=20,
                           height=2,
                           command=self.login)
        login_btn.pack(pady=20)

        # Подсказка
        hint = Label(login_card,
                     text="admin / admin",
                     font=("Arial", 10),
                     bg=self.colors['surface'],
                     fg=self.colors['text_secondary'])
        hint.pack()

        # Обработка Enter
        self.login_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.login_entry.focus()

    def clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, END)
            if placeholder == "Пароль":
                event.widget.config(show="•")

    def login(self):
        username = self.login_entry.get().strip()
        password = self.password_entry.get()

        if username == "Логин" or password == "Пароль" or not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        if username in self.users and self.users[username]["password"] == password:
            self.current_user = username
            self.setup_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def setup_main_interface(self):
        self.clear_window()

        # Главный контейнер
        main_container = Frame(self.main_app, bg=self.colors['background'])
        main_container.pack(fill=BOTH, expand=True)

        # Верхняя панель
        self.setup_header(main_container)

        # Основная область чата
        self.setup_chat_area(main_container)

        # Панель ввода
        self.setup_input_panel(main_container)

        # Загружаем историю чата
        self.load_chat_messages()

    def setup_header(self, parent):
        """Верхняя панель с кнопками управления"""
        header = Frame(parent, bg=self.colors['surface'], height=70)
        header.pack(fill=X)
        header.pack_propagate(False)

        # Логотип
        logo_frame = Frame(header, bg=self.colors['surface'])
        logo_frame.pack(side=LEFT, padx=25, pady=20)

        title = Label(logo_frame, text="NEUROHELP",
                      font=("Arial", 18, "bold"),
                      bg=self.colors['surface'],
                      fg=self.colors['primary'])
        title.pack(side=LEFT)

        # Панель управления
        control_frame = Frame(header, bg=self.colors['surface'])
        control_frame.pack(side=RIGHT, padx=25, pady=20)

        # Кнопка выхода
        logout_btn = Button(control_frame, text="Выйти",
                            font=("Arial", 10),
                            bg=self.colors['surface_light'],
                            fg=self.colors['text_primary'],
                            relief='flat',
                            padx=15,
                            pady=8,
                            command=self.logout)
        logout_btn.pack(side=RIGHT, padx=(10, 0))

        # Информация о пользователе
        user_info = Label(control_frame,
                          text=f"    👤 {self.current_user}",
                          font=("Arial", 10),
                          bg=self.colors['surface'],
                          fg=self.colors['text_secondary'])
        user_info.pack(side=RIGHT, padx=(20, 10))

        # Кнопка очистки контекста
        clear_btn = Button(control_frame, text="Очистить контекст",
                           font=("Arial", 10),
                           bg=self.colors['surface_light'],
                           fg=self.colors['text_primary'],
                           relief='flat',
                           padx=15,
                           pady=8,
                           command=self.clear_chat)
        clear_btn.pack(side=RIGHT, padx=(10, 0))

        # Кнопка библиотеки
        library_btn = Button(control_frame, text="Библиотека",
                             font=("Arial", 10),
                             bg=self.colors['surface_light'],
                             fg=self.colors['text_primary'],
                             relief='flat',
                             padx=15,
                             pady=8,
                             command=self.show_library)
        library_btn.pack(side=RIGHT, padx=(10, 0))

        # Кнопка управления пользователями (для админов)
        if self.users[self.current_user].get('is_admin'):
            users_btn = Button(control_frame, text="Пользователи",
                               font=("Arial", 10),
                               bg=self.colors['surface_light'],
                               fg=self.colors['text_primary'],
                               relief='flat',
                               padx=15,
                               pady=8,
                               command=self.show_user_management)
            users_btn.pack(side=RIGHT, padx=(10, 0))

    def setup_chat_area(self, parent):
        """Область сообщений"""
        self.messages_frame = Frame(parent, bg=self.colors['background'])
        self.messages_frame.pack(fill=BOTH, expand=True)

        # Canvas для сообщений
        self.chat_canvas = Canvas(self.messages_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = Scrollbar(self.messages_frame, orient="vertical", command=self.chat_canvas.yview)
        self.scrollable_frame = Frame(self.chat_canvas, bg=self.colors['background'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw",
            width=self.chat_canvas.winfo_width()
        )

        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязка событий
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.messages_frame.bind("<Configure>", self._on_chat_resize)

        # Отслеживание изменения размера canvas
        self.chat_canvas.bind("<Configure>", self._on_chat_resize)

    def setup_input_panel(self, parent):
        """Панель ввода сообщений"""
        input_container = Frame(parent, bg=self.colors['background'])
        input_container.pack(fill=X, padx=25, pady=20)

        # Контейнер для поля ввода
        input_wrapper = Frame(input_container, bg=self.colors['surface_light'],
                              relief='flat', padx=3, pady=3)
        input_wrapper.pack(fill=X)

        self.message_input = Text(input_wrapper,
                                  height=4,
                                  wrap=WORD,
                                  font=("Arial", 12),
                                  padx=15,
                                  pady=15,
                                  relief='flat',
                                  highlightthickness=0,
                                  bg=self.colors['input_bg'],
                                  fg=self.colors['text_primary'],
                                  insertbackground=self.colors['text_primary'])
        self.message_input.pack(side=LEFT, fill=BOTH, expand=True)

        # Кнопка отправки
        send_btn = Button(input_wrapper,
                          text="➤",
                          font=("Arial", 16),
                          bg=self.colors['primary'],
                          fg='white',
                          relief='flat',
                          width=3,
                          command=self.send_message)
        send_btn.pack(side=RIGHT, padx=5, pady=5)

        self.message_input.bind("<Return>", self.handle_enter)
        self.message_input.bind("<Shift-Return>", self.handle_shift_enter)
        self.message_input.focus()

    def _on_chat_resize(self, event):
        """Обработка изменения размера чата"""
        self.chat_canvas.itemconfig(self.chat_window, width=event.width)

        # Обновляем wraplength для всех сообщений при изменении размера
        self.update_all_message_wraplengths()

    def update_all_message_wraplengths(self):
        """Обновление переноса для всех сообщений при изменении размера"""
        # Вычисляем новую ширину для переноса (80% от ширины чата)
        new_wraplength = int(self.chat_canvas.winfo_width() * 0.8)

        # Устанавливаем минимальную и максимальную ширину
        new_wraplength = max(400, min(new_wraplength, 800))

        # Обновляем все сообщения в scrollable_frame
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, Frame):
                # Ищем Label с текстом в дочерних виджетах
                for child in widget.winfo_children():
                    if isinstance(child, Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, Frame):  # text_frame
                                for great_grandchild in grandchild.winfo_children():
                                    if isinstance(great_grandchild, Label):
                                        great_grandchild.config(wraplength=new_wraplength)

    def _on_mousewheel(self, event):
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def handle_enter(self, event):
        self.send_message()
        return "break"

    def handle_shift_enter(self, event):
        return

    def send_message(self):
        message = self.message_input.get("1.0", END).strip()
        if not message:
            return

        self.add_message(message, "user")
        self.message_input.delete("1.0", END)

        # Ответ от бота через RAG систему
        self.main_app.after(500, lambda: self.bot_response(message))

    def bot_response(self, message):
        try:
            if hasattr(self, 'rag_system') and self.rag_initialized:
                # Используем RAG систему
                response = self.rag_system.process_question(message)
                answer_text = response[0]  # Берем первый элемент массива - текст ответа
                context_chunks = response[1]
                confidence = response[2]

                # Преобразуем confidence в строку с форматированием
                confidence_str = f"{confidence:.3f}"

                # Формируем полный ответ с уверенностью
                full_answer = f"{answer_text}\n\n🎯 Степень уверенности: {confidence_str} / 1.0"

                # Отправляем основной ответ
                self.add_message(full_answer, "ai")

                # Отправляем отдельное сообщение с документами-гиперссылками
                if context_chunks:
                    self.add_documents_message(context_chunks)
                else:
                    self.add_message("📚 Использованные документы: не найдены", "ai")

            else:
                # Заглушка, если RAG система не работает
                self.add_message("Это тестовый ответ. RAG система не инициализирована.", "ai")

        except Exception as e:
            print(f"Ошибка при получении ответа: {e}")
            self.add_message("Произошла ошибка при обработке запроса", "ai")

    def add_documents_message(self, context_chunks):
        """Добавление сообщения с документами-гиперссылками (с фильтрацией дубликатов)"""
        # Создаем фрейм для сообщения с документами
        msg_frame = Frame(self.scrollable_frame, bg=self.colors['background'])
        msg_frame.pack(fill=X, padx=25, pady=8)

        # Основной контейнер
        container = Frame(msg_frame, bg=self.colors['background'])
        container.pack(anchor='w', fill=X)

        # Контейнер сообщения
        message_bg = self.colors['ai_message']
        text_color = self.colors['text_primary']

        message_container = Frame(container, bg=message_bg, relief='flat', padx=0, pady=0)
        message_container.pack(padx=(0, 80), pady=2, anchor='w')

        # Заголовок документов
        text_frame = Frame(message_container, bg=message_bg)
        text_frame.pack(fill=X, padx=20, pady=(16, 10))

        title_label = Label(text_frame,
                            text="📚 Использованные документы:",
                            wraplength=600,
                            justify='left',
                            font=("Arial", 12, "bold"),
                            bg=message_bg,
                            fg=text_color,
                            anchor='w')
        title_label.pack(fill=X)

        # Фрейм для кнопок-документов
        docs_frame = Frame(message_container, bg=message_bg)
        docs_frame.pack(fill=X, padx=20, pady=(0, 16))

        # Фильтруем дубликаты и берем уникальные документы с максимальной схожестью
        unique_docs = self._get_unique_documents(context_chunks)

        if not unique_docs:
            no_docs_label = Label(docs_frame,
                                  text="Документы не найдены",
                                  font=("Arial", 10),
                                  bg=message_bg,
                                  fg=text_color,
                                  anchor='w')
            no_docs_label.pack(fill=X)
        else:
            for i, (file_path, similarity) in enumerate(unique_docs[:5], 1):  # Ограничиваем 5 документами
                doc_frame = Frame(docs_frame, bg=message_bg)
                doc_frame.pack(fill=X, pady=2)

                filename = os.path.basename(file_path)
                similarity_str = f"{similarity:.3f}"

                # Создаем кнопку-гиперссылку для документа
                doc_button = Button(doc_frame,
                                    text=f"{i}. {filename} (схожесть: {similarity_str})",
                                    font=("Arial", 10),
                                    bg=message_bg,
                                    fg=self.colors['primary_light'],
                                    relief='flat',
                                    cursor='hand2',
                                    anchor='w',
                                    command=lambda path=file_path: self.open_document(path))
                doc_button.pack(side=LEFT)

        # Панель с временем
        bottom_frame = Frame(message_container, bg=message_bg)
        bottom_frame.pack(fill=X, padx=20, pady=(0, 12))

        time_label = Label(bottom_frame,
                           text=datetime.datetime.now().strftime("%H:%M"),
                           font=("Arial", 9),
                           bg=message_bg,
                           fg=text_color)
        time_label.pack(side=LEFT)

        # Прокрутка вниз
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _get_unique_documents(self, context_chunks):
        """Получить уникальные документы с максимальной схожестью для каждого"""
        unique_docs = {}

        for chunk in context_chunks:
            file_path = chunk.get('source')
            if not file_path:
                continue

            similarity = chunk.get('similarity', 0)
            # Безопасное преобразование similarity в float
            similarity_float = float(similarity) if hasattr(similarity, 'item') else float(similarity)

            # Если документ уже есть в списке, берем максимальную схожесть
            if file_path in unique_docs:
                if similarity_float > unique_docs[file_path]:
                    unique_docs[file_path] = similarity_float
            else:
                unique_docs[file_path] = similarity_float

        # Сортируем по убыванию схожести
        sorted_docs = sorted(unique_docs.items(), key=lambda x: x[1], reverse=True)

        return sorted_docs

    def open_document(self, file_path):
        """Открытие документа"""
        try:
            # Полный путь к документу
            full_path = os.path.abspath(file_path)

            # Проверяем существование файла
            if not os.path.exists(full_path):
                # Пробуем найти в папке data/documents
                docs_dir = "data/documents"
                filename = os.path.basename(file_path)
                alternative_path = os.path.join(docs_dir, filename)

                if os.path.exists(alternative_path):
                    full_path = os.path.abspath(alternative_path)
                else:
                    messagebox.showerror("Ошибка", f"Документ не найден:\n{filename}")
                    return

            # Открываем файл с помощью стандартной программы
            if os.name == 'nt':  # Windows
                os.startfile(full_path)
            elif os.name == 'posix':  # Linux, macOS
                import subprocess
                subprocess.run(['open', full_path] if sys.platform == 'darwin' else ['xdg-open', full_path])
            else:
                messagebox.showinfo("Информация", f"Документ:\n{full_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть документ:\n{str(e)}")

    def load_chat_messages(self):
        """Загрузка сообщений чата"""
        # Очищаем текущие сообщения
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Загружаем сообщения
        user_chat = self.get_user_chat()
        messages = user_chat.get('messages', [])

        for msg_data in messages:
            self.add_message(msg_data['message'], msg_data['sender'], add_to_history=False)

        # Если чат пустой, добавляем приветственное сообщение
        if not messages:
            self.add_message("Добро пожаловать в NeuroHelp! Я ваш AI-помощник. Чем могу помочь?", "ai")

    def add_message(self, message, sender, add_to_history=True):
        """Добавление сообщения с премиальным дизайном"""
        if add_to_history:
            # Сохраняем в историю
            user_chat = self.get_user_chat()
            if 'messages' not in user_chat:
                user_chat['messages'] = []

            user_chat['messages'].append({
                'sender': sender,
                'message': message,
                'time': datetime.datetime.now().isoformat()
            })
            self.save_chats()

        # Создаем фрейм для сообщения
        msg_frame = Frame(self.scrollable_frame, bg=self.colors['background'])
        msg_frame.pack(fill=X, padx=25, pady=8)

        # Основной контейнер
        container = Frame(msg_frame, bg=self.colors['background'])

        if sender == "user":
            container.pack(anchor='e', fill=X)
            # Сообщение пользователя - справа, фиолетовое
            message_bg = self.colors['user_message']
            text_color = 'white'
            container_padx = (80, 0)  # Отступ слева для пользовательских сообщений
        else:
            container.pack(anchor='w', fill=X)
            # Сообщение AI - слева, темное
            message_bg = self.colors['ai_message']
            text_color = self.colors['text_primary']
            container_padx = (0, 80)  # Отступ справа для AI сообщений

        # Контейнер сообщения с закругленными углами (эмулируем через рамку)
        message_container = Frame(container, bg=message_bg, relief='flat', padx=0, pady=0)
        message_container.pack(padx=container_padx, pady=2, anchor='w' if sender == "ai" else 'e')

        # Текст сообщения с автоматическим переносом
        text_frame = Frame(message_container, bg=message_bg)
        text_frame.pack(fill=X, padx=20, pady=16)

        # Используем Label с автоматическим переносом вместо Text
        msg_label = Label(text_frame,
                          text=message,
                          wraplength=600,  # Максимальная ширина перед переносом
                          justify='left',
                          font=("Arial", 12),
                          bg=message_bg,
                          fg=text_color,
                          anchor='w')
        msg_label.pack(fill=X)

        # Панель с кнопкой копирования и временем
        bottom_frame = Frame(message_container, bg=message_bg)
        bottom_frame.pack(fill=X, padx=20, pady=(8, 12))

        # Время
        time_label = Label(bottom_frame,
                           text=datetime.datetime.now().strftime("%H:%M"),
                           font=("Arial", 9),
                           bg=message_bg,
                           fg=text_color)
        time_label.pack(side=LEFT)

        # Кнопка копирования
        copy_btn = Button(bottom_frame,
                          text="📋 Копировать",
                          font=("Arial", 9),
                          bg=message_bg,
                          fg=text_color,
                          relief='flat',
                          command=lambda: self.copy_text(message))
        copy_btn.pack(side=RIGHT)

        # Автоматическое обновление размера контейнера
        self.update_message_container_size(message_container)

        # Прокрутка вниз
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def update_message_container_size(self, container):
        """Автоматическое обновление размера контейнера сообщения"""
        # Даем время на отрисовку
        self.main_app.update_idletasks()

        # Вычисляем необходимую ширину
        required_width = container.winfo_reqwidth()
        required_height = container.winfo_reqheight()

        # Устанавливаем минимальные размеры для красоты
        min_width = 200
        max_width = 800

        if required_width < min_width:
            container.config(width=min_width)
        elif required_width > max_width:
            container.config(width=max_width)

    def update_message_size(self, text_widget):
        """Обновление размера сообщения"""
        text_widget.config(state=NORMAL)
        line_count = int(text_widget.index('end-1c').split('.')[0])
        text_widget.config(height=line_count)
        text_widget.config(state=DISABLED)

    def copy_text(self, text):
        """Копирование текста в буфер обмена"""
        self.main_app.clipboard_clear()
        self.main_app.clipboard_append(text)
        self.show_copy_notification()

    def show_copy_notification(self):
        """Уведомление о копировании"""
        notification = Toplevel(self.main_app)
        notification.overrideredirect(True)
        notification.geometry("200x40")
        notification.configure(bg=self.colors['accent'])

        # Центрируем уведомление
        x = self.main_app.winfo_x() + (self.main_app.winfo_width() // 2) - 100
        y = self.main_app.winfo_y() + (self.main_app.winfo_height() // 2) - 20
        notification.geometry(f"+{x}+{y}")

        label = Label(notification, text="✓ Текст скопирован",
                      font=("Arial", 11),
                      bg=self.colors['accent'],
                      fg='white')
        label.pack(expand=True)

        notification.after(1500, notification.destroy)

    def clear_chat(self):
        """Очистка чата"""
        if messagebox.askyesno("Очистка чата", "Вы уверены, что хотите очистить всю историю сообщений?"):
            user_chat = self.get_user_chat()
            user_chat['messages'] = []
            self.save_chats()

            RAGSystem.clear_history(self)

            # Очищаем отображение
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Добавляем приветственное сообщение
            self.add_message("История сообщений очищена. Чем могу помочь?", "ai")
            self.update_all_message_wraplengths()



    def show_library(self):
        """Библиотека документов"""
        self.library_window = Toplevel(self.main_app)
        self.library_window.title("Библиотека документов")
        self.library_window.geometry("808x600")
        self.library_window.configure(bg=self.colors['surface'])
        self.library_window.transient(self.main_app)
        self.library_window.resizable(False, False)

        # Центрируем окно
        x = self.main_app.winfo_x() + (self.main_app.winfo_width() // 2) - 300
        y = self.main_app.winfo_y() + (self.main_app.winfo_height() // 2) - 250
        self.library_window.geometry(f"+{x}+{y}")

        # Заголовок
        header_frame = Frame(self.library_window, bg=self.colors['surface'], padx=30, pady=20)
        header_frame.pack(fill=X)

        title = Label(header_frame, text="📚 Библиотека документов",
                      font=("Arial", 18, "bold"),
                      bg=self.colors['surface'],
                      fg=self.colors['text_primary'])
        title.pack(anchor='w')

        subtitle = Label(header_frame, text="Папка data/documents/",
                         font=("Arial", 12),
                         bg=self.colors['surface'],
                         fg=self.colors['text_secondary'])
        subtitle.pack(anchor='w', pady=(5, 0))

        # Панель управления
        control_frame = Frame(self.library_window, bg=self.colors['surface'], padx=30, pady=10)
        control_frame.pack(fill=X)

        add_btn = Button(control_frame, text="+ Добавить документ",
                         font=("Arial", 11),
                         bg=self.colors['primary'],
                         fg='white',
                         relief='flat',
                         padx=20,
                         pady=10,
                         command=self.add_document)
        add_btn.pack(side=LEFT)

        # Список документов
        list_frame = Frame(self.library_window, bg=self.colors['surface'], padx=30, pady=10)
        list_frame.pack(fill=BOTH, expand=True)

        # Заголовки колонок
        columns_frame = Frame(list_frame, bg=self.colors['surface_light'], padx=15, pady=12)
        columns_frame.pack(fill=X)

        Label(columns_frame, text="Документ",
              font=("Arial", 11, "bold"),
              bg=self.colors['surface_light'],
              fg=self.colors['text_primary']).pack(side=LEFT)

        Label(columns_frame, text="Действия",
              font=("Arial", 11, "bold"),
              bg=self.colors['surface_light'],
              fg=self.colors['text_primary']).pack(side=RIGHT)

        # Прокручиваемая область
        canvas = Canvas(list_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar = Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_library_frame = Frame(canvas, bg=self.colors['surface'])

        self.scrollable_library_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_library_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заполняем список документов
        self.fill_documents_list()

        # Кнопка закрытия
        footer_frame = Frame(self.library_window, bg=self.colors['surface'], padx=30, pady=20)
        footer_frame.pack(fill=X)

        Button(footer_frame, text="Закрыть",
               font=("Arial", 12),
               bg=self.colors['surface_light'],
               fg=self.colors['text_primary'],
               relief='flat',
               pady=10,
               command=self.library_window.destroy).pack(fill=X)

    def fill_documents_list(self):
        """Заполнение списка документов"""
        # Очищаем старый список
        for widget in self.scrollable_library_frame.winfo_children():
            widget.destroy()

        # Получаем список файлов в папке sources
        try:
            files = os.listdir(self.sources_dir)
        except:
            files = []

        if not files:
            # Сообщение если папка пустая
            empty_frame = Frame(self.scrollable_library_frame, bg=self.colors['surface'], pady=40)
            empty_frame.pack(fill=X)

            Label(empty_frame, text="Папка sources пуста",
                  font=("Arial", 12),
                  bg=self.colors['surface'],
                  fg=self.colors['text_secondary']).pack()

            Label(empty_frame, text="Добавьте документы с помощью кнопки выше",
                  font=("Arial", 10),
                  bg=self.colors['surface'],
                  fg=self.colors['text_secondary']).pack()
            return

        # Отображаем файлы
        for i, filename in enumerate(files):
            file_frame = Frame(self.scrollable_library_frame,
                               bg=self.colors['surface_light'] if i % 2 == 0 else self.colors['surface'],
                               padx=15, pady=12)
            file_frame.pack(fill=X, pady=1)

            # Иконка и название файла
            file_icon = "📄"
            if filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                file_icon = "📄"
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                file_icon = "🖼️"
            elif filename.lower().endswith(('.xls', '.xlsx', '.csv')):
                file_icon = "📊"

            file_label = Label(file_frame,
                               text=f"{file_icon} {filename}",
                               font=("Arial", 11),
                               bg=file_frame['bg'],
                               fg=self.colors['text_primary'],
                               anchor='w')
            file_label.pack(side=LEFT, fill=X, expand=True)

            # Кнопка удаления (теперь видимая и с правильным цветом)
            delete_btn = Button(file_frame,
                                text="🗑️ Удалить",
                                font=("Arial", 9),
                                bg=self.colors['danger'],
                                fg='white',
                                relief='flat',
                                padx=10,
                                pady=5,
                                command=lambda f=filename: self.delete_document(f))
            delete_btn.pack(side=RIGHT, padx=(10, 0))

    def add_document(self):
        """Добавление документа в библиотеку"""
        file_path = filedialog.askopenfilename(
            title="Выберите документ",
            filetypes=[
                ("Все файлы", "*.*"),
                ("PDF документы", "*.pdf"),
                ("Word документы", "*.doc *.docx"),
                ("Текстовые файлы", "*.txt"),
                ("Изображения", "*.jpg *.jpeg *.png *.gif")
            ]
        )

        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.sources_dir, filename)

            try:
                shutil.copy2(file_path, dest_path)
                messagebox.showinfo("Успех", f"Документ '{filename}' добавлен в библиотеку")

                # Обновляем список документов
                self.fill_documents_list()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить документ: {str(e)}")

    def delete_document(self, filename):
        """Удаление документа из библиотеки"""
        if messagebox.askyesno("Подтверждение", f"Удалить документ '{filename}'?"):
            try:
                file_path = os.path.join(self.sources_dir, filename)
                os.remove(file_path)
                messagebox.showinfo("Успех", f"Документ '{filename}' удален")

                # Обновляем список документов
                self.fill_documents_list()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить документ: {str(e)}")

    def show_user_management(self):
        """Управление пользователями (для админов)"""
        if not self.users[self.current_user].get('is_admin'):
            messagebox.showerror("Ошибка", "Недостаточно прав")
            return

        management = Toplevel(self.main_app)
        management.title("Управление пользователями")
        management.geometry("500x400")
        management.configure(bg=self.colors['surface'])
        management.transient(self.main_app)

        # Центрируем окно
        x = self.main_app.winfo_x() + (self.main_app.winfo_width() // 2) - 250
        y = self.main_app.winfo_y() + (self.main_app.winfo_height() // 2) - 200
        management.geometry(f"+{x}+{y}")

        Label(management, text="👥 Управление пользователями",
              font=("Arial", 16, "bold"),
              bg=self.colors['surface'],
              fg=self.colors['text_primary']).pack(pady=20)

        # Форма добавления
        add_frame = Frame(management, bg=self.colors['surface'], padx=30, pady=10)
        add_frame.pack(fill=X)

        Label(add_frame, text="Добавить пользователя:",
              font=("Arial", 12, "bold"),
              bg=self.colors['surface'],
              fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))

        input_frame = Frame(add_frame, bg=self.colors['surface'])
        input_frame.pack(fill=X)

        self.new_login = Entry(input_frame, width=15, font=("Arial", 11),
                               bg=self.colors['input_bg'], fg=self.colors['text_primary'],
                               relief='solid', bd=1)
        self.new_login.pack(side=LEFT, padx=(0, 10), ipady=5)

        self.new_password = Entry(input_frame, width=15, show="•", font=("Arial", 11),
                                  bg=self.colors['input_bg'], fg=self.colors['text_primary'],
                                  relief='solid', bd=1)
        self.new_password.pack(side=LEFT, padx=(0, 10), ipady=5)

        Button(input_frame, text="Добавить",
               bg=self.colors['primary'],
               fg='white',
               relief='flat',
               padx=15,
               command=self.add_user).pack(side=LEFT, ipady=5)

        # Список пользователей
        list_frame = Frame(management, bg=self.colors['surface'], padx=30, pady=10)
        list_frame.pack(fill=BOTH, expand=True)

        canvas = Canvas(list_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar = Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.user_list_frame = Frame(canvas, bg=self.colors['surface'])

        self.user_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.user_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.fill_user_list()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        Button(management, text="Закрыть",
               font=("Arial", 12),
               bg=self.colors['surface_light'],
               fg=self.colors['text_primary'],
               relief='flat',
               pady=10,
               command=management.destroy).pack(fill=X, padx=30, pady=15)

    def fill_user_list(self):
        """Заполнение списка пользователей"""
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        for i, username in enumerate(self.users.keys()):
            user_frame = Frame(self.user_list_frame,
                               bg=self.colors['surface_light'] if i % 2 == 0 else self.colors['surface'],
                               padx=15, pady=10)
            user_frame.pack(fill=X, pady=1)

            Label(user_frame, text=username,
                  anchor='w',
                  bg=user_frame['bg'],
                  fg=self.colors['text_primary']).pack(side=LEFT, fill=X, expand=True)

            password = self.users[username]["password"]
            Label(user_frame, text=password,
                  anchor='w',
                  bg=user_frame['bg'],
                  fg=self.colors['text_secondary']).pack(side=LEFT, padx=10)

            if username != self.current_user and username != "admin":
                Button(user_frame, text="Удалить",
                       bg=self.colors['danger'],
                       fg='white',
                       relief='flat',
                       padx=10,
                       pady=5,
                       command=lambda u=username: self.remove_user(u)).pack(side=RIGHT, padx=10)

    def add_user(self):
        username = self.new_login.get().strip()
        password = self.new_password.get().strip()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        if username in self.users:
            messagebox.showerror("Ошибка", "Пользователь уже существует")
            return

        self.users[username] = {"password": password, "is_admin": False}
        self.save_users()
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен")

        self.new_login.delete(0, END)
        self.new_password.delete(0, END)
        self.fill_user_list()

    def remove_user(self, username):
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {username}?"):
            del self.users[username]
            self.save_users()
            messagebox.showinfo("Успех", f"Пользователь {username} удален")
            self.fill_user_list()

    def logout(self):
        """Выход из аккаунта"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выйти из аккаунта?"):
            self.current_user = None
            self.show_login_screen()

    def clear_window(self):
        for widget in self.main_app.winfo_children():
            widget.destroy()

    def run(self):
        self.main_app.mainloop()


if __name__ == "__main__":
    app = NeuroHelpApp()
    app.run()