import tkinter as tk
from tkinter import messagebox
import random
import copy


class Sudoku:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.frame(400, 400)
        self.entries = []
        self.puzzle = []
        self.solution = []
        self.original = []
        self.difficulty = tk.StringVar(value="")
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

        label = tk.Label(self.root, text="Select Game Difficulty", font=("Times New Roman", 16, "bold"))
        label.pack(pady=30)

        for level in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(
                self.root, text=level, variable=self.difficulty,
                value=level, font=("Arial", 12)
            ).pack(anchor="w", padx=40)

        tk.Button(self.root, text="Start Game", font=("Times New Roman", 14, "bold"), command=self.load_game).pack(pady=20)


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

        self.create_grid()


    def create_grid(self):
        frame = tk.Frame(self.root)
        frame.pack()

        self.entries = []

        for i in range(9):
            row = []
            for j in range(9):
                val = self.puzzle[i][j]
                entry = tk.Entry(frame, width=2, font=("Arial", 16), justify="center")
                if val != 0:
                    entry.insert(0, str(val))
                    entry.config(state="disabled", disabledforeground="blue")
                entry.grid(row=i, column=j, padx=1, pady=1)
                row.append(entry)
            self.entries.append(row)


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
