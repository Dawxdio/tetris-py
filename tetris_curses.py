from os import name, system
from time import sleep
from random import choice
import curses as cs

if name == 'nt':  # Windows
    from msvcrt import getch
else:  # Linux, source: https://gist.github.com/michelbl/efda48b19d3e587685e3441a74457024
    from sys import stdin
    from termios import tcgetattr, tcsetattr, ICANON, ECHO, TCSAFLUSH
    from tty import setcbreak


    def getch():
        old_settings = tcgetattr(stdin)
        new_settings = old_settings
        new_settings[3] = (new_settings[3] & ~ICANON & ~ECHO)  # Turn off key echoing
        tcsetattr(stdin.fileno(), TCSAFLUSH, new_settings)  
        setcbreak(stdin.fileno())
        try:
            c = stdin.read(1)
            if c == '\x1b':
                c2 = stdin.read(2)
                if c2 == "[A":  # Up arrow
                    return 72
                elif c2 == "[B":  # Down arrow
                    return 80
                elif c2 == "[C":  # Right arrow
                    return 77
                elif c2 == "[D":  # Left arrow
                    return 75
            else:
                return ord(c)
        finally:
            tcsetattr(stdin.fileno(), TCSAFLUSH, old_settings)


# -----------------------------------------------------
# CHECKS

def collision_down(cords: list, st: list) -> bool:
    for k in cords:
        if k[0] == 21 or "&" in st[k[0] + 1][k[1]]:
            return True
    return False


def collision_side(val: int, cords: list, st: list) -> bool:
    for k in cords:
        if "&" in st[k[0]][k[1] + val]:
            return True
    return False


# -----------------------------------------------------
# PRINT


def draw(st: list) -> None:  # st == middle screen
    global right_screen, left_screen, speed_incr
    print(y_border, end="")
    print(x_border * 20, end=y_border)
    print(x_border * 20, end=y_border)
    print(x_border * 20, end=f"{y_border}\n")
    for i in range(2, 22):
        print(y_border, end="")
        [print(j, end="") for j in left_screen[i]]
        print(y_border, end="")
        [print(j * 2, end="") for j in st[i]]
        print(y_border, end="")
        [print(j, end="") for j in right_screen[i]]
        print(y_border)
    print(y_border, end="")
    print(x_border * 20, end=y_border)
    print(x_border * 20, end=y_border)
    print(x_border * 20, end=f"{y_border}\n")


def update(cords: list, func: tuple, cur: str, st: list, mainscr) -> tuple:
    preview = "\033[38;5;244m\033[48;5;244m"
    for k in cords:
        mainscr.addstr(k[0], k[1]*2, " ")
        mainscr.addstr(k[0], k[1]*2+1, " ")
        st[k[0]][k[1]] = " "  # clear previous cords
    cords, st = func
    preview_cords, st = drop(cords, st, False)
    for k in preview_cords:
        mainscr.addstr(k[0], k[1]*2, f"{preview}$\033[0m")
        mainscr.addstr(k[0], k[1]*2+1, f"{preview}$\033[0m")
        st[k[0]][k[1]] = f"{preview}$\033[0m"  # draw preview
    for k in cords:
        mainscr.addstr(k[0], k[1]*2, f"{piece_colors[cur]}@\033[0m")
        mainscr.addstr(k[0], k[1]*2+1, f"{piece_colors[cur]}@\033[0m")
        st[k[0]][k[1]] = f"{piece_colors[cur]}@\033[0m"  # draw new piece
    if preview_cords != cords:
        for k in preview_cords:
            mainscr.addstr(k[0], k[1]*2, " ")
            mainscr.addstr(k[0], k[1]*2+1, " ")
            st[k[0]][k[1]] = " "
    mainscr.refresh()
    return cords, st



def line_clear(st: list, sco: int, com: int, dif: bool) -> tuple:
    global speed_incr, difficulty
    clr_lns: list = []
    points: tuple = (100, 300, 500, 800)
    for k in range(len(st)):
        if "&" in st[k][0]:
            full: bool = True
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
        st_copy = [[" " for j in range(10)] for i in range(n)]  # Add new empty lines on top of after-clear state
        st_copy += st[:clr_lns[0]]  # Copy existing lines from existing state, up to the first cleared line-1
        for k in range(n-1):
            st_copy += st[clr_lns[k]+1:clr_lns[k+1]]  # Copy all lines between cleared lines
        st_copy += st[clr_lns[-1]+1:]  # Copy existing lines from existing state, down from last cleared line+1
        st = st_copy  # Replace state with state after clear
        return st, sco, com + 1, dif
    return st, sco, 0, dif


# -----------------------------------------------------
# MOVEMENT

def rotate(cords: list, cur: str, rot: int, st: list) -> tuple:
    old_cords: list = cords
    x_cords: list = [i[1] for i in cords]
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


def move_side(val: int, cords: list, st: list) -> tuple:
    if not collision_side(val, cords, st):
        cords = [[k[0], k[1] + val] for k in cords]
    return cords, st


def move_down(cords: list, st: list, scored: bool) -> tuple:
    global score
    if scored:
        score += 1
    return [[k[0] + 1, k[1]] for k in cords], st


def drop(cords: list, st: list, scored: bool) -> tuple:
    global score
    while not collision_down(cords, st):
        if scored:
            score += 2
        cords = [[k[0] + 1, k[1]] for k in cords]
    return cords, st


# -----------------------------------------------------
# MENU


menu_content: dict = {
    "start": ("&" * 24,
              "! Choose a difficulty: !",
              "! Easy:   Press 1      !",
              "! Medium: Press 2      !",
              "! Hard:   Press 3      !",
              "&" * 24),
    "pause": ("&" * 24,
              "!     Game Paused      !",
              "! Continue:  Press P   !",
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


def menu(st: list, mainscr, menu_type: str, is_new: bool) -> None:
    global left_screen, right_screen, score, upcoming
    if is_new:
        if menu_type == "start":
            set_default_values()
        draw_menu(st, menu_type)
    if name == 'nt':
        key: int = ord(getch())
    else:
        key: int = getch()
    if menu_type == "pause" and key == ord("p"):
        return
    elif key == ord("r"):
        menu([[" " for _ in range(10)] for _ in range(22)], "start", True)
        return
    elif key == ord("q"):
        quit(0)
    elif menu_type == "start":
        diff: int
        spd_inc: int
        if key == ord("1"):
            diff = 1
            spd_inc = 75
        elif key == ord("2"):
            diff = 2
            spd_inc = 100
        elif key == ord("3"):
            diff = 3
            spd_inc = 125
        else:
            menu(st, menu_type, is_new=False)
        set_default_values(diff, spd_inc)
        main(mainscr)
        return
    else:
        menu(st, menu_type, is_new=False)


def draw_menu(st: list, menu_type: str) -> None:
    global left_screen, right_screen, menu_content
    cs.clear()
    print(y_border, end="")
    [print(x_border * 20, end=y_border) for _ in range(3)]
    print()
    for i in range(2, 9):
        print(y_border, end="")
        [print(j, end="") for j in left_screen[i]]
        print(y_border, end="")
        [print(j * 2, end="") for j in st[i]]
        print(y_border, end="")
        [print(j, end="") for j in right_screen[i]]
        print(y_border)
    for i in range(9, 15):
        print(y_border, end="")
        [print(j, end="") for j in left_screen[i]]
        if menu_type == "over" and i == 11:
            score_len = len(str(score))
            left_offset = (5 - max(0, score_len - 9))
            right_offset = 20 - (left_offset + score_len + 5)
            print(f'! Score:{" " * left_offset}{score}{" " * right_offset}!', end="")
        else:
            print(menu_content[menu_type][i - 9], end="")
        [print(j, end="") for j in right_screen[i]]
        print(y_border)
    for i in range(15, 22):
        print(y_border, end="")
        [print(j, end="") for j in left_screen[i]]
        print(y_border, end="")
        [print(j * 2, end="") for j in st[i]]
        print(y_border, end="")
        [print(j, end="") for j in right_screen[i]]
        print(y_border)
    print(y_border, end="")
    [print(x_border * 20, end=y_border) for _ in range(3)]
    print()


# -----------------------------------------------------
# OTHER

def store(cords: list, stored: str, cur: str, lim: bool, st: list) -> tuple:
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
        left_screen[9 + k[0]][k[1] * 2 + 1] = f"{piece_colors[cur]}@\033[0m"
    if stored == "":
        new = generate()
        return default_cords[new], cur, new, True, st
    return default_cords[stored], cur, stored, True, st


def generate() -> str:
    return choice(list(default_cords.keys()))


def set_down(cords: list, cur: str, st: list, mainscr) -> list:
    for k in cords:
        st[k[0]][k[1]] = f"{piece_colors[cur]}&\033[0m"
    return st


def do_nothing(cords: list, st: list) -> tuple:
    return cords, st


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


def set_default_values(diff=None, spd_inc=None) -> None:
    global speed_incr, difficulty, score, stored, upcoming, left_screen, right_screen
    speed_incr = spd_inc
    difficulty = diff
    score = 0
    stored = ""
    upcoming = [generate() for _ in range(4)]
    left_screen_cont = [[*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"       SCORE:       "],
                    [*"          0         "],
                    [*"                    "],
                    [*f"{x_border*20}"],
                    [*"                    "],
                    [*"      STORED:       "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*f"{x_border*20}"],
                    [*"     CONTROLS:      "],
                    [*" -Up arrow: Rotate  "],
                    [*" -Left/Right arrow: "],
                    [*"  Move Left/Right   "],
                    [*" -Down arrow: Drop  "],
                    [*" -C: Store          "],
                    [*" -Space: Quick Drop "],
                    [*" -P: Pause          "], ]
    for y, i  in enumerate(left_screen_cont):
        for x, j in i:
            left_screen.addstr(y,x,j)
    right_screen_cont = [[*"                    "],
                    [*"                    "],
                    [*"     UPCOMING:      "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*f"{x_border*20}"],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*f"{x_border*20}"],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*f"{x_border*20}"],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],
                    [*"                    "],]
    for y, i  in enumerate(right_screen_cont):
        for x, j in i:
            right_screen.addstr(y,x,j)


# -----------------------------------------------------
# BLOCK DATA

default_cords: dict = {
    # These values indicate where a piece will generate, piece[[fragment[y][x]]*4]
    "Z": [[1, 3], [1, 4], [2, 4], [2, 5]],
    "S": [[1, 4], [1, 5], [2, 3], [2, 4]],
    "O": [[1, 4], [1, 5], [2, 4], [2, 5]],
    "L": [[1, 5], [2, 3], [2, 4], [2, 5]],
    "T": [[1, 4], [2, 3], [2, 4], [2, 5]],
    "I": [[2, 3], [2, 4], [2, 5], [2, 6]],
    "J": [[1, 3], [2, 3], [2, 4], [2, 5]]

}

piece_colors: dict = {
    # ANSI Escape Codes corresponding to different colors
    "Z": '\033[91;101m',
    "S": '\033[92;102m',
    "O": '\033[93;103m',
    "L": '\033[94;104m',
    "T": '\033[95;105m',
    "I": '\033[96;106m',
    "J": '\033[38;5;202m\033[48;5;202m'  # This one is longer because there is no orange in the default colors
}

