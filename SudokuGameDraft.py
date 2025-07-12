import tkinter as tk
from tkinter import messagebox
import random
import copy
import time


class Sudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.frame(450, 450)
        self.entries = []
        self.puzzle = []
        self.solution = []
        self.original = []
        self.difficulty = tk.StringVar(value="")
        self.score = 0
        self.start_time = None
        self.timer_label = None
        self.score_label = None
        self.hint_label = None
        self.numbers_left_label = None
        self.timer_running = False
        self.cell_states = {}
        self.move_history = []
        self.pause_button = None
        self.paused = False
        self.hints_used = 0
        self.difficulty_screen()


    def frame(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')


    def difficulty_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Select Game Difficulty", font=("Helvetica", 16, "bold"))
        label.pack(pady=30)

        for level in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(
                self.root, text=level, variable=self.difficulty,
                value=level, font=("Arial", 12)
            ).pack(anchor="w", padx=40)

        tk.Button(self.root, text="Start Game", font=("Helvetica", 14, "bold"), command=self.load_game).pack(pady=20)


    def load_game(self):
        level = self.difficulty.get()
        if not level:
            messagebox.showwarning("Warning", "Please select a difficulty level!")
            return

        full_board = self.generate_board()
        self.solution = copy.deepcopy(full_board)
        self.puzzle = self.remove_num(full_board, level)
        self.original = copy.deepcopy(self.puzzle)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.score = 0
        self.hints_used = 0
        self.timer_running = True
        self.paused = False
        self.cell_states = {}
        self.move_history = []
        self.start_time = time.time()

        self.create_grid()
        self.update_timer()
        self.update_numbers_left()


    def create_grid(self):
        grid_frame = tk.Frame(self.root, bg="black")
        grid_frame.pack(pady=10)

        self.entries = []

        for i in range(9):
            row = []
            for j in range(9):
                val = self.puzzle[i][j]

                top = 2 if i % 3 == 0 else 1
                bottom = 2 if i == 8 else (2 if (i + 1) % 3 == 0 else 1)
                left = 2 if j % 3 == 0 else 1
                right = 2 if j == 8 else (2 if (j + 1) % 3 == 0 else 1)

                cell_frame = tk.Frame(
                    grid_frame,
                    highlightbackground="black",
                    highlightcolor="black",
                    highlightthickness=0,
                    bd=0
                )
                cell_frame.grid(row=i, column=j, padx=(left, right), pady=(top, bottom))

                entry = tk.Entry(
                    cell_frame,
                    width=2,
                    font=("Arial", 16),
                    justify="center",
                    relief="solid",
                    bd=0
                )

                if val != 0:
                    entry.insert(0, str(val))
                    entry.config(state="disabled", disabledforeground="blue")
                else:
                    var = tk.StringVar()
                    entry.config(textvariable=var)
                    var.trace_add("write", lambda *args, i=i, j=j, var=var: self.cell_change(i, j, var))
                    self.cell_states[(i, j)] = None

                entry.pack()
                row.append(entry)
            self.entries.append(row)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        button_frame = tk.Frame(control_frame)
        button_frame.pack()

        tk.Button(button_frame, text="Reset", font=("Helvetica", 12), command=self.reset_grid).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Hint", font=("Helvetica", 12), command=self.give_hint).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Undo", font=("Helvetica", 12), command=self.undo_move).grid(row=0, column=2, padx=5)
        self.pause_button = tk.Button(button_frame, text="Pause", font=("Helvetica", 12), command=self.toggle_pause)
        self.pause_button.grid(row=0, column=3, padx=5)

        status_frame = tk.Frame(control_frame)
        status_frame.pack(pady=5)

        self.score_label = tk.Label(status_frame, text=f"Score: {self.score}", font=("Arial", 12))
        self.score_label.pack(side="left", padx=10)

        self.timer_label = tk.Label(status_frame, text="Time: 00:00", font=("Arial", 12))
        self.timer_label.pack(side="left", padx=10)

        self.hint_label = tk.Label(status_frame, text=f"Hints left: {3 - self.hints_used}", font=("Arial", 12))
        self.hint_label.pack(side="left", padx=10)

        self.numbers_left_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.numbers_left_label.pack(pady=5)


    def update_timer(self):
        if self.timer_running and not self.paused:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.config(text=f"Time: {mins:02}:{secs:02}")
        self.root.after(1000, self.update_timer)


    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")


    def cell_change(self, i, j, var):
        if self.paused:
            return

        val = var.get()
        correct_val = str(self.solution[i][j])
        entry = self.entries[i][j]
        previous_state = self.cell_states[(i, j)]

        self.move_history.append((i, j, entry.get(), previous_state, entry["state"]))

        if val == correct_val and previous_state != "correct":
            if previous_state == "wrong":
                self.score += 15
            else:
                self.score += 10
            self.cell_states[(i, j)] = "correct"
            entry.config(fg="green", state="disabled", disabledforeground="green")
        elif val != correct_val and val != "":
            if previous_state != "wrong":
                if previous_state == "correct":
                    self.score -= 15
                else:
                    self.score -= 5
                self.cell_states[(i, j)] = "wrong"
                entry.config(fg="red")
        elif val == "":
            self.cell_states[(i, j)] = None
            entry.config(fg="black")

        self.update_score()
        self.update_numbers_left()

        if all(state == "correct" for state in self.cell_states.values()):
            self.timer_running = False
            self.show_completion_popup()


    def show_completion_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Congratulations!")
        
        popup_width = 300
        popup_height = 150
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (popup_width // 2)
        y = (screen_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        
        popup.transient(self.root)  
        popup.grab_set()  

        label = tk.Label(popup, text=f"You've completed the Sudoku!\nScore: {self.score}", font=("Arial", 12))
        label.pack(pady=15)

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        btn_new = tk.Button(button_frame, text="New Game", font=("Helvetica", 12, "bold"), width=10, command=lambda: self.start_new_game(popup))
        btn_new.grid(row=0, column=0, padx=10)

        btn_exit = tk.Button(button_frame, text="Exit", font=("Helvetica", 12, "bold"), width=10, command=self.root.destroy)
        btn_exit.grid(row=0, column=1, padx=10)


    def start_new_game(self, popup):
        popup.destroy()
        self.difficulty.set("")
        self.difficulty_screen()


    def undo_move(self):
        if not self.move_history:
            return

        i, j, prev_val, prev_state, prev_entry_state = self.move_history.pop()
        entry = self.entries[i][j]
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, prev_val)
        entry.config(fg="black" if prev_state is None else ("green" if prev_state == "correct" else "red"))
        entry.config(state=prev_entry_state)
        self.cell_states[(i, j)] = prev_state

        self.score = 0
        for (row, col), state in self.cell_states.items():
            if state == "correct":
                self.score += 10
            elif state == "wrong":
                self.score -= 5
        self.update_score()
        self.update_numbers_left()


    def reset_grid(self):
        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                val = self.original[i][j]
                if val != 0:
                    entry.insert(0, str(val))
                    entry.config(state="disabled", disabledforeground="blue")
                else:
                    entry.config(fg="black", bg="white")
        self.score = 0
        self.cell_states = {(i, j): None for i in range(9) for j in range(9) if self.original[i][j] == 0}
        self.move_history.clear()
        self.update_score()
        self.hints_used = 0
        self.hint_label.config(text=f"Hints left: {3 - self.hints_used}")
        self.update_numbers_left()


    def give_hint(self):
        if self.hints_used >= 3:
            messagebox.showinfo("Hint Limit Reached", "You can only use 3 hints per game.")
            return

        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] == 0 and self.entries[i][j].get() == "":
                    self.entries[i][j].insert(0, str(self.solution[i][j]))
                    self.entries[i][j].config(fg="green", state="disabled", disabledforeground="green", bg="#ccffcc")
                    self.entries[i][j].after(500, lambda e=self.entries[i][j]: e.config(bg="white"))
                    self.cell_states[(i, j)] = "correct"
                    self.score -= 15
                    self.hints_used += 1
                    self.update_score()
                    self.hint_label.config(text=f"Hints left: {3 - self.hints_used}")
                    self.update_numbers_left()
                    return

        messagebox.showinfo("No Hint", "No more empty cells to hint.")


    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")


    def update_numbers_left(self):
        counts = {str(i): 9 for i in range(1, 10)}

        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if val in counts and (self.entries[i][j]['state'] == 'disabled' or self.cell_states.get((i,j)) == 'correct'):
                    counts[val] -= 1

        display_text = "Numbers left:  "
        for num in range(1, 10):
            display_text += f"{num}-{[counts[str(num)]]}  "

        self.numbers_left_label.config(text=display_text)


    def generate_board(self):
        board = [[0] * 9 for _ in range(9)]
        self.fill_board(board)
        return board


    def fill_board(self, board):
        num_list = list(range(1, 10))
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    random.shuffle(num_list)
                    for num in num_list:
                        if self.place_num(board, i, j, num):
                            board[i][j] = num
                            if self.fill_board(board):
                                return True
                            board[i][j] = 0
                    return False
        return True


    def place_num(self, board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
        return True


    def remove_num(self, board, difficulty):
        level_map = {
            "Easy": 35,
            "Medium": 45,
            "Hard": 55
        }
        cells_to_remove = level_map.get(difficulty, 45)
        puzzle = copy.deepcopy(board)

        count = 0
        while count < cells_to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if puzzle[row][col] != 0:
                puzzle[row][col] = 0
                count += 1
        return puzzle


if __name__ == "__main__":
    root = tk.Tk()
    app = Sudoku(root)
    root.mainloop()
