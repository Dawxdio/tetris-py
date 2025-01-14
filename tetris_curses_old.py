from os import name, system
from time import sleep
from random import choice
import curses as cs

game_score = 0
# -----------------------------------------------------
# CHECKS

def collision_down(coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if k[0] == 20 or "#" in st[k[0] + 1][k[1]]:
            return True
    return False


def collision_side(val: int, coordinates: list[list[int]], st: list[list[str]]) -> bool:
    for k in coordinates:
        if val == -1 and k[1] == 1:
            return True
        elif val == 1 and k[1] == 18:
            return True
        #elif "#" in st[k[0]][k[1] + val]:
            #return True
    return False


# -----------------------------------------------------
# PRINT


def update(coordinates: list[list[int]], func: tuple[list[list[int]], list[list[str]]],cur: str, st: list[list[str]], mainscr)\
        -> tuple[list[list[int]], list[list[str]], None|int]:
    for k in coordinates:
        mainscr.addstr(k[0], k[1], " ")
        st[k[0]][k[1]] = " "
    coordinates, st = func
    preview_coordinates, st = drop(coordinates, st, False)
    #for k in preview_coordinates:
        #mainscr.addstr(k[0], k[1], "$")
        #st[k[0]][k[1]] = "$"
    for k in coordinates:
        mainscr.addstr(k[0], k[1], "@", cs.color_pair(piece_colors[cur]))
        st[k[0]][k[1]] = "@"
    mainscr.refresh()
    if preview_coordinates != coordinates:
        for k in preview_coordinates:
            mainscr.addstr(k[0], k[1], " ")
            st[k[0]][k[1]] = " "
    return coordinates, st



def line_clear(st: list[list[str]], com: int, dif: bool) -> tuple[list[list[str]], int, bool]:
    global game_score
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
    if n > 0:
        act_sco = points[n-1] + (50*com)
        if dif:
            act_sco *= 1.5
        if n == 4:
            dif = True
        else:
            dif = False
        game_score += act_sco
        return [[" " for _ in range(10)] for _ in range(n)] + st[:cleared_lines[0]] + st[cleared_lines[-1] + 1:], com+1, dif
    return st, 0, dif


# -----------------------------------------------------
# MOVEMENT

def rotate(coordinates: list[list[int]], cur: str, rot: int, st: list[list[str]])\
        -> tuple[list[list[int]], list[list[str]]]:
    old_coordinates: list[list[int]] = coordinates
    x_coordinates: tuple[int] = [i[1] for i in coordinates]
    if cur == "I":
        xcord_I: int = x_coordinates[0]
        if xcord_I == x_coordinates[3]:
            if rot == 3:
                if xcord_I == 1:
                    coordinates = [[k[0], k[1] + 2] for k in coordinates]
                elif xcord_I == 2:
                    coordinates = [[k[0], k[1] + 1] for k in coordinates]
                elif xcord_I == 18:
                    coordinates = [[k[0], k[1] - 1] for k in coordinates]
            if rot == 1:
                if xcord_I == 18:
                    coordinates = [[k[0], k[1] - 2] for k in coordinates]
                elif xcord_I == 17:
                    coordinates = [[k[0], k[1] - 1] for k in coordinates]
                elif xcord_I == 1:
                    coordinates = [[k[0], k[1] + 1] for k in coordinates]
    else:
        if 1 in x_coordinates:  # prevent rotating into left wall
            coordinates = [[k[0], k[1] + 1] for k in coordinates]
        if 18 in x_coordinates:  # prevent rotating into right wall
            coordinates = [[k[0], k[1] - 1] for k in coordinates]
    new_coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0],
                        coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(4)]
    for k in new_coordinates:
        if k[0] > 20 or k[1] > 18 or "#" in st[k[0]][k[1]]:
            return old_coordinates, st
    return new_coordinates, st


