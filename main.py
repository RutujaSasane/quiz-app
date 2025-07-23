import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import os
import random

MODERN_FONT = ("Segoe UI", 20, "bold")
MODERN_FONT_LARGE = ("Segoe UI", 32, "bold")
MODERN_FONT_MED = ("Segoe UI", 18)
MODERN_FONT_SMALL = ("Segoe UI", 14)
BG_DARK = "#181f23"
TEAL = "#00e6e6"
CYAN = "#00adb5"
WHITE = "#f8f8f8"
VIBRANT = "#00e6e6"
RED = "#ff1744"
ORANGE = "#ff9100"

class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("Quiz App")
        master.attributes('-fullscreen', True)
        master.configure(bg=BG_DARK)
        self.username = None
        self.score = 0
        self.total_time_taken = 0
        self.current_question = 0
        self.selected_option = tk.IntVar(value=-1)
        self.timer_seconds = 30
        self.timer_running = False
        self.question_start_time = None
        self.answered = False
        self.questions = []
        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.clear_screen()
        self.header_frame = tk.Frame(self.master, bg=BG_DARK)
        self.header_frame.pack(fill=tk.X, pady=(40, 0))
        self.title_label = tk.Label(self.header_frame, text="General Knowledge Quiz", font=MODERN_FONT_LARGE, fg=TEAL, bg=BG_DARK, pady=20)
        self.title_label.pack()

        self.welcome_frame = tk.Frame(self.master, bg=BG_DARK)
        self.welcome_frame.pack(expand=True)
        self.welcome_label = tk.Label(self.welcome_frame, text="Welcome! Enter your name to start:", font=MODERN_FONT, fg=WHITE, bg=BG_DARK, pady=20)
        self.welcome_label.pack(pady=(40, 10))
        self.name_entry = tk.Entry(self.welcome_frame, font=MODERN_FONT, fg=BG_DARK, bg=WHITE, width=20, bd=0, relief=tk.FLAT, justify='center', highlightthickness=2, highlightcolor=TEAL)
        self.name_entry.pack(pady=10, ipady=8)
        self.name_entry.focus_set()
        self.start_button = tk.Button(self.welcome_frame, text="Start Quiz!", command=self.start_quiz, font=MODERN_FONT, fg=WHITE, bg=VIBRANT, activebackground=CYAN, activeforeground=WHITE, width=16, bd=0, pady=10, cursor="hand2", highlightthickness=0)
        self.start_button.pack(pady=20)
        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg=CYAN))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg=VIBRANT))
        self.master.bind('<Return>', lambda e: self.start_quiz())

    def start_quiz(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Please enter your name to start the quiz.")
            return
        self.username = name
        self.load_questions()
        self.current_question = 0
        self.score = 0
        self.total_time_taken = 0
        self.show_quiz_screen()

    def load_questions(self):
        with open("questions.json", "r") as f:
            questions = json.load(f)
        random.shuffle(questions)
        questions = questions[:10]
        for q in questions:
            opts = q['options']
            correct = q['answer']
            zipped = list(zip(opts, range(len(opts))))
            random.shuffle(zipped)
            new_opts, old_indices = zip(*zipped)
            q['options'] = list(new_opts)
            q['answer'] = old_indices.index(correct)
        self.questions = questions

    def show_quiz_screen(self):
        self.clear_screen()
        self.header_frame = tk.Frame(self.master, bg=BG_DARK)
        self.header_frame.pack(fill=tk.X, pady=(30, 0))
        self.title_label = tk.Label(self.header_frame, text=f"Good luck, {self.username}!", font=MODERN_FONT_LARGE, fg=TEAL, bg=BG_DARK, pady=20)
        self.title_label.pack()

        self.content_frame = tk.Frame(self.master, bg=BG_DARK)
        self.content_frame.pack(expand=True)

        self.question_label = tk.Label(self.content_frame, text="", wraplength=700, font=MODERN_FONT, fg=WHITE, bg=BG_DARK, pady=20, justify="center")
        self.question_label.pack(pady=(30, 10))

        self.options_frame = tk.Frame(self.content_frame, bg=BG_DARK)
        self.options_frame.pack(pady=5)
        self.options = []
        for i in range(4):
            rb = tk.Radiobutton(
                self.options_frame,
                text="",
                variable=self.selected_option,
                value=i,
                font=MODERN_FONT_MED,
                fg=BG_DARK,
                bg=WHITE,
                selectcolor=TEAL,
                activebackground=TEAL,
                activeforeground=BG_DARK,
                indicatoron=0,
                width=30,
                pady=6,
                bd=0,
                relief=tk.FLAT,
                highlightthickness=0,
                cursor="hand2"
            )
            rb.pack(pady=8)
            rb.bind("<Enter>", lambda e, b=rb: b.config(bg=CYAN))
            rb.bind("<Leave>", lambda e, b=rb: b.config(bg=WHITE))
            self.options.append(rb)

        self.timer_label = tk.Label(self.content_frame, text="Time left: 30s", font=MODERN_FONT_MED, fg=ORANGE, bg=BG_DARK)
        self.timer_label.pack(pady=8)

        self.feedback_label = tk.Label(self.content_frame, text="", font=MODERN_FONT_MED, fg=TEAL, bg=BG_DARK)
        self.feedback_label.pack(pady=8)

        self.button_frame = tk.Frame(self.content_frame, bg=BG_DARK)
        self.button_frame.pack(pady=18)
        self.submit_button = tk.Button(self.button_frame, text="Submit", command=self.submit_answer, font=MODERN_FONT, fg=WHITE, bg=VIBRANT, activebackground=CYAN, activeforeground=WHITE, width=14, bd=0, pady=10, cursor="hand2", highlightthickness=0)
        self.submit_button.grid(row=0, column=0, padx=18)
        self.submit_button.bind("<Enter>", lambda e: self.submit_button.config(bg=CYAN))
        self.submit_button.bind("<Leave>", lambda e: self.submit_button.config(bg=VIBRANT))
        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.exit_app, font=MODERN_FONT, fg=WHITE, bg=RED, activebackground=BG_DARK, activeforeground=RED, width=14, bd=0, pady=10, cursor="hand2", highlightthickness=0)
        self.exit_button.grid(row=0, column=1, padx=18)
        self.exit_button.bind("<Enter>", lambda e: self.exit_button.config(bg=ORANGE))
        self.exit_button.bind("<Leave>", lambda e: self.exit_button.config(bg=RED))
        self.show_question()

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def show_question(self):
        q = self.questions[self.current_question]
        self.selected_option.set(-1)  # Reset selection for each question
        self.question_label.config(text=f"Q{self.current_question+1}: {q['question']}")
        for i, opt in enumerate(q['options']):
            self.options[i].config(text=opt, state=tk.NORMAL)
        self.timer_seconds = 30
        self.update_timer_label()
        self.timer_running = True
        self.answered = False
        self.submit_button.config(state=tk.NORMAL)
        self.feedback_label.config(text="")
        self.question_start_time = time.time()
        self.start_timer()

    def start_timer(self):
        def countdown():
            while self.timer_seconds > 0 and self.timer_running and not self.answered:
                time.sleep(1)
                self.timer_seconds -= 1
                self.update_timer_label()
            if self.timer_seconds == 0 and self.timer_running and not self.answered:
                self.timer_running = False
                self.master.after(0, self.time_up)
        threading.Thread(target=countdown, daemon=True).start()

    def update_timer_label(self):
        self.timer_label.config(text=f"Time left: {self.timer_seconds}s")

    def submit_answer(self):
        if not self.timer_running or self.answered:
            return
        selected = self.selected_option.get()
        if selected == -1:
            self.feedback_label.config(text="Please select an option before submitting.", fg=ORANGE)
            return
        self.answered = True
        self.timer_running = False
        time_taken = int(time.time() - self.question_start_time)
        self.total_time_taken += min(time_taken, 30)
        correct = self.questions[self.current_question]['answer']
        for rb in self.options:
            rb.config(state=tk.DISABLED)
        if selected == correct:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg=TEAL)
        else:
            self.feedback_label.config(text=f"Incorrect! Correct: {self.questions[self.current_question]['options'][correct]}", fg=RED)
        self.submit_button.config(state=tk.DISABLED)
        self.master.after(1200, self.next_question)

    def time_up(self):
        if self.answered:
            return
        self.answered = True
        for rb in self.options:
            rb.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.total_time_taken += 30
        self.feedback_label.config(text="Time's up! No answer selected.", fg=ORANGE)
        self.master.after(1200, self.next_question)

    def next_question(self):
        if not self.answered:
            return
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.show_question()
        else:
            self.show_score()

    def show_score(self):
        self.update_leaderboard()
        leaderboard = self.get_leaderboard()
        self.clear_screen()
        self.header_frame = tk.Frame(self.master, bg=BG_DARK)
        self.header_frame.pack(fill=tk.X, pady=(30, 0))  # Reduced top padding
        self.title_label = tk.Label(self.header_frame, text="Quiz Completed!", font=MODERN_FONT_LARGE, fg=TEAL, bg=BG_DARK, pady=10)  # Reduced pady
        self.title_label.pack()

        self.result_frame = tk.Frame(self.master, bg=BG_DARK)
        self.result_frame.pack(expand=True)
        appreciation = "Congratulations!" if self.score >= 7 else ("Well done!" if self.score >= 4 else "Keep practicing!")
        result_msg = f"{appreciation} {self.username}, your score is {self.score} out of {len(self.questions)}.\nTotal Time: {self.total_time_taken}s"
        self.result_label = tk.Label(self.result_frame, text=result_msg, font=MODERN_FONT, fg=TEAL, bg=BG_DARK, pady=10, justify="center")
        self.result_label.pack(pady=(10, 10))  # Reduced space above and below

        leaderboard_title = tk.Label(self.result_frame, text="Leaderboard (Top 10)", font=MODERN_FONT, fg=CYAN, bg=BG_DARK, pady=6)
        leaderboard_title.pack()

        # Scrollable leaderboard box
        leaderboard_box = tk.Frame(self.result_frame, bg=BG_DARK, highlightbackground=CYAN, highlightthickness=2, bd=0)
        leaderboard_box.pack(pady=(6, 10), ipadx=8, ipady=8)
        canvas = tk.Canvas(leaderboard_box, bg=BG_DARK, highlightthickness=0, width=500, height=260)
        scrollbar = tk.Scrollbar(leaderboard_box, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Table headers
        header_bg = CYAN
        header_fg = BG_DARK
        tk.Label(scroll_frame, text="#", font=MODERN_FONT_SMALL, fg=header_fg, bg=header_bg, width=3, anchor="center", pady=4).grid(row=0, column=0, padx=(0, 10), sticky="ew")
        tk.Label(scroll_frame, text="Name", font=MODERN_FONT_SMALL, fg=header_fg, bg=header_bg, width=14, anchor="center", pady=4).grid(row=0, column=1, padx=(0, 10), sticky="ew")
        tk.Label(scroll_frame, text="Score", font=MODERN_FONT_SMALL, fg=header_fg, bg=header_bg, width=10, anchor="center", pady=4).grid(row=0, column=2, padx=(0, 10), sticky="ew")
        tk.Label(scroll_frame, text="Time", font=MODERN_FONT_SMALL, fg=header_fg, bg=header_bg, width=12, anchor="center", pady=4).grid(row=0, column=3, sticky="ew")

        for idx, entry in enumerate(leaderboard[:10], 1):
            rank_label = tk.Label(scroll_frame, text=f"{idx}.", font=MODERN_FONT_MED, fg=TEAL, bg=BG_DARK, width=3, anchor="e")
            rank_label.grid(row=idx, column=0, sticky="e", padx=(0, 10), pady=2)
            name_label = tk.Label(scroll_frame, text=entry['name'], font=MODERN_FONT_MED, fg=WHITE, bg=BG_DARK, width=14, anchor="w")
            name_label.grid(row=idx, column=1, sticky="w", padx=(0, 10), pady=2)
            score_label = tk.Label(scroll_frame, text=f"{entry['score']}", font=MODERN_FONT_MED, fg=CYAN, bg=BG_DARK, width=10, anchor="w")
            score_label.grid(row=idx, column=2, sticky="w", padx=(0, 10), pady=2)
            time_label = tk.Label(scroll_frame, text=f"{entry['time']}s", font=MODERN_FONT_SMALL, fg=ORANGE, bg=BG_DARK, width=12, anchor="w")
            time_label.grid(row=idx, column=3, sticky="w", pady=2)

        self.button_frame = tk.Frame(self.result_frame, bg=BG_DARK)
        self.button_frame.pack(pady=12)  # Reduced bottom padding
        self.retry_button = tk.Button(self.button_frame, text="Retry", command=self.retry_quiz, font=MODERN_FONT, fg=WHITE, bg=VIBRANT, activebackground=CYAN, activeforeground=WHITE, width=14, bd=0, pady=10, cursor="hand2", highlightthickness=0)
        self.retry_button.grid(row=0, column=0, padx=12)
        self.retry_button.bind("<Enter>", lambda e: self.retry_button.config(bg=CYAN))
        self.retry_button.bind("<Leave>", lambda e: self.retry_button.config(bg=VIBRANT))
        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.exit_app, font=MODERN_FONT, fg=WHITE, bg=RED, activebackground=BG_DARK, activeforeground=RED, width=14, bd=0, pady=10, cursor="hand2", highlightthickness=0)
        self.exit_button.grid(row=0, column=1, padx=12)
        self.exit_button.bind("<Enter>", lambda e: self.exit_button.config(bg=ORANGE))
        self.exit_button.bind("<Leave>", lambda e: self.exit_button.config(bg=RED))

    def retry_quiz(self):
        self.load_questions()
        self.current_question = 0
        self.score = 0
        self.total_time_taken = 0
        self.show_quiz_screen()

    def update_leaderboard(self):
        entry = {
            "name": self.username,
            "score": self.score,
            "time": self.total_time_taken
        }
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        data.append(entry)
        with open("leaderboard.json", "w") as f:
            json.dump(data, f, indent=2)

    def get_leaderboard(self):
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        data.sort(key=lambda x: (-x['score'], x['time'], x['name'].lower()))
        return data[:10]

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the quiz?"):
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
