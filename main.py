from time import sleep
from msvcrt import getch


def generate():
    return


def rotate():
    return


def move():
    return


def drop():
    return


def keep():
    return


def reset():
    return


state = [[" " for _ in range(10)] for _ in range(20)]

while True:
    print(" - - - - - - - - - - ")
    for i in range(20):
        print("|", end="")
        for j in range(10):
            print(state[i][j], end=" ")
        print("|")
    print(" - - - - - - - - - - ")
    keycode = ord(getch())
    if keycode == 72:  # Up arrow
        print("rotate right")
    elif keycode == 75:  # Left arrow
        print("move left")
    elif keycode == 77:  # Right arrow
        print("move right")
    elif keycode == 80:  # Down arrow
        print("slow drop")
    elif keycode == 99:  # "c"
        print("keep")
    elif keycode == 114:  # "r"
        print("reset")
    elif keycode == 32:  # Space
        print("instant drop")
#
# def clear():
#     if name == 'nt':
#         _ = system('cls')
#     else:
#         _ = system('clear')

#
# while True:
#     print("""
#     | - - - - - - - - - - |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     |                     |
#     | _ _ _ _ _ _ _ _ _ _ |
#     """)
#     sleep(1)
#     a=input()
#     clear()
