from time import sleep
from msvcrt import getch

while True:
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
    print(keycode)
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
