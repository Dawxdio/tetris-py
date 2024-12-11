from os import name, system
from time import sleep
from random import choice
from re import search

if name == 'nt':  # windows
    from msvcrt import getch, kbhit


# -----------------------------------------------------
# CHECKS

def collision_down(coordinates):
    for k in coordinates:
        if k[0] == 20 or search(r".+#.+", state[k[0] + 1][k[1]]):
            return True
    return False


def collision_side(val, coordinates):
    for k in coordinates:
        if search(r".+#.+", state[k[0]][k[1] + val]):
            return True
    return False


# -----------------------------------------------------
# PRINT

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def refresh(coordinates, func, cur):
    preview = "\033[38;5;244m\033[48;5;244m"
    for k in coordinates:
        state[k[0]][k[1]] = " "  # clear previous coordinates
    coordinates = func
    preview_coordinates = drop(coordinates)
    for k in preview_coordinates:
        state[k[0]][k[1]] = f"{preview}$\033[0m"  # draw preview
    for k in coordinates:
        state[k[0]][k[1]] = f"{piece_colors[cur]}@\033[0m"  # draw new piece
    clear()
    print("_" * 23)
    for i in range(1, 21):
        print("||", end="")
        for j in range(10):
            print(state[i][j] * 2, end="")
        print("||")
    print("̅" * 23)
    if preview_coordinates != coordinates:
        for k in preview_coordinates:
            state[k[0]][k[1]] = " "
    return coordinates


def set_down(coordinates, cur):
    for k in coordinates:
        state[k[0]][k[1]] = f"{piece_colors[cur]}#\033[0m"
    return


# -----------------------------------------------------
# MOVEMENT

def rotate(coordinates, cur, rot):
    old_coordinates = coordinates
    y_coordinates = [i[0] for i in coordinates]
    x_coordinates = [i[1] for i in coordinates]
    if 0 in y_coordinates:  # prevent rotating into ceiling
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    elif 20 in y_coordinates:  # prevent rotating into floor
        coordinates = [[k[0] - 1, k[1]] for k in coordinates]
    if cur == "|" and rot == 3:
        if 0 in x_coordinates or 1 in x_coordinates:
            coordinates = [[k[0], k[1] + 2] for k in coordinates]
    elif 0 in x_coordinates:  # prevent rotating into left wall
        coordinates = [[k[0], k[1] + 1] for k in coordinates]
    if cur == "|" and rot == 1:
        if 9 in x_coordinates or 8 in x_coordinates:
            coordinates = [[k[0], k[1] - 2] for k in coordinates]
    elif 9 in x_coordinates:  # prevent rotating into right wall
        coordinates = [[k[0], k[1] - 1] for k in coordinates]
    new_coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0],
                        coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(len(coordinates))]
    for k in new_coordinates:
        if search(r".+#.+", state[k[0]][k[1]]):
            return old_coordinates
    return new_coordinates


def move_side(val, coordinates):
    if not collision_side(val, coordinates):
        coordinates = [[k[0], k[1] + val] for k in coordinates]
    return coordinates


def move_down(coordinates):
    return [[k[0] + 1, k[1]] for k in coordinates]


def drop(coordinates):
    while not collision_down(coordinates):
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    return coordinates


# -----------------------------------------------------
# OTHER

def store(coordinates, stored, cur, lim):
    if lim:
        return coordinates, stored, cur, lim
    for k in coordinates:
        state[k[0]][k[1]] = " "
    if stored == "":
        new = generate()
        return default_coordinates[new], cur, new, True
    return default_coordinates[stored], cur, stored, True


def generate():
    return choice(list(default_coordinates.keys()))


def do_nothing(coordinates):
    return coordinates


# -----------------------------------------------------
# BLOCK DATA

default_coordinates = {
    "Z": [[0, 3], [0, 4], [1, 4], [1, 5]],
    "Z_reverse": [[0, 4], [0, 5], [1, 3], [1, 4]],
    "L": [[0, 5], [1, 3], [1, 4], [1, 5]],
    "L_reverse": [[0, 3], [1, 3], [1, 4], [1, 5]],
    "Square": [[0, 4], [0, 5], [1, 4], [1, 5]],
    "T": [[0, 5], [1, 4], [1, 5], [1, 6]],
    "|": [[1, 3], [1, 4], [1, 5], [1, 6]]
}

piece_colors = {
    "Z": '\033[91;101m',
    "Z_reverse": '\033[92;102m',
    "L": '\033[94;104m',
    "L_reverse": '\033[38;5;202m\033[48;5;202m',
    "Square": '\033[93;103m',
    "T": '\033[95;105m',
    "|": '\033[96;106m'
}

rotation_table = {
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

state = [[" " for _ in range(10)] for _ in range(21)]


# -----------------------------------------------------
# DRIVER CODE

def main():
    stored = ""
    while True:
        current = generate()
        cur_coords = default_coordinates[current]
        clock = 0
        rotation_state = 0
        store_limit = False
        while True:
            x_coords = [i[1] for i in cur_coords]
            clock += 0.01
            if kbhit():  # check if there is keyboard input
                keycode = ord(getch())  # get keyboard input
                if keycode == 72 and current != "Square":  # Up arrow
                    rotation_success = (cur_coords != rotate(cur_coords, current, rotation_state))
                    if rotation_success:
                        cur_coords = refresh(cur_coords, rotate(cur_coords, current, rotation_state), current)
                        rotation_state = (rotation_state + 1) % 4
                elif keycode == 75:  # Left arrow
                    if 0 not in x_coords:  # check if coordinate after move would be out of range
                        cur_coords = refresh(cur_coords, move_side(-1, cur_coords), current)
                elif keycode == 77:  # Right arrow
                    if 9 not in x_coords:
                        cur_coords = refresh(cur_coords, move_side(1, cur_coords), current)
                elif keycode == 80:  # Down arrow
                    if not collision_down(cur_coords):
                        cur_coords = refresh(cur_coords, move_down(cur_coords), current)
                    else:
                        set_down(cur_coords, current)
                        break
                elif keycode == 99:  # "c"
                    cur_coords, stored, current, store_limit = store(cur_coords, stored, current, store_limit)
                    rotation_state = 0
                    refresh(cur_coords, do_nothing(cur_coords), current)
                elif keycode == 114:  # "r"
                    break
                elif keycode == 32:  # Space
                    cur_coords = refresh(cur_coords, drop(cur_coords), current)
                    set_down(cur_coords, current)
                    break
            else:
                sleep(0.01)
                if int(clock) == 1:
                    if not collision_down(cur_coords):
                        clock = 0
                        cur_coords = refresh(cur_coords, move_down(cur_coords), current)
                    else:
                        set_down(cur_coords, current)
                        break


if __name__ == "__main__":
    main()
