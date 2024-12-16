from os import name, system
from time import sleep
from random import choice
from re import search

if name == 'nt':  # windows
    from msvcrt import getch, kbhit
elif name == 'unix':
    import curses as cs

# -----------------------------------------------------
# CHECKS

def collision_down(coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if k[0] == 21 or search(r".+#.+", st[k[0] + 1][k[1]]):
            return True
    return False


def collision_side(val: int, coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if search(r".+#.+", st[k[0]][k[1] + val]):
            return True
    return False


# -----------------------------------------------------
# PRINT

def clear() -> None:
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def draw(st: list[list[str]]) -> None:
    clear()
    print("_" * 24)
    for i in range(2, 22):
        print("||", end="")
        for j in range(10):
            print(st[i][j] * 2, end="")
        print("||")
    print("~"* 24)


def refresh(coordinates: list[list[int]], func: tuple[list[list[int]], list[list[str]]], cur: str, st: list[list[str]])\
        -> tuple[list[list[int]], list[list[str]]]:
    preview = "\033[38;5;244m\033[48;5;244m"
    for k in coordinates:
        st[k[0]][k[1]] = " "  # clear previous coordinates
    coordinates, st = func
    preview_coordinates, st = drop(coordinates, st)
    for k in preview_coordinates:
        st[k[0]][k[1]] = f"{preview}$\033[0m"  # draw preview
    for k in coordinates:
        st[k[0]][k[1]] = f"{piece_colors[cur]}@\033[0m"  # draw new piece
    draw(st)
    if preview_coordinates != coordinates:
        for k in preview_coordinates:
            st[k[0]][k[1]] = " "
    return coordinates, st


def line_clear(st: list[list[str]]) -> list[list[str]]:
    cleared_lines = []
    for k in range(len(st)):
        if search(".+#.+", st[k][0]):
            full = True
            for p in range(1, len(st[k])):
                if not search(".+#.+", st[k][p]):
                    full = False
                    break
            if full:
                for q in range(len(st[k])):
                    st[k][q] = " "
                cleared_lines.append(k)
    n = len(cleared_lines)
    if n > 0:
        return [[" " for _ in range(10)] for _ in range(n)] + st[:cleared_lines[0]] + st[cleared_lines[-1] + 1:]
    return st


# -----------------------------------------------------
# MOVEMENT

def rotate(coordinates: list[list[int]], cur: str, rot: int, st: list[list[str]])\
        -> tuple[list[list[int]], list[list[str]]]:
    old_coordinates = coordinates
    x_coordinates = [i[1] for i in coordinates]
    if cur == "|":
        if 0 in x_coordinates:
            if 1 in x_coordinates:
                coordinates = [[k[0], k[1] + 1] for k in coordinates]
            else:
                coordinates = [[k[0], k[1] + 2] for k in coordinates]
        if 9 in x_coordinates:
            if 8 in x_coordinates:
                coordinates = [[k[0], k[1] - 1] for k in coordinates]
            else:
                coordinates = [[k[0], k[1] - 2] for k in coordinates]
    else:
        if 0 in x_coordinates:  # prevent rotating into left wall
            coordinates = [[k[0], k[1] + 1] for k in coordinates]
        if 9 in x_coordinates:  # prevent rotating into right wall
            coordinates = [[k[0], k[1] - 1] for k in coordinates]
    new_coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0],
                        coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(len(coordinates))]
    for k in new_coordinates:
        if k[0] > 21 or k[1] > 9 or search(r".+#.+", st[k[0]][k[1]]):
            return old_coordinates, st
    return new_coordinates, st


def move_side(val: int, coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    if not collision_side(val, coordinates, st):
        coordinates = [[k[0], k[1] + val] for k in coordinates]
    return coordinates, st


def move_down(coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    return [[k[0] + 1, k[1]] for k in coordinates], st


def drop(coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    while not collision_down(coordinates, st):
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    return coordinates, st


# -----------------------------------------------------
# OTHER

def store(coordinates: list[list[int]], stored: str, cur: str, lim: bool, st: list[list[str]]) \
        -> tuple[list[list[int]], str, str, bool, list[list[str]]]:
    if lim:
        return coordinates, stored, cur, lim, st
    for k in coordinates:
        st[k[0]][k[1]] = " "
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


def pause_menu():
    clear()
    print("||      Game Paused       ||")
    print("|| Press Esc To Continue  ||")
    print("|| Press R To Reset       ||")
    print("|| Press Q To Quit        ||")
    key = ord(getch())
    if key == 27: # "Esc"
        return
    elif key == 114:  # "r"
        main()
        return
    elif key == 113:  #"q"
        quit(0)
    else:
        pause_menu()
# -----------------------------------------------------
# BLOCK DATA

default_coordinates: dict[str, list[list[int]]] = {
    "Z": [[1, 3], [1, 4], [2, 4], [2, 5]],
    "Z_reverse": [[1, 4], [1, 5], [2, 3], [2, 4]],
    "L": [[1, 5], [2, 3], [2, 4], [2, 5]],
    "L_reverse": [[1, 3], [2, 3], [2, 4], [2, 5]],
    "Square": [[1, 4], [1, 5], [2, 4], [2, 5]],
    "T": [[1, 5], [2, 4], [2, 5], [2, 6]],
    "|": [[2, 3], [2, 4], [2, 5], [2, 6]]
}

piece_colors: dict[str, str] = {
    "Z": '\033[91;101m',
    "Z_reverse": '\033[92;102m',
    "L": '\033[94;104m',
    "L_reverse": '\033[38;5;202m\033[48;5;202m',
    "Square": '\033[93;103m',
    "T": '\033[95;105m',
    "|": '\033[96;106m'
}

rotation_table: dict[str, tuple] = {
    "Z":
        (
            ((0, 2), (1, 1), (0, 0), (1, -1)),
            ((2, 0), (1, -1), (0, 0), (-1, -1)),
            ((0, -2), (-1, -1), (0, 0), (-1, 1)),
            ((-2, 0), (-1, 1), (0, 0), (1, 1))
        ),
    "Z_reverse":
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
    "L_reverse":
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
    "|":
        (
            ((-2, 2), (-1, 1), (0, 0), (1, -1)),
            ((2, 2), (1, 1), (0, 0), (-1, -1)),
            ((2, -2), (1, -1), (0, 0), (-1, 1)),
            ((-2, -2), (-1, -1), (0, 0), (1, 1))
        ),
}


# -----------------------------------------------------
# DRIVER CODE

def main():
    game_state: list[list[str]] = [[" " for _ in range(10)] for _ in range(22)]
    stored: str = ""
    while True:
        current: str = generate()
        for i in game_state[1][3:6]:
            if search(r".+#.+", i):
                exit(0)
            else:
                cur_coords: list[list[int]] = default_coordinates[current]
        clock: float = 0
        rotation_state: int = 0
        store_limit: bool = False
        cur_coords, game_state = refresh(cur_coords, do_nothing(cur_coords, game_state), current, game_state)
        while True:
            x_coords: list[int] = [i[1] for i in cur_coords]
            clock += 0.01
            if kbhit():  # check if there is keyboard input
                keycode: int = ord(getch())  # get keyboard input
                if keycode == 72 and current != "Square":  # Up arrow
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
                        cur_coords, game_state = refresh(cur_coords, move_down(cur_coords, game_state), current,
                                                         game_state)
                    else:
                        game_state = set_down(cur_coords, current, game_state)
                        game_state = line_clear(game_state)
                        break
                elif keycode == 99:  # "c"
                    cur_coords, stored, current, store_limit, game_state = store(cur_coords, stored, current,
                                                                                 store_limit, game_state)
                    rotation_state = 0
                    refresh(cur_coords, do_nothing(cur_coords, game_state), current, game_state)
                elif keycode == 27:  # "Esc"
                    pause_menu()
                elif keycode == 32:  # Space
                    cur_coords, game_state = refresh(cur_coords, drop(cur_coords, game_state), current, game_state)
                    game_state = set_down(cur_coords, current, game_state)
                    game_state = line_clear(game_state)
                    break
            else:
                sleep(0.01)
                if int(clock) == 1:
                    if not collision_down(cur_coords, game_state):
                        clock = 0
                        cur_coords, game_state = refresh(cur_coords, move_down(cur_coords, game_state), current,
                                                         game_state)
                    else:
                        game_state = set_down(cur_coords, current, game_state)
                        game_state = line_clear(game_state)
                        break


if __name__ == "__main__":
    main()
