import time
from tkinter import *
from tkinter import ttk
from minimax import is_game_over, minimax, get_winner, result
from functools import partial
from constants import *



button_style = ttk.Style()
button_style.configure('board.TButton', font=('Helvetica', 70))


def initial_state():
    """Return a empty 3x3 grid"""
    return [[BLANK for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
class GameBoard(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                b = ttk.Button(self, text=" ", style="board.TButton")
                b.grid(column=i, row=j, sticky=NSEW)
                self.grid_columnconfigure(i, weight=1)
                self.grid_rowconfigure(j, weight=1)

    def display_move(self, x, y, player):
        button = self.grid_slaves(row=x, column=y)[0]
        button.config(state=DISABLED, text=player)

    def add_button_click_events(self, player):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                button = self.grid_slaves(row=i, column=j)[0]
                move_with_args = partial(self.button_clicked, i, j, player)
                button.config(command=move_with_args)

    def button_clicked(self, x, y, player):
        self.event_generate("<<PlayerClickedTile>>", x=x, y=y)

    def get_all_buttons(self):
        buttons = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                buttons.append(self.grid_slaves(row=i, column=j)[0])
        return buttons

    def set_busy(self, busy: bool):
        for button in self.get_all_buttons():
            if busy:
                button.config(cursor="watch")
            else:
                button.config(cursor="")

    def set_frame_state(self, disabled: bool):
        for button in self.get_all_buttons():
            if disabled:
                button.config(state=DISABLED)
            else:
                if button['text'] == " ":
                    button.config(state=NORMAL)

    def clear_board(self):
        for button in self.get_all_buttons():
            button.config(state=NORMAL)
            button.config(text=" ")


class PopupFrame(Frame):
    def __init__(self, master, game_board=None, showing=False, *args, **kwargs):
        super().__init__(master, bg="white", highlightbackground="grey", highlightthickness=2, *args, **kwargs)
        self.game_board = game_board
        self.showing = showing
        master.bind("<Configure>", self.resize_frame)

        if showing:
            self.show()

    def get_width_height_x_y(self):
        pwidth, pheight = self.master.winfo_width(), self.master.winfo_height()
        # width, height = pwidth - 150, pheight - 150
        width, height = 300, 300
        x, y = pwidth / 2 - width / 2, pheight / 2 - height / 2
        return width, height, x, y

    def resize_frame(self, *args):
        if self.showing:
            width, height, x, y = self.get_width_height_x_y()
            self.place(width=width, height=height, x=x, y=y)

    def show(self):
        self.showing = True
        self.game_board.set_frame_state(disabled=True)
        width, height, x, y = self.get_width_height_x_y()
        self.place(width=width, height=height, x=x, y=y)

    def hide(self):
        self.showing = False
        self.game_board.set_frame_state(disabled=False)
        self.place_forget()


class StartScreen(PopupFrame):
    def __init__(self, master, game_board, set_player, set_not_ai, text="Play Game"):
        super().__init__(master, game_board=game_board)
        # pass the method to set the current player
        self.set_player = set_player
        self.set_not_ai = set_not_ai

        self.label = Label(self, text=text, bg="white", fg="black", font=("Arial", 20, "bold"))
        self.play_as_X = ttk.Button(self, text=f"Play as {X}", command=self.play_as_X)
        self.play_as_O = ttk.Button(self, text=f"Play as {O}", command=self.play_as_O)
        self.two_player = ttk.Button(self, text="Play 2 player game", command=self.play_2_player)

        self.label.grid(row=0, column=0, sticky=NSEW)
        self.play_as_X.grid(row=1, column=0, sticky=NSEW)
        self.play_as_O.grid(row=2, column=0, sticky=NSEW)
        self.two_player.grid(row=3, column=0, sticky=NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def play_as_X(self, *args):
        self.hide()
        self.set_player(X)

    def play_as_O(self, *args):
        self.hide()
        self.set_player(O)

    def play_2_player(self, *args):
        self.hide()
        self.set_not_ai()

    def set_label(self, text):
        self.label['text'] = text


class Application(Frame):
    def __init__(self, title, master=None, *args, **kwargs):
        super().__init__(master, bg="orange", *args, **kwargs)
        self.master.title(title)
        self.master.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.master.minsize(width=MIN_WINDOW_SIZE[0], height=MIN_WINDOW_SIZE[1])
        self.status_label = ttk.Label()
        self.status_label.pack()
        self.game_board = GameBoard(self.master)
        self.game_board.pack(fill=BOTH, expand=YES)
        self.game_board.bind("<<PlayerClickedTile>>", self.PlayerClickedTile)
        self.against_ai = True
        self.board = initial_state()
        self.start_game_frame = StartScreen(self.master,
                                            game_board=self.game_board,
                                            set_player=self.set_player,
                                            set_not_ai=self.set_not_ai)
        self.start_game_frame.show()

        self.player = X

        self.game_board.add_button_click_events(self.player)

    def set_player(self, player):
        self.restart_game()
        self.update()
        self.player = player
        self.set_status(f"{player}'s turn")
        if player == O:
            # if the player is playing the AI and the AI is x then the AI should go first
            if self.against_ai:
                self.ai_move()

    def set_status(self, text):
        self.status_label['text'] = text
        self.update()

    def set_not_ai(self):
        self.restart_game()
        self.against_ai = False
        self.player = X

    def PlayerClickedTile(self, event):
        self.player_move(event.x, event.y)
        if self.check_game_over():
            return

        if self.against_ai:
            self.ai_move()

            if self.check_game_over():
                return
        else:
            # if not playing an ai must toggle between x and o turns
            if self.player == X:
                self.player = O
            else:
                self.player = X
            self.set_status(f"{self.player}'s turn")

    def player_move(self, x, y):
        self.board[x][y] = self.player
        self.game_board.display_move(x, y, self.player)
        self.update()

    def check_game_over(self):
        if is_game_over(self.board):
            self.game_board.set_busy(True)
            win = get_winner(self.board)
            if win is None:
                self.set_status("Tie Game")
                self.start_game_frame.set_label("Tie Game")
            else:
                self.start_game_frame.set_label(f"{win} wins")
                self.set_status(f"{win} wins")
            self.update()
            time.sleep(SHOW_GAME_OVER_TIME)
            self.game_board.set_busy(False)
            self.start_game_frame.show()
            return True
        return False

    def ai_move(self):
        self.set_status("Computer's turn")
        self.game_board.set_busy(True)
        start = time.time()

        move = minimax(self.board)
        self.board = result(self.board, move)

        if self.player == X:
            self.game_board.display_move(move[0], move[1], O)
        else:
            self.game_board.display_move(move[0], move[1], X)

        end = time.time()
        elapsed_time = end - start
        time.sleep(max(AI_THINK_TIME - elapsed_time, 0))
        self.game_board.set_busy(False)
        self.set_status(f"{self.player}'s turn")

    def restart_game(self):
        self.player = X
        self.against_ai = True
        self.board = initial_state()
        self.game_board.clear_board()
        self.set_status(f"{self.player}'s turn")


if __name__ == '__main__':
    app = Application('Tic Tac Toe')
    icon = PhotoImage(file="icon.png")
    app.master.iconphoto(True, icon)
    app.mainloop()
