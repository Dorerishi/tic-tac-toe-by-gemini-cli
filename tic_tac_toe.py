import os
import sys

# Platform-specific imports for single-key press detection
try:
    import tty, termios
    UNIX = True
except ImportError:
    import msvcrt
    UNIX = False

class Game:
    """Manages the internal state and logic of the Tic-Tac-Toe game."""
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'X'
        self.winner = None

    def make_move(self, row, col):
        if self.board[row][col] is None:
            self.board[row][col] = self.current_player
            if self.check_win(self.current_player):
                self.winner = self.current_player
            elif self.check_draw():
                self.winner = 'Draw'
            else:
                self.switch_player()
            return True
        return False

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_win(self, player):
        # Check rows, columns, and diagonals
        for i in range(self.board_size):
            if all(self.board[i][j] == player for j in range(self.board_size)) or \
               all(self.board[j][i] == player for j in range(self.board_size)):
                return True
        if all(self.board[i][i] == player for i in range(self.board_size)) or \
           all(self.board[i][(self.board_size - 1) - i] == player for i in range(self.board_size)):
            return True
        return False

    def check_draw(self):
        return all(cell is not None for row in self.board for cell in row)

class CommandLineUI:
    """Handles all command-line display and user input."""
    
    COLOR_X = '\033[91m'  # Red
    COLOR_O = '\033[94m'  # Blue
    COLOR_RESET = '\033[0m'
    HIGHLIGHT_BG = '\033[47m' # White background

    def __init__(self, game):
        self.game = game

    def get_key(self):
        if UNIX:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        else:
            return msvcrt.getch().decode('utf-8')

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_board(self, cursor_pos):
        self.clear_screen()
        print(f"Player {self.game.current_player}'s turn")
        print("Use WASD to move, Space to place, Q to quit.")
        for r in range(self.game.board_size):
            display_row = []
            for c in range(self.game.board_size):
                cell = self.game.board[r][c]
                if cell == 'X':
                    colored_cell = f"{self.COLOR_X}{cell}{self.COLOR_RESET}"
                elif cell == 'O':
                    colored_cell = f"{self.COLOR_O}{cell}{self.COLOR_RESET}"
                else:
                    colored_cell = ' '

                if (r, c) == cursor_pos:
                    display_row.append(f"{self.HIGHLIGHT_BG}{colored_cell} {self.COLOR_RESET}")
                else:
                    display_row.append(f" {colored_cell} ")
            print("|".join(display_row))
            if r < self.game.board_size - 1:
                print("" + "---" * self.game.board_size)

    def get_move_with_pointer(self):
        cursor_r, cursor_c = 0, 0
        while True:
            self.display_board((cursor_r, cursor_c))
            key = self.get_key().lower()

            if key == 'w': cursor_r = max(0, cursor_r - 1)
            elif key == 's': cursor_r = min(self.game.board_size - 1, cursor_r + 1)
            elif key == 'a': cursor_c = max(0, cursor_c - 1)
            elif key == 'd': cursor_c = min(self.game.board_size - 1, cursor_c + 1)
            elif key == ' '::
                if self.game.board[cursor_r][cursor_c] is None:
                    return cursor_r, cursor_c
            elif key == 'q':
                self.clear_screen()
                print("Goodbye!")
                exit()

    def display_game_over(self):
        self.display_board((-1, -1)) # No cursor
        if self.game.winner == 'Draw':
            print("\nIt's a draw!")
        else:
            winner = self.game.winner
            colored_winner = f"{self.COLOR_X if winner == 'X' else self.COLOR_O}{winner}{self.COLOR_RESET}"
            print(f"\nPlayer {colored_winner} wins!")

    def run(self):
        while self.game.winner is None:
            row, col = self.get_move_with_pointer()
            self.game.make_move(row, col)
        self.display_game_over()

if __name__ == "__main__":
    game = Game()
    ui = CommandLineUI(game)
    ui.run()