def move_side(val: int, coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    if not collision_side(val, coordinates, st):
        coordinates = [[k[0], k[1] + val] for k in coordinates]
    return coordinates, st


def move_down(coordinates: list[list[int]], st: list[list[str]], scored: bool) -> tuple[list[list[int]], list[list[str]]]:
    global game_score
    if not collision_down(coordinates, st):
        if scored:
            game_score += 1
        return [[k[0] + 1, k[1]] for k in coordinates], st
    return coordinates, st


def drop(coordinates: list[list[int]], st: list[list[str]], scored: bool) -> tuple[list[list[int]], list[list[str]]]:
    global game_score
    while not collision_down(coordinates, st):
        if scored:
            game_score+=2
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    return coordinates, st


# -----------------------------------------------------
# OTHER

def store(coordinates: list[list[int]], stored: str, cur: str, lim: bool, st: list[list[str]], mainscr) \
        -> tuple[list[list[int]], str, str, bool, list[list[str]]]:
    if lim:
        return coordinates, stored, cur, lim, st
    for k in coordinates:
        mainscr.addstr(k[0], k[1], " ")
        st[k[0]][k[1]] = " "
    if stored == "":
        new = generate()
        return default_coordinates[new], cur, new, True, st
    return default_coordinates[stored], cur, stored, True, st


def generate() -> str:
    return choice(list(default_coordinates.keys()))


def set_down(coordinates: list, cur: str, st: list, mainscr) -> list:
    for k in coordinates:
        mainscr.addstr(k[0], k[1], "#", cs.color_pair(1))
        st[k[0]][k[1]] = "#"
    return st


def do_nothing(coordinates: list[list[int]], st: list[list[str]]) -> tuple[list[list[int]], list[list[str]]]:
    return coordinates, st



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
    "Z": 2,
    "S": 1,
    "L": 4,
    "J": 3,
    "O": 3,
    "T": 5,
    "I": 6,
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
# DRIVER CODE

def main(mainscr):
    global game_score
    cs.curs_set(0)
    mainscr = cs.newwin(22,20,0,0)
    mainscr.border("|","|","~","~")
    mainscr.keypad(True)
    mainscr.nodelay(True)
    state: list[list[str]] = [[" " for _ in range(20)] for _ in range(22)]
    stored: str = ""
    combo: int = 0
    difficult: bool = False
    while True:
        current: str = generate()
        cur_coords: list[list[int]] = default_coordinates[current]
        clock: float = 0
        rotation_state: int = 0
        store_limit: bool = False
        cur_coords, state = update(cur_coords, do_nothing(cur_coords, state), current, state, mainscr)
        while True:
            clock += 0.01
            keycode: int = mainscr.getch() # get keyboard input
            if keycode == cs.KEY_DOWN:
                cur_coords, state = update(cur_coords, move_down(cur_coords, state, True), current, state, mainscr)
            elif keycode == cs.KEY_UP and current != "O":
                rotation_success = (cur_coords, state != rotate(cur_coords, current, rotation_state, state))
                if rotation_success:
                    cur_coords, state = update(cur_coords, rotate(cur_coords, current, rotation_state, state), current, state, mainscr)
                    rotation_state = (rotation_state + 1) % 4
            elif keycode == cs.KEY_LEFT:
                cur_coords, state = update(cur_coords, move_side(-1, cur_coords, state), current, state, mainscr)
            elif keycode == cs.KEY_RIGHT:
                cur_coords, state = update(cur_coords, move_side(1, cur_coords, state), current, state, mainscr)
            elif keycode == ord("c"):
                cur_coords, stored, current, store_limit, state = store(cur_coords, stored, current, store_limit, state, mainscr)
                rotation_state = 0
            #elif keycode == ord("e"):
                #menu(state, "pause", game_score, isNew=True)
                #cur_coords, state = update(cur_coords, do_nothing(cur_coords, state), current, state)
            elif keycode == ord(" "):
                cur_coords, state = update(cur_coords, drop(cur_coords, state, True), current, state, mainscr)
            else:
                sleep(0.01)
                if int(clock) == 1:
                    cur_coords, state = update(cur_coords, move_down(cur_coords, state, False), current, state, mainscr)
                    clock = 0
                    if not collision_down(cur_coords, state):
                        cur_coords, state = update(cur_coords, move_down(cur_coords, state, False), current, state, mainscr)
                        clock = 0
                    else:
                        state = set_down(cur_coords, current, state, mainscr)
                        state, combo, difficult = line_clear(state, combo, difficult)
                        break

if __name__ == "__main__":
    cs.wrapper(main)
