from os import name, system
from time import sleep
from msvcrt import getch
from random import choice


def generate():
    return choice(list(pieces.keys()))


def refresh(cords):
    for k in cords:
        state[k[0]][k[1]] = "@"
    return


def rotate():
    return


def move(val, cords, st):
    for k in cords:
        st[k[0]][k[1]] = " "
    return [[k[0], k[1]+val] for k in cords], st


def drop(cords, st):
    for k in cords:
        st[k[0]][k[1]] = " "
    return [[k[0]+1, k[1]] for k in cords], st


def reset():
    return


def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


pieces = {
    "Z": [[0, 3], [0, 4], [1, 4], [1, 5]],
    "Z_reverse": [[0, 4], [0, 5], [1, 3], [1, 4]],
    "L": [[0, 5], [1, 3], [1, 4], [1, 5]],
    "L_reverse": [[0, 3], [1, 3], [1, 4], [1, 5]],
    "Square": [[0, 4], [0, 5], [1, 4], [1, 5]],
    "T": [[0, 5], [1, 4], [1, 5], [1, 6]],
    "|": [[1, 3], [1, 4], [1, 5], [1, 6]]
}
# TODO: change coordinate order (y,x) => (x,y)
state = [[" " for _ in range(10)] for _ in range(21)]

current_piece = generate()
piece_coordinates = pieces[current_piece]
store = []
while True:
    keycode = ord(getch())  # fetch keyboard input
    if keycode == 72:  # Up arrow
        print("rotate right")
    elif keycode == 75:  # Left arrow
        # check if x coordinate after move would be out of range
        if 0 not in [i[1] for i in piece_coordinates]:
            piece_coordinates, state = move(-1, piece_coordinates, state)
    elif keycode == 77:  # Right arrow
        # check if x coordinate after move would be out of range
        if 9 not in [i[1] for i in piece_coordinates]:
            piece_coordinates, state = move(1, piece_coordinates, state)
    elif keycode == 80:  # Down arrow
        try:
            piece_coordinates, state = drop(piece_coordinates, state)
        except IndexError:
            continue
    elif keycode == 99:  # "c"
        temp = current_piece
        if store:
            current_piece = store
            refresh(pieces[store])
        else:
            current_piece = generate()
        store = temp

    elif keycode == 114:  # "r"
        print("reset")
    elif keycode == 32:  # Space
        print("instant drop")

    refresh(piece_coordinates)
    print("-----------------------")
    for i in range(1, 21):
        print("||", end="")
        for j in range(9):
            print(state[i][j], end=",")
        print(state[i][9], end="")
        print("||")
    print("-----------------------")