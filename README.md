# tetris-py


## Introduction
This is a project I made for my 'Fundamentals of Programming' course at university. The assignment was to code a simple game, using terminal output as a graphics interface.
Out of all the avalible topics, Tetris seemed the most interesting (and hardest to code) to me, which is why I chose it.
This project contains zero AI-written code and minimal amounts of code from forums like Stack Overflow, most of it came straight from my chaotic perfectionist brain.

## Contents
1. tetris_normal.py:
   * Uses Python print() statements
   * Because of this, contains significant screen flicker
   * Works natively on Windows and Linux
2. ~~tetris_curses.py:~~  Scrapped.
   * ~~Uses the 'Curses' module, made for text-mode display handling~~
   * ~~Has no screen flicker~~
   * ~~Works natively on Linux~~
   * ~~Requires launch using Docker on Windows~~  

## How to run tetris_normal.py

### Windows:
1. Download tetris_normal.py.
2. Open a command line interface.
3. Run the following commands in the command line:
   
   a) Check that you have Python installed.

      ```
      python --version
      ```
   b) If Python is not found, follow this installation guide:
   
   * https://www.geeksforgeeks.org/how-to-install-python-on-windows/
   
   c) Run the downloaded file.

      ```
      python C:\Users\%USERNAME%\Downloads\tetris_normal.py
      ```

### Linux:
1. Download tetris_normal.py.
2. Open a command line interface.
3. Run the following commands in the command line:
   
   a) Check that you have Python installed.

      ```
      python3 --version
      ```
   b) If Python is not found, follow this installation guide:
   
   * https://www.geeksforgeeks.org/how-to-install-python-on-linux/
   
   c) Run the downloaded file.

      ```
      python3 /home/${USER}/Downloads/tetris_normal.py
      ```

