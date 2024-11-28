from os import name, system
from time import sleep
from msvcrt import getch, kbhit
from random import choice


def generate():
    return choice(list(default_cords.keys()))


def refresh(cords):
    for k in cords:
        state[k[0]][k[1]] = "@"
    return


def rotate():
    return


def move_side(val, cords, st):
    for k in cords:
        st[k[0]][k[1]] = " "  # clear previous placement
    cords = [[k[0], k[1]+val] for k in cords]
    refresh(cords)
    return cords, st


def move_down(cords, st):
    for k in cords:
        st[k[0]][k[1]] = " "  # clear previous placement
    cords = [[k[0]+1, k[1]] for k in cords]
    refresh(cords)
    return cords, st


def drop(cords, st):  # placeholder
    for k in cords:
        st[k[0]][k[1]] = " "  # clear previous placement
    diff = 20 - max([k[0] for k in cords])
    cords = [[k[0] + diff, k[1]] for k in cords]
    refresh(cords)
    return cords, st


def store(cords, st, stored, cur):
    for k in cords:
        st[k[0]][k[1]] = " "
    if stored == "":
        new = generate()
        return default_cords[new], cur, new, 
    return default_cords[stored], cur, stored


def reset():
    return


def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


default_cords = {
    "Z": [[0, 3], [0, 4], [1, 4], [1, 5]],
    "Z_reverse": [[0, 4], [0, 5], [1, 3], [1, 4]],
    "L": [[0, 5], [1, 3], [1, 4], [1, 5]],
    "L_reverse": [[0, 3], [1, 3], [1, 4], [1, 5]],
    "Square": [[0, 4], [0, 5], [1, 4], [1, 5]],
    "T": [[0, 5], [1, 4], [1, 5], [1, 6]],
    "|": [[1, 3], [1, 4], [1, 5], [1, 6]]
}

state = [[" " for _ in range(10)] for _ in range(21)]

current_piece = generate()
piece_coordinates = default_cords[current_piece]
stored_piece = ""
resolution = 2
clock = 0
while True:
    clock += 0.01
    if kbhit():  # check if there is keyboard input
        keycode = ord(getch())  # get keyboard input
        if keycode == 72:  # Up arrow
            print("rotate right")
        elif keycode == 75:  # Left arrow
            # check if horizontal coordinate after move would be out of range
            if 0 not in [i[1] for i in piece_coordinates]:
                piece_coordinates, state = move_side(-1, piece_coordinates, state)
        elif keycode == 77:  # Right arrow
            # check if horizontal coordinate after move would be out of range
            if 9 not in [i[1] for i in piece_coordinates]:
                piece_coordinates, state = move_side(1, piece_coordinates, state)
        elif keycode == 80:  # Down arrow
            # check if vertical coordinate after move would be out of range
            if 20 not in [i[0] for i in piece_coordinates]:
                piece_coordinates, state = move_down(piece_coordinates, state)
        elif keycode == 99:  # "c"
            piece_coordinates, stored_piece, current_piece = store(piece_coordinates, state, stored_piece, current_piece)
        elif keycode == 114:  # "r"
            print("reset")
        elif keycode == 32:  # Space
            piece_coordinates, state = drop(piece_coordinates, state)
    else:
        # check if vertical coordinate after move would be out of range
        if 20 not in [i[0] for i in piece_coordinates] and int(clock) == 1:
            clock = 0
            piece_coordinates, state = move_down(piece_coordinates, state)
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
    
    