rot_tbl: dict = {
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

upcoming: list
difficulty: int
speed_incr: int
score: int  # Max score without bugs: 99_999_999_999_999
stored: str
left_screen = cs.newwin(22,20,0,0)
right_screen = cs.newwin(22,20,0,40)
x_border: str = "~"
y_border: str = "||"

# -----------------------------------------------------
# DRIVER CODE

def main(mainscr):
    global score, right_screen, left_screen, upcoming, stored
    cs.curs_set(0)
    mainscr = cs.newwin(22,20,0,20)
    mainscr.border("|","|","~","~")
    mainscr.nodelay(True)
    combo: int = 0
    difficult: bool = False
    state: list = [[" " for _ in range(10)] for _ in range(22)]
    while True:
        sscore = str(score)
        score_len = len(sscore)
        left_offset = 10 - (score_len > 2) * (score_len // 2)
        right_offset = 20 - (left_offset + score_len)
        left_screen[4] = [*f'{" " * left_offset}{sscore}{" " * right_offset}']
        c_piece: str = next_block()
        c_cords: list = default_cords[c_piece]
        for i in state[2][3:6]:
            if "&" in i:
                menu(state, "over", is_new=True)
                break
        clock: int = 0
        rot_state: int = 0
        store_lim: bool = False
        c_cords, state = update(c_cords, do_nothing(c_cords, state), c_piece, state, mainscr)
        while True:
            x_cor: list = [i[1] for i in c_cords]
            clock += speed_incr
            sleep(0.01)
            if name == 'nt':
                keycode: int = ord(getch())
            else:
                keycode: int = getch()
            if keycode == 72 and c_piece != "O":  # Up arrow
                rotation_success = (c_cords, state != rotate(c_cords, c_piece, rot_state, state))
                if rotation_success:
                    c_cords, state = update(c_cords, rotate(c_cords, c_piece, rot_state, state), c_piece, state, mainscr)
                    rot_state = (rot_state + 1) % 4
            elif keycode == 75:  # Left arrow
                if 0 not in x_cor:  # check if coordinate after move would be out of range
                    c_cords, state = update(c_cords, move_side(-1, c_cords, state), c_piece, state, mainscr)
            elif keycode == 77:  # Right arrow
                if 9 not in x_cor:
                    c_cords, state = update(c_cords, move_side(1, c_cords, state), c_piece, state, mainscr)
            elif keycode == 80:  # Down arrow
                if not collision_down(c_cords, state):
                    c_cords, state = update(c_cords, move_down(c_cords, state, True), c_piece, state, mainscr)
                else:
                    state = set_down(c_cords, c_piece, state, mainscr)
                    state, score, combo, difficult = line_clear(state, score, combo, difficult)
                    break
            elif keycode == ord("c"):
                c_cords, stored, c_piece, store_lim, state = store(c_cords, stored, c_piece, store_lim, state)
                rot_state = 0
                update(c_cords, do_nothing(c_cords, state), c_piece, state, mainscr)
            elif keycode == ord("p"):
                menu(state, "pause", is_new=True)
                c_cords, state = update(c_cords, do_nothing(c_cords, state), c_piece, state, mainscr)
            elif keycode == ord(" "):
                c_cords, state = update(c_cords, drop(c_cords, state, True), c_piece, state, mainscr)
                state = set_down(c_cords, c_piece, state, mainscr)
                state, score, combo, difficult = line_clear(state, score, combo, difficult)
                break
            elif keycode == ord("q"):
                exit(0)
            elif keycode == ord("r"):
                set_default_values(difficulty, speed_incr)
                main(mainscr)
            if clock >= 10000:
                if not collision_down(c_cords, state):
                    clock = 0
                    c_cords, state = update(c_cords, move_down(c_cords, state, False), c_piece, state, mainscr)
                else:
                    state = set_down(c_cords, c_piece, state, mainscr)
                    state, score, combo, difficult = line_clear(state, score, combo, difficult)
                    break


if __name__ == "__main__":
    cs.wrapper(menu([[" " for _ in range(10)] for _ in range(22)], "start", True))
