# ===============================
# CONNECT FOUR — NEGAMAX AI
# ===============================

ROWS = 6
COLS = 7
INF = 10**9

EMPTY = 0
PLAYER = 1     # AI
OPPONENT = -1  # Human


# ---------- BOARD ----------

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def print_board(board):
    print()
    for row in board:
        print("|", end="")
        for cell in row:
            if cell == PLAYER:
                print(" X ", end="")
            elif cell == OPPONENT:
                print(" O ", end="")
            else:
                print(" . ", end="")
        print("|")
    print("  0  1  2  3  4  5  6 ")
    print()


def valid_moves(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def make_move(board, col, player):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r
    return None


def undo_move(board, col):
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return


# ---------- WIN CHECK ----------

def check_win(board, player):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == player for i in range(4)):
                return True

    # Diagonal /
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True

    # Diagonal \
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True

    return False


# ---------- EVALUATION ----------

def evaluate_window(window, player):
    opponent = -player
    score = 0

    if window.count(player) == 4:
        score += 100000
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 500
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 50

    # Strong blocking incentive
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 800

    return score


def evaluate_board(board, player):
    if check_win(board, player):
        return INF
    if check_win(board, -player):
        return -INF

    score = 0

    # Center column bonus
    center = [board[r][COLS // 2] for r in range(ROWS)]
    score += center.count(player) * 6

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = [board[r+i][c] for i in range(4)]
            score += evaluate_window(window, player)

    # Diagonal /
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Diagonal \
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    return score


# ---------- NEGAMAX + ALPHA-BETA ----------

def negamax(board, depth, alpha, beta, player):
    if depth == 0 or check_win(board, player) or check_win(board, -player):
        return evaluate_board(board, player)

    max_eval = -INF

    for col in valid_moves(board):
        make_move(board, col, player)
        score = -negamax(board, depth - 1, -beta, -alpha, -player)
        undo_move(board, col)

        max_eval = max(max_eval, score)
        alpha = max(alpha, score)

        if alpha >= beta:
            break  # cutoff

    return max_eval


def best_move(board, depth, player):
    best_score = -INF
    best_col = None

    for col in valid_moves(board):
        make_move(board, col, player)
        score = -negamax(board, depth - 1, -INF, INF, -player)
        undo_move(board, col)

        if score > best_score:
            best_score = score
            best_col = col

    return best_col


# ---------- GAME LOOP ----------

def play():
    board = create_board()
    print("Connect Four")
    print("You are O, AI is X")
    print_board(board)

    turn = OPPONENT  # human starts

    while True:
        if turn == OPPONENT:
            col = int(input("Your move (0-6): "))
            if col not in valid_moves(board):
                print("Invalid move!")
                continue
            make_move(board, col, OPPONENT)
        else:
            print("AI thinking...")
            col = best_move(board, depth=5, player=PLAYER)
            make_move(board, col, PLAYER)

        print_board(board)

        if check_win(board, turn):
            print("You win!" if turn == OPPONENT else "AI wins!")
            break

        if not valid_moves(board):
            print("Draw!")
            break

        turn = -turn


if __name__ == "__main__":
    play()
