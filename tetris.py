from os import name, system
from time import sleep
from random import choice
if name == 'nt':
    from msvcrt import getch, kbhit
else:
    from sys import stdin
    from termios import tcgetattr, tcsetattr, ICANON, ECHO, TCSAFLUSH, TCSADRAIN
    from tty import setcbreak
    from select import select
    def kbhit():
        return select([stdin], [], [], 0)[0] == []
    def getch():
        old_settings = tcgetattr(stdin)
        new_settings = tcgetattr(stdin)
        new_settings[3] = (new_settings[3] & ~ICANON & ~ECHO)
        tcsetattr(stdin.fileno(), TCSAFLUSH, new_settings)
        setcbreak(stdin.fileno())
        c = stdin.read(1)
        if c == '\x1b':
            c2 = stdin.read(2)
            if c2 == "[A":
                return 72
            elif c2 == "[B":
                return 80
            elif c2 == "[C":
                return 77
            elif c2 == "[D":
                return 75
        else:
            return ord(c)

# -----------------------------------------------------
# CHECKS

def collision_down(cords: list[list[int]], st: list[list[str]]) -> bool:
    for k in cords:
        if k[0] == 21 or "&" in st[k[0] + 1][k[1]]:
            return True
    return False


def collision_side(val: int, cords: list[list[int]], st: list[list[str]]) -> bool:
    for k in cords:
        if "&" in st[k[0]][k[1] + val]:
            return True
    return False


# -----------------------------------------------------
# PRINT

def clear() -> None:
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def draw(st: list[list[str]]) -> None:  # st == middle screen
    global right_screen, left_screen, speed_incr
    clear()
    print("||", end="")
    print("~" * 20, end="||")
    print("~" * 20, end="||")
    print("~" * 20, end="||\n")
    for i in range(2, 22):
        print("||", end="")
        [print(j, end="") for j in left_screen[i]]
        print("||", end="")
        [print(j*2, end="") for j in st[i]]
        print("||", end="")
        [print(j, end="") for j in right_screen[i]]
        print("||")
    print("||", end="")
    print("~" * 20, end="||")
    print("~" * 20, end="||")
    print("~" * 20, end="||\n")


