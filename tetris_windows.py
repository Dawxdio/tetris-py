from os import name, system
from time import sleep
from random import choice
from msvcrt import getch, kbhit


# -----------------------------------------------------
# CHECKS

def collision_down(coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if k[0] == 21 or "#" in st[k[0] + 1][k[1]]:
            return True
    return False


def collision_side(val: int, coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if "#" in st[k[0]][k[1] + val]:
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
        for j in range(20):
            print(left_screen[i][j], end="")

        print("||", end="")
        for j in range(10):
            print(st[i][j] * 2, end="")
        print("||", end="")
        for j in range(20):
            print(right_screen[i][j], end="")
        print("||")
    print("||", end="")
    print("~" * 20, end="||")
    print("~" * 20, end="||")
    print("~" * 20, end="||\n")


def refresh(coordinates: list[list[int]], func: tuple[list[list[int]], list[list[str]]], cur: str, st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    preview = "\033[38;5;244m\033[48;5;244m"

    for k in coordinates:
        st[k[0]][k[1]] = " "  # clear previous coordinates
    coordinates, st = func
    preview_coordinates, st = drop(coordinates, st, False)
    for k in preview_coordinates:
        st[k[0]][k[1]] = f"{preview}$\033[0m"  # draw preview
    for k in coordinates:
        st[k[0]][k[1]] = f"{piece_colors[cur]}@\033[0m"  # draw new piece
    draw(st)

    if preview_coordinates != coordinates:
        for k in preview_coordinates:
            st[k[0]][k[1]] = " "
    return coordinates, st


def line_clear(st: list[list[str]], sco: int, com: int, dif: bool) -> tuple[list[list[str]], int, int, bool]:
    global speed_incr, difficulty
    cleared_lines = []
    points = [100, 300, 500, 800]
    for k in range(len(st)):
        if "#" in st[k][0]:
            full = True
            for p in range(1, len(st[k])):
                if "#" not in st[k][p]:
                    full = False
                    break
            if full:
                for q in range(len(st[k])):
                    st[k][q] = " "
                cleared_lines.append(k)
    n = len(cleared_lines)
    speed_incr += n * difficulty
    if n > 0:
        act_sco = points[n - 1] + (50 * com)
        if dif:
            act_sco *= 1.5
        if n == 4:
            dif = True
        else:
            dif = False
        sco += act_sco
        return [[" " for _ in range(10)] for _ in range(n)] + st[:cleared_lines[0]] + st[cleared_lines[-1] + 1:], sco, com + 1, dif
    return st, sco, 0, dif


# -----------------------------------------------------
# MOVEMENT

def rotate(coordinates: list[list[int]], cur: str, rot: int, st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    old_coordinates: list[list[int]] = coordinates
    x_coordinates: list[int] = [i[1] for i in coordinates]
    if cur == "I":
        xcord_I: int = x_coordinates[0]
        if xcord_I == x_coordinates[3]:
            if rot == 3:
                if xcord_I == 0:
                    coordinates = [[k[0], k[1] + 2] for k in coordinates]
                elif xcord_I == 1:
                    coordinates = [[k[0], k[1] + 1] for k in coordinates]
                elif xcord_I == 9:
                    coordinates = [[k[0], k[1] - 1] for k in coordinates]
            if rot == 1:
                if xcord_I == 9:
                    coordinates = [[k[0], k[1] - 2] for k in coordinates]
                elif xcord_I == 8:
                    coordinates = [[k[0], k[1] - 1] for k in coordinates]
                elif xcord_I == 0:
                    coordinates = [[k[0], k[1] + 1] for k in coordinates]
    else:
        if 0 in x_coordinates:  # prevent rotating into left wall
            coordinates = [[k[0], k[1] + 1] for k in coordinates]
        if 9 in x_coordinates:  # prevent rotating into right wall
            coordinates = [[k[0], k[1] - 1] for k in coordinates]
    new_coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0],
                        coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(len(coordinates))]
    for k in new_coordinates:
        if k[0] > 21 or k[1] > 9 or "#" in st[k[0]][k[1]]:
            return old_coordinates, st
    return new_coordinates, st


def move_side(val: int, coordinates: list[list[int]], st: list[list[str]]) \
        -> tuple[list[list[int]], list[list[str]]]:
    if not collision_side(val, coordinates, st):
        coordinates = [[k[0], k[1] + val] for k in coordinates]
    return coordinates, st


def move_down(coordinates: list[list[int]], st: list[list[str]], scored: bool) \
        -> tuple[list[list[int]], list[list[str]]]:
    global game_score
    if scored:
        game_score += 1
    return [[k[0] + 1, k[1]] for k in coordinates], st


def drop(coordinates: list[list[int]], st: list[list[str]], scored: bool) \
        -> tuple[list[list[int]], list[list[str]]]:
    global game_score
    while not collision_down(coordinates, st):
        if scored:
            game_score += 2
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    return coordinates, st


# -----------------------------------------------------
# OTHER

def store(coordinates: list[list[int]], stored: str, cur: str, lim: bool, st: list[list[str]]) \
        -> tuple[list[list[int]], str, str, bool, list[list[str]]]:
    global right_screen
    if lim:
        return coordinates, stored, cur, lim, st
    for k in coordinates:
        st[k[0]][k[1]] = " "
    left_screen[10] = [*"                    "]
    left_screen[11] = [*"                    "]
    for k in default_coordinates[cur]:
        left_screen[9 + k[0]][(k[1] * 2) - 1] = f"{piece_colors[cur]}@\033[0m"
        left_screen[9 + k[0]][k[1] * 2] = f"{piece_colors[cur]}@\033[0m"
    if stored == "":
        new = generate()
        return default_coordinates[new], cur, new, True, st
    return default_coordinates[stored], cur, stored, True, st


def generate() -> str:
    return choice(list(default_coordinates.keys()))


def set_down(coordinates: list, cur: str, st: list) -> list:
    for k in coordinates:
        st[k[0]][k[1]] = f"{piece_colors[cur]}#\033[0m"
    return st


def do_nothing(coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    return coordinates, st


def menu(st: list[list[str]], menu_type: str, sco: int, is_new: bool) -> None:
    global left_screen, right_screen, speed_incr, difficulty
    if is_new:
        clear()
        print("~" * 24)
        for k in range(2, 9):
            print("||", end="")
            for n in range(10):
                print(st[k][n] * 2, end="")
            print("||")
        print("#" * 24)
        if menu_type == "pause":
            print("#     Game Paused      #")
            print("# Continue:  Press Esc #")
            print("# New Game:  Press R   #")
            print("# Quit:      Press Q   #")
        elif menu_type == "over":
            print("#      Game Over!      #")
            print(f"# Score: {sco}{" " * (14 - len(str(sco)))}#")
            print("# New Game:  Press R   #")
            print("# Quit:      Press Q   #")
        elif menu_type == "start":
            print("# Choose a difficulty: #")
            print("# Easy: Press 1        #")
            print("# Medium: Press 2      #")
            print("# Hard: Press 3        #")
        print("#" * 24)
        for k in range(15, 22):
            print("||", end="")
            for n in range(10):
                print(st[k][n] * 2, end="")
            print("||")
        print("~" * 24)
    key = ord(getch())
    if key == 27 and menu_type == "pause":  # "Esc"
        return
    elif key == 114:  # "r"
        main()
        return
    elif key == 113:  # "q"
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
            menu(st, menu_type, sco, is_new=False)
        main()
        return
    else:
        menu(st, menu_type, sco, is_new=False)


def next_block() -> str:
    global upcoming
    new_block = upcoming.pop(0)
    upcoming.append(generate())
    for i, k in enumerate(upcoming):
        right_screen[4 + i * 5] = [*"                    "]
        right_screen[5 + i * 5] = [*"                    "]
        for j in default_coordinates[k]:
            right_screen[3 + i * 5 + j[0]][(j[1] * 2) - 1] = f"{piece_colors[k]}@\033[0m"
            right_screen[3 + i * 5 + j[0]][j[1] * 2] = f"{piece_colors[k]}@\033[0m"
    return new_block


# -----------------------------------------------------
# BLOCK DATA

default_coordinates: dict[str, list[list[int]]] = {
    "Z": [[1, 3], [1, 4], [2, 4], [2, 5]],
    "S": [[1, 4], [1, 5], [2, 3], [2, 4]],
    "L": [[1, 5], [2, 3], [2, 4], [2, 5]],
    "J": [[1, 3], [2, 3], [2, 4], [2, 5]],
    "O": [[1, 4], [1, 5], [2, 4], [2, 5]],
    "T": [[1, 5], [2, 4], [2, 5], [2, 6]],
    "I": [[2, 3], [2, 4], [2, 5], [2, 6]]
}

piece_colors: dict[str, str] = {
    "Z": '\033[91;101m',
    "S": '\033[92;102m',
    "L": '\033[94;104m',
    "J": '\033[38;5;202m\033[48;5;202m',
    "O": '\033[93;103m',
    "T": '\033[95;105m',
    "I": '\033[96;106m'
}

rotation_table: dict[str, tuple] = {
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
    "L":
        (
            ((2, 0), (-1, 1), (0, 0), (1, -1)),
            ((0, -2), (1, 1), (0, 0), (-1, -1)),
            ((-2, 0), (1, -1), (0, 0), (-1, 1)),
            ((0, 2), (-1, -1), (0, 0), (1, 1))
        ),
    "J":
        (
            ((0, 2), (-1, 1), (0, 0), (1, -1)),
            ((2, 0), (1, 1), (0, 0), (-1, -1)),
            ((0, -2), (1, -1), (0, 0), (-1, 1)),
            ((-2, 0), (-1, -1), (0, 0), (1, 1))
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
}

# -----------------------------------------------------
# GAME DATA

upcoming: list[str] = [generate() for _ in range(4)]

difficulty: int = 2
speed_incr: int = 100
game_score: int = 0

left_screen: list[list[str]] = [[*"                    "],
                                [*"                    "],
                                [*"                    "],
                                [*"       SCORE:       "],
                                [*"         0          "],
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
    global game_score, right_screen, left_screen, upcoming
    combo: int = 0
    difficult: bool = False
    game_state: list[list[str]] = [[" " for _ in range(10)] for _ in range(22)]
    stored: str = ""
    while True:
        left_screen[4] = [
            *f"{" " * (9 - len(str(game_score)) // 2)}{str(game_score)}{" " * (12 - len(str(game_score)) // 2)}"]
        current: str = next_block()
        cur_coords: list[list[int]] = default_coordinates[current]
        for i in game_state[1][3:6]:
            if "#" in i:
                menu(game_state, "over", game_score, is_new=True)
        clock: int = 0
        rotation_state: int = 0
        store_limit: bool = False
        cur_coords, game_state = refresh(cur_coords, do_nothing(cur_coords, game_state), current, game_state)
        while True:
            x_coords: list[int] = [i[1] for i in cur_coords]
            clock += speed_incr
            if kbhit():  # check if there is keyboard input
                keycode: int = ord(getch())  # get keyboard input
                if keycode == 72 and current != "O":  # Up arrow
                    rotation_success = (cur_coords, game_state != rotate(cur_coords, current, rotation_state, game_state))
                    if rotation_success:
                        cur_coords, game_state = refresh(cur_coords,
                                                         rotate(cur_coords, current, rotation_state, game_state),
                                                         current, game_state)
                        rotation_state = (rotation_state + 1) % 4
                elif keycode == 75:  # Left arrow
                    if 0 not in x_coords:  # check if coordinate after move would be out of range
                        cur_coords, game_state = refresh(cur_coords, move_side(-1, cur_coords, game_state), current,
                                                         game_state)
                elif keycode == 77:  # Right arrow
                    if 9 not in x_coords:
                        cur_coords, game_state = refresh(cur_coords, move_side(1, cur_coords, game_state), current,
                                                         game_state)
                elif keycode == 80:  # Down arrow
                    if not collision_down(cur_coords, game_state):
                        cur_coords, game_state = refresh(cur_coords, move_down(cur_coords, game_state, True), current,
                                                         game_state)
                    else:
                        game_state = set_down(cur_coords, current, game_state)
                        game_state, game_score, combo, difficult = line_clear(game_state, game_score, combo, difficult)
                        break
                elif keycode == 99:  # "c"
                    cur_coords, stored, current, store_limit, game_state = store(cur_coords, stored, current,
                                                                                 store_limit, game_state)
                    rotation_state = 0
                    refresh(cur_coords, do_nothing(cur_coords, game_state), current, game_state)
                elif keycode == 27:  # "Esc"
                    menu(game_state, "pause", game_score, is_new=True)
                    cur_coords, game_state = refresh(cur_coords, do_nothing(cur_coords, game_state), current,
                                                     game_state)
                elif keycode == 32:  # Space
                    cur_coords, game_state = refresh(cur_coords, drop(cur_coords, game_state, True), current,
                                                     game_state)
                    game_state = set_down(cur_coords, current, game_state)
                    game_state, game_score, combo, difficult = line_clear(game_state, game_score, combo, difficult)
                    break
            else:
                sleep(0.01)
                if clock >= 10000:
                    if not collision_down(cur_coords, game_state):
                        clock = 0
                        cur_coords, game_state = refresh(cur_coords, move_down(cur_coords, game_state, False), current,
                                                         game_state)
                    else:
                        game_state = set_down(cur_coords, current, game_state)
                        game_state, game_score, combo, difficult = line_clear(game_state, game_score, combo, difficult)
                        break


if __name__ == "__main__":
    menu([[" " for _ in range(10)] for _ in range(22)], "start", 0, True)
