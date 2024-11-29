from os import name, system
from time import sleep
from msvcrt import getch, kbhit
from random import choice


def generate():
    return choice(list(default_coordinates.keys()))


def refresh(coordinates, func):
    for k in coordinates:
        state[k[0]][k[1]] = " "
    coordinates = func
    for k in coordinates:
        state[k[0]][k[1]] = "@"
    return coordinates


def move_side(val, coordinates):
    coordinates = [[k[0], k[1]+val] for k in coordinates]
    return coordinates


def move_down(coordinates):
    coordinates = [[k[0]+1, k[1]] for k in coordinates]
    return coordinates


def drop(coordinates):
    diff = 20 - max([k[0] for k in coordinates])
    coordinates = [[k[0] + diff, k[1]] for k in coordinates]
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
        coordinates = [[k[0]+1, k[1]] for k in coordinates]
    elif 20 in [i[0] for i in coordinates]:  # prevent rotating into floor
        coordinates = [[k[0]-1, k[1]] for k in coordinates]
    if 0 in [i[1] for i in coordinates]:  # prevent rotating into left wall
        coordinates = [[k[0], k[1]+1] for k in coordinates]
    elif 9 in [i[1] for i in coordinates]:  # prevent rotating into right wall
        coordinates = [[k[0], k[1]-1] for k in coordinates]
    coordinates = [[coordinates[k][0] + rotation_table[cur][rot][k][0], coordinates[k][1] + rotation_table[cur][rot][k][1]] for k in range(len(coordinates))]
    for k in coordinates:
        state[k[0]][k[1]] = "@"
    return coordinates, (rot+1)%4  # keep rotation_state within <0,3>


default_coordinates = {
    "Z":         [[0, 3], [0, 4], [1, 4], [1, 5]],
    "Z_reverse": [[0, 4], [0, 5], [1, 3], [1, 4]],
    "L":         [[0, 5], [1, 3], [1, 4], [1, 5]],
    "L_reverse": [[0, 3], [1, 3], [1, 4], [1, 5]],
    "Square":    [[0, 4], [0, 5], [1, 4], [1, 5]],
    "T":         [[0, 5], [1, 4], [1, 5], [1, 6]],
    "|":         [[1, 3], [1, 4], [1, 5], [1, 6]]
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
while True:
    state = [[" " for _ in range(10)] for _ in range(21)]
    current_piece = generate()
    piece_coordinates = default_coordinates[current_piece]
    stored_piece = ""
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
                    piece_coordinates = refresh(piece_coordinates, move_down(piece_coordinates))
            elif keycode == 99:  # "c"
                piece_coordinates, stored_piece, current_piece = store(piece_coordinates, stored_piece, current_piece)
            elif keycode == 114:  # "r"
                break
            elif keycode == 32:  # Space
                piece_coordinates = refresh(piece_coordinates, drop(piece_coordinates))
        else:
            if 20 not in [i[0] for i in piece_coordinates] and int(clock) == 1:
                clock = 0
                piece_coordinates = refresh(piece_coordinates, move_down(piece_coordinates))
        clear()
        print("_"*(resolution*10+13))
        for i in range(1, 21):
            for m in range(resolution):
                print("||", end="")
                for j in range(9):
                    if m%resolution==resolution-1:
                        print(state[i][j]*resolution, end=",")
                    else:
                        print(state[i][j]*resolution, end=" ")
                print(state[i][9]*resolution, end="")
                print("||")
        print("̅"*(resolution*10+13))
    
    