def refresh(cords: list[list[int]], func: tuple[list[list[int]], list[list[str]]], cur: str, st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    preview = "\033[38;5;244m\033[48;5;244m"

    for k in cords:
        st[k[0]][k[1]] = " "  # clear previous cords
    cords, st = func
    preview_cords, st = drop(cords, st, False)
    for k in preview_cords:
        st[k[0]][k[1]] = f"{preview}$\033[0m"  # draw preview
    for k in cords:
        st[k[0]][k[1]] = f"{piece_colors[cur]}@\033[0m"  # draw new piece
    draw(st)

    if preview_cords != cords:
        for k in preview_cords:
            st[k[0]][k[1]] = " "
    return cords, st


def line_clear(st: list[list[str]], sco: int, com: int, dif: bool) -> tuple[list[list[str]], int, int, bool]:
    global speed_incr, difficulty
    clr_lns: list[int] = []
    points: tuple[int] = (100, 300, 500, 800)
    for k in range(len(st)):
        if "&" in st[k][0]:
            full = True
            for p in range(1, len(st[k])):
                if "&" not in st[k][p]:
                    full = False
                    break
            if full:
                for q in range(len(st[k])):
                    st[k][q] = " "
                clr_lns.append(k)
    n: int = len(clr_lns)
    speed_incr += n * difficulty
    if n > 0:
        act_sco: float = points[n - 1] + (50 * com)
        if dif:
            act_sco *= 1.5
        if n == 4:
            dif = True
        else:
            dif = False
        sco += int(act_sco)
        return [[" " for _ in range(10)] for _ in range(n)] + st[:clr_lns[0]] + st[clr_lns[-1] + 1:], sco, com + 1, dif
    return st, sco, 0, dif


def draw_menu(st: list[list[str]], menu_type: str) -> None:
    global left_screen, right_screen, menu_content
    clear()
    print("||", end="")
    [print("~" * 20, end="||") for _ in range(3)]
    print()
    for i in range(2, 9):
        print("||", end="")
        [print(j, end="") for j in left_screen[i]]
        print("||", end="")
        [print(j*2, end="") for j in st[i]]
        print("||", end="")
        [print(j, end="") for j in right_screen[i]]
        print("||")
    for i in range(9,15):
        print("||", end="")
        [print(j, end="") for j in left_screen[i]]
        if menu_type == "over" and i == 11:
            score_len = len(str(score))
            left_offset = (5 - max(0, (score_len) - 9))
            right_offset = 20 - (left_offset + score_len + 5)
            print(f'! Score:{" " * left_offset}{score}{" " * right_offset}!', end="")
        else:
            print(menu_content[menu_type][i-9], end="")
        [print(j, end="") for j in right_screen[i]]
        print("||")
    for i in range(15, 22):
        print("||", end="")
        [print(j, end="") for j in left_screen[i]]
        print("||", end="")
        [print(j*2, end="") for j in st[i]]
        print("||", end="")
        [print(j, end="") for j in right_screen[i]]
        print("||")
    print("||", end="")
    [print("~" * 20, end="||") for _ in range(3)]
    print()
    return


menu_content: dict[str, tuple[str]] = {
    "start":("&" * 24,
             "! Choose a difficulty: !",
             "! Easy: Press 1        !",
             "! Medium: Press 2      !",
             "! Hard: Press 3        !",
             "&" * 24),
    "pause":("&" * 24,
             "!     Game Paused      !",
             "! Continue:  Press Esc !",
             "! New Game:  Press R   !",
             "! Quit:      Press Q   !",
             "&" * 24),
    "over": ("&" * 24,
             "!      Game Over!      !",
             "! Score:     0         !",
             "! New Game:  Press R   !",
             "! Quit:      Press Q   !",
             "&" * 24)
}

# -----------------------------------------------------
# MOVEMENT

def rotate(cords: list[list[int]], cur: str, rot: int, st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    old_cords: list[list[int]] = cords
    x_cords: list[int] = [i[1] for i in cords]
    if cur == "I":
        xcord_I: int = x_cords[0]
        if xcord_I == x_cords[3]:
            if rot == 3:
                if xcord_I == 0:  # all elements of "I" are touching left wall
                    cords = [[k[0], k[1] + 2] for k in cords]
                elif xcord_I == 1:  # one element of "I" is touching left wall
                    cords = [[k[0], k[1] + 1] for k in cords]
                elif xcord_I == 9:  # -||- right wall
                    cords = [[k[0], k[1] - 1] for k in cords]
            if rot == 1:
                if xcord_I == 9:  # all elements of "I" are touching right wall
                    cords = [[k[0], k[1] - 2] for k in cords]
                elif xcord_I == 8:  # one element of "I" is touching right wall
                    cords = [[k[0], k[1] - 1] for k in cords]
                elif xcord_I == 0:  # -||- left wall
                    cords = [[k[0], k[1] + 1] for k in cords]
    else:
        if 0 in x_cords:  # at least one element of piece is touching left wall
            cords = [[k[0], k[1] + 1] for k in cords]
        if 9 in x_cords:  # -||- right wall
            cords = [[k[0], k[1] - 1] for k in cords]
    ncords = [[k[0] + rot_tbl[cur][rot][i][0], k[1] + rot_tbl[cur][rot][i][1]] for i, k in enumerate(cords)]
    for k in ncords:
        if k[0] > 21 or k[1] > 9 or "&" in st[k[0]][k[1]]:
            return old_cords, st
    return ncords, st


def move_side(val: int, cords: list[list[int]], st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    if not collision_side(val, cords, st):
        cords = [[k[0], k[1] + val] for k in cords]
    return cords, st


def move_down(cords: list[list[int]], st: list[list[str]], scored: bool) \
        -> tuple[list[list[int]], list[list[str]]]:
    global score
    if scored:
        score += 1
    return [[k[0] + 1, k[1]] for k in cords], st


def drop(cords: list[list[int]], st: list[list[str]], scored: bool) \
        -> tuple[list[list[int]], list[list[str]]]:
    global score
    while not collision_down(cords, st):
        if scored:
            score += 2
        cords = [[k[0] + 1, k[1]] for k in cords]
    return cords, st


# -----------------------------------------------------
# OTHER

def store(cords: list[list[int]], stored: str, cur: str, lim: bool, st: list[list[str]]) \
        -> tuple[list[list[int]], str, str, bool, list[list[str]]]:
    global right_screen
    if lim:
        return cords, stored, cur, lim, st
    for k in cords:
        st[k[0]][k[1]] = " "
    # Clear previous stored piece from left_screen
    left_screen[10] = [*"                    "]
    left_screen[11] = [*"                    "]
    # Add current stored piece to left_screen 
    for k in default_cords[cur]:
        left_screen[9 + k[0]][k[1] * 2] = f"{piece_colors[cur]}@\033[0m"
        left_screen[9 + k[0]][k[1] * 2+1] = f"{piece_colors[cur]}@\033[0m"
    if stored == "":
        new = generate()
        return default_cords[new], cur, new, True, st
    return default_cords[stored], cur, stored, True, st


def generate() -> str:
    return choice(list(default_cords.keys()))


def set_down(cords: list[list[int]], cur: str, st: list[list[str]]) \
        -> list[list[str]]:
    for k in cords:
        st[k[0]][k[1]] = f"{piece_colors[cur]}&\033[0m"
    return st


def do_nothing(cords: list[list[int]], st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    return cords, st


def menu(st: list[list[str]], menu_type: str, is_new: bool) -> None:
    global left_screen, right_screen, speed_incr, difficulty, score
    if is_new:
        draw_menu(st, menu_type)
    if name == 'nt':
        key: int = ord(getch())
    else:
        key: int = getch()
    if menu_type == "pause" and key == 27:  # "Esc"
        return
    elif key == ord("r"):
        score = 0
        main()
        return
    elif key == ord("q"):
        quit(0)
    elif menu_type == "start":
        if key == ord("1"):
            difficulty = 1
            speed_incr = 75
        elif key == ord("2"):
            difficulty = 2
            speed_incr = 100
        elif key == ord("3"):
            difficulty = 3
            speed_incr = 125
        else:
            menu(st, menu_type, is_new=False)
        main()
        return
    else:
        menu(st, menu_type, is_new=False)


def next_block() -> str:
    global upcoming
    new_block = upcoming.pop(0)
    upcoming.append(generate())
    for i, k in enumerate(upcoming):
        # Clear only the parts containing old upcoming pieces
        right_screen[4 + i * 5] = [*"                    "]
        right_screen[5 + i * 5] = [*"                    "]
        # Add updated upcoming piece to right_screen
        for j in default_cords[k]:
            right_screen[3 + i * 5 + j[0]][(j[1] * 2) - 1] = f"{piece_colors[k]}@\033[0m"
            right_screen[3 + i * 5 + j[0]][j[1] * 2] = f"{piece_colors[k]}@\033[0m"
    return new_block


# -----------------------------------------------------
# BLOCK DATA

default_cords: dict[str, list[list[int]]] = {
    # These values indicate where a piece will generate, piece[[fragment[y][x]]*4]
    "Z": [[1, 3], [1, 4], [2, 4], [2, 5]],
    "S": [[1, 4], [1, 5], [2, 3], [2, 4]],
    "O": [[1, 4], [1, 5], [2, 4], [2, 5]],
    "L": [[1, 5], [2, 3], [2, 4], [2, 5]],
    "T": [[1, 4], [2, 3], [2, 4], [2, 5]],
    "I": [[2, 3], [2, 4], [2, 5], [2, 6]],
    "J": [[1, 3], [2, 3], [2, 4], [2, 5]]
    
}

piece_colors: dict[str, str] = {
    # ANSI Escape Codes corresponding to different colors
    "Z": '\033[91;101m',
    "S": '\033[92;102m',
    "O": '\033[93;103m',
    "L": '\033[94;104m',
    "T": '\033[95;105m',
    "I": '\033[96;106m',
    "J": '\033[38;5;202m\033[48;5;202m'  # This one is longer because there is no orange in the default colors
}

rot_tbl: dict[str, tuple] = {
    # These values indicate how much to move each fragment of the piece when rotating, piece((fragment(y)(x))*4)
    "Z":
        (
            ((0, 2), (1, 1), (0, 0), (1, -1)),
            ((2, 0), (1, -1), (0, 0), (-1, -1)),
            ((0, -2), (-1, -1), (0, 0), (-1, 1)),
            ((-2, 0), (-1, 1), (0, 0), (1, 1))
        ),
    "S":
        (
            ((1, 1), (2, 0), (-1, 1), (0, 0)),
            ((1, -1), (0, -2), (1, 1), (0, 0)),
            ((-1, -1), (-2, 0), (1, -1), (0, 0)),
            ((-1, 1), (0, 2), (-1, -1), (0, 0))
        ),
    # Yes, there is no "O"/Square, because rotating a square would not change the position of the fragments
    "L":
        (
            ((2, 0), (-1, 1), (0, 0), (1, -1)),
            ((0, -2), (1, 1), (0, 0), (-1, -1)),
            ((-2, 0), (1, -1), (0, 0), (-1, 1)),
            ((0, 2), (-1, -1), (0, 0), (1, 1))
        ),
    "T":
        (
            ((1, 1), (-1, 1), (0, 0), (1, -1)),
            ((1, -1), (1, 1), (0, 0), (-1, -1)),
            ((-1, -1), (1, -1), (0, 0), (-1, 1)),
            ((-1, 1), (-1, -1), (0, 0), (1, 1))
        ),
    "I":
        (
            ((-2, 2), (-1, 1), (0, 0), (1, -1)),
            ((2, 2), (1, 1), (0, 0), (-1, -1)),
            ((2, -2), (1, -1), (0, 0), (-1, 1)),
            ((-2, -2), (-1, -1), (0, 0), (1, 1))
        ),
    "J":
        (
            ((0, 2), (-1, 1), (0, 0), (1, -1)),
            ((2, 0), (1, 1), (0, 0), (-1, -1)),
            ((0, -2), (1, -1), (0, 0), (-1, 1)),
            ((-2, 0), (-1, -1), (0, 0), (1, 1))
        )
}

# -----------------------------------------------------
# GAME DATA

upcoming: list[str] = [generate() for _ in range(4)]

difficulty: int = 2
speed_incr: int = 100
score: int = 0 # Max score without bugs: 99_999_999_999_999

left_screen: list[list[str]] = [[*"                    "],
                                [*"                    "],
                                [*"                    "],
                                [*"       SCORE:       "],
                                [*"          0         "],
                                [*"                    "],
                                [*"~~~~~~~~~~~~~~~~~~~~"],
                                [*"                    "],
                                [*"      STORED:       "],
                                [*"                    "],
                                [*"                    "],
                                [*"                    "],
                                [*"                    "],
                                [*"~~~~~~~~~~~~~~~~~~~~"],
                                [*"     CONTROLS:      "],
                                [*" -Up arrow: Rotate  "],
                                [*" -Left/Right arrow: "],
                                [*"  Move Left/Right   "],
                                [*" -Down arrow: Drop  "],
                                [*" -C: Store          "],
                                [*" -Space: Quick Drop "],
                                [*" -Esc: Pause        "], ]
right_screen: list[list[str]] = [[*"                    "],
                                 [*"                    "],
                                 [*"     UPCOMING:      "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"~~~~~~~~~~~~~~~~~~~~"],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"~~~~~~~~~~~~~~~~~~~~"],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"~~~~~~~~~~~~~~~~~~~~"],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "],
                                 [*"                    "], ]


# -----------------------------------------------------
# DRIVER CODE

def main():
    global score, right_screen, left_screen, upcoming
    combo: int = 0
    difficult: bool = False
    state: list[list[str]] = [[" " for _ in range(10)] for _ in range(22)]
    stored: str = ""
    while True:
        sscore = str(score)
        score_len = len(sscore)
        left_offset = 10 - (score_len>2)*(score_len//2)
        right_offset = 20 - (left_offset + score_len) 
        left_screen[4] = [*f'{" " * left_offset}{sscore}{" " * right_offset}']
        c_piece: str = next_block()
        c_cords: list[list[int]] = default_cords[c_piece]
        for i in state[1][3:6]:
            if "&" in i:
                menu(state, "over", is_new=True)
                break
        clock: int = 0
        rot_state: int = 0
        store_lim: bool = False
        c_cords, state = refresh(c_cords, do_nothing(c_cords, state), c_piece, state)
        while True:
            x_cor: list[int] = [i[1] for i in c_cords]
            clock += speed_incr
            if kbhit():  # check if there is keyboard input
                if name == 'nt':
                    keycode: int = ord(getch())  # get keyboard input
                else:
                    keycode: int = getch()
                if keycode == 72 and c_piece != "O":  # Up arrow
                    rotation_success = (c_cords, state != rotate(c_cords, c_piece, rot_state, state))
                    if rotation_success:
                        c_cords, state = refresh(c_cords, rotate(c_cords, c_piece, rot_state, state), c_piece, state)
                        rot_state = (rot_state + 1) % 4
                elif keycode == 75:  # Left arrow
                    if 0 not in x_cor:  # check if coordinate after move would be out of range
                        c_cords, state = refresh(c_cords, move_side(-1, c_cords, state), c_piece, state)
                elif keycode == 77:  # Right arrow
                    if 9 not in x_cor:
                        c_cords, state = refresh(c_cords, move_side(1, c_cords, state), c_piece, state)
                elif keycode == 80:  # Down arrow
                    if not collision_down(c_cords, state):
                        c_cords, state = refresh(c_cords, move_down(c_cords, state, True), c_piece, state)
                    else:
                        state = set_down(c_cords, c_piece, state)
                        state, score, combo, difficult = line_clear(state, score, combo, difficult)
                        break
                elif keycode == ord("c"):
                    c_cords, stored, c_piece, store_lim, state = store(c_cords, stored, c_piece, store_lim, state)
                    rot_state = 0
                    refresh(c_cords, do_nothing(c_cords, state), c_piece, state)
                elif keycode == 27:  # "Esc"
                    menu(state, "pause", is_new=True)
                    c_cords, state = refresh(c_cords, do_nothing(c_cords, state), c_piece, state)
                elif keycode == ord(" "):
                    c_cords, state = refresh(c_cords, drop(c_cords, state, True), c_piece, state)
                    state = set_down(c_cords, c_piece, state)
                    state, score, combo, difficult = line_clear(state, score, combo, difficult)
                    break
            else:
                sleep(0.01)
                if clock >= 10000:
                    if not collision_down(c_cords, state):
                        clock = 0
                        c_cords, state = refresh(c_cords, move_down(c_cords, state, False), c_piece, state)
                    else:
                        state = set_down(c_cords, c_piece, state)
                        state, score, combo, difficult = line_clear(state, score, combo, difficult)
                        break


if __name__ == "__main__":
    menu([[" " for _ in range(10)] for _ in range(22)], "start", True)
