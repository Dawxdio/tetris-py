from os import name, system
from time import sleep
from random import choice

if name == 'nt':  # windows
    from msvcrt import getch, kbhit
# elif name == 'unix':  # linux
    # import termios, fcntl, sys
else:
    print("Unsupported Operating System")


def generate():
    return choice(list(default_coordinates.keys()))


def ignore_inner(val, coordinates: list):
    if val == 0:
        x_set = set()
        for k in coordinates:
            x_set.add(k[1])
        coordinates = [max([m for m in coordinates if m[1] == k]) for k in x_set]
    elif val == 1:
        y_set = set()
        for k in coordinates:
            y_set.add(k[0])
        coordinates = [max([m for m in coordinates if m[0] == k]) for k in y_set]
    elif val == -1:
        y_set = set()
        for k in coordinates:
            y_set.add(k[0])
        coordinates = [min([m for m in coordinates if m[0] == k]) for k in y_set]
    return coordinates


def collision_down(coordinates):
    coordinates = ignore_inner(0, coordinates)
    for k in coordinates:
        if k[0] == 20 or state[k[0] + 1][k[1]] == "@":
            return True
    return False


def collision_side(val, coordinates):
    coordinates = ignore_inner(val, coordinates)
    for k in coordinates:
        if state[k[0]][k[1] + val] == "@":
            return True
    return False


def refresh(coordinates, func):
    for k in coordinates:
        state[k[0]][k[1]] = " "  # clear previous coordinates
    coordinates = func
    for k in coordinates:
        state[k[0]][k[1]] = "@"  # draw new piece
    return coordinates


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


def store(coordinates, stored, cur):
    for k in coordinates:
        state[k[0]][k[1]] = " "
    if stored == "":
        new = generate()
        return default_coordinates[new], cur, new,
    return default_coordinates[stored], cur, stored


def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def rotate(coordinates, cur, rot):
    for k in coordinates:
        state[k[0]][k[1]] = " "
    if 0 in [i[0] for i in coordinates]:  # prevent rotating into ceiling
        coordinates = [[k[0] + 1, k[1]] for k in coordinates]
    elif 20 in [i[0] for i in coordinates]:  # prevent rotating into floor
        coordinates = [[k[0] - 1, k[1]] for k in coordinates]
    if 0 in [i[1] for i in coordinates]:  # prevent rotating into left wall
        coordinates = [[k[0], k[1] + 1] for k in coordinates]
    elif 9 in [i[1] for i in coordinates]:  # prevent rotating into right wall
        coordinates = [[k[0], k[1] - 1] for k in coordinates]
    coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0],
                    coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(len(coordinates))]
    for k in coordinates:
        state[k[0]][k[1]] = "@"
    return coordinates, (rot + 1) % 4  # keep rotation_state within <0,3>


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
    "Z": '\033[91m',
    "Z_reverse": '\033[92m',
    "L": '\033[93m',
    "L_reverse": '\033[94m',
    "Square": '\033[33m',
    "T": '\033[95m',
    "|": '\033[96m'
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
stored_piece = ""

while True:
    current_piece = generate()
    piece_coordinates = default_coordinates[current_piece]
    rotation_state = 0
    resolution = 1
    clock = 0
    while True:
        clock += 0.01
        if kbhit():  # check if there is keyboard input
            keycode = ord(getch())  # get keyboard input
            if keycode == 72 and current_piece != "Square":  # Up arrow
                piece_coordinates, rotation_state = rotate(piece_coordinates, current_piece, rotation_state)
            elif keycode == 75:  # Left arrow
                if 0 not in [i[1] for i in piece_coordinates]:  # check if coordinate after move would be out of range
                    piece_coordinates = refresh(piece_coordinates, move_side(-1, piece_coordinates))
            elif keycode == 77:  # Right arrow
                if 9 not in [i[1] for i in piece_coordinates]:
                    piece_coordinates = refresh(piece_coordinates, move_side(1, piece_coordinates))
            elif keycode == 80:  # Down arrow
                if 20 not in [i[0] for i in piece_coordinates]:
                    if not collision_down(piece_coordinates):
                        piece_coordinates = refresh(piece_coordinates, move_down(piece_coordinates))
                    else:
                        break
                else:
                    break
            elif keycode == 99:  # "c"
                piece_coordinates, stored_piece, current_piece = store(piece_coordinates, stored_piece, current_piece)
            elif keycode == 114:  # "r"
                break
            elif keycode == 32:  # Space
                piece_coordinates = refresh(piece_coordinates, drop(piece_coordinates))
                break
        else:
            if int(clock) == 1:
                if 20 not in [i[0] for i in piece_coordinates]:
                    if not collision_down(piece_coordinates):
                        clock = 0
                        piece_coordinates = refresh(piece_coordinates, move_down(piece_coordinates))
                    else:
                        break
                else:
                    break
        print("_" * (resolution * 10 + 13))
        for i in range(1, 21):
            for m in range(resolution):
                print("||", end="")
                for j in range(9):
                    if m % resolution == resolution - 1:
                        print(state[i][j] * resolution, end=',')
                    else:
                        print(state[i][j] * resolution, end=" ")
                print(state[i][9] * resolution, end="")
                print("||")
        print("̅" * (resolution * 10 + 13))
        clear()
