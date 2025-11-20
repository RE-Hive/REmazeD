#=============Library==============#
import os
import sys
import time
import random
import threading
import json
from collections import deque
#=============Library==============#

#=============VARIABEL==============#
WIDTH, HEIGHT = 71, 31

WALL = '#'
PATH = ' '
PLAYER_CHAR = '@'
EXIT = 'E'
GUARD = 'G'

NUM_GUARD = 6           # jumlah guardian  
timer_left = 0
timer_running = False
#=============VARIABEL==============#


#=============Fungsi Dasar==============#
def slowprint(text, delay=0.1, newline=True):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if newline:
        print()

def clear():
    print("\033[H\033[J", end="")
#=======================================#



#============ MAZE + GUARD SYSTEM ============#

# ==== MAP STATIS DENGAN DEATH ROUTE ==== #
STATIC_MAZE = [
"#######################################################################",
"#                                     #                               #",
"# ################################### # ############### ############# #",
"# #                                      #              #           # #",
"# # #################################### # ############## # ######### #",
"# #    #   #                         #   #              # #         # #",
"# #### # # ##### ################### # # # ############ # # ####### # #",
"# # ## # # #     #                 # # # # #          # # # #   #   # #",
"# # ## # # # ######### ######### # # # # # # ######## # # # # #   # # #",
"# # ## # # #     #     #       # # # # ### # #        # # ########### #",
"# # ## # # ##### # ##### # # # #           # # ######## #           # #",
"# #    # #       #       # # # # #############        # # ######### # #",
"# ###################### # # # # #        #  # ######## # #         # #",
"# #                      # # # # # ## ### #  #          # ########### #",
"# ######################## # # # # ## #   #    ######## #             #",
"# #                        # # # #### # ###########   # ############# #",
"# # ######################## # #    #               # #               #",
"# # #                        # #################### # # ########### # #",
"# # ###### ###### # ######     #        #   #       # # #           # #",
"# # #    # # #    # #    # ######### ## # # # ##### # # # ########### #",
"# # # ## # # # ## # # ## # #       # ## # # # #   # #                 #",
"# # #### #   # ## # #### # ####### # ## # # # # # # # ### ########### #",
"# #      # # #  # #      #         # ## # #   # # # # # #           # #",
"# # ###### ###### # ###### ############ # # # # ### # # ############# #",
"# # # #         # #                #    # # # #     # #               #",
"# # # ######### # ######## ######### #### # # ####### ############### #",
"#   #             #                         #                         #",
"#######################################################################"
]


def make_maze(w, h):
    """Kembali ke static map dan exit random"""
    maze = [list(row) for row in STATIC_MAZE]
    
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == EXIT:  
                maze[y][x] = PATH

    # Ambil semua lokasi kosong yang valid untuk exit dan guardian
    reachable = [(x, y) for y, row in enumerate(maze) 
                 for x, cell in enumerate(row) 
                 if cell == PATH and (x, y) != (1, 1)]

    # === RANDOM EXIT ===
    exit_pos = random.choice(reachable)
    ex, ey = exit_pos
    maze[ey][ex] = EXIT

    # kode exit tidak boleh nempel guardian
    reachable.remove(exit_pos)

    # === RANDOM GUARDIAN ===
    guardian_count = min(NUM_GUARD, len(reachable))
    chosen = random.sample(reachable, guardian_count)
    for (gx, gy) in chosen:
        maze[gy][gx] = GUARD

    return maze


#============ END MAZE SYSTEM ==================#



#================ Timer ====================#
def count_up():
    global timer_left, timer_running
    while timer_running:
        time.sleep(1)
        timer_left += 1
#===========================================#



#============ Input Controller ============#
if os.name == 'nt':
    import msvcrt
    def getch():
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            return ch + msvcrt.getwch()
        return ch

else:
    import select, tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            r, _, _ = select.select([sys.stdin], [], [], 0.01)
            if r:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    return ch + sys.stdin.read(2)
                return ch
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
#===========================================#



#================ Soal ====================#
def load_questions_from_json(filename="jatim.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [(i["q"].strip(), i["a"].strip()) for i in data if "q" in i and "a" in i]
    except:
        print("Error membaca jatim.json !")
        return []

BASE = os.path.dirname(os.path.abspath(__file__))
questions = load_questions_from_json(os.path.join(BASE, "jatim.json"))

def pick_random_question(q):
    return random.choice(q) if q else (None, None)
#===========================================#



#================ Render ==================#
def render(maze, player_pos, steps):
    clear()
    px, py = player_pos
    lines = []

    for y, row in enumerate(maze):
        line = []
        for x, cell in enumerate(row):
            if (x, y) == (px, py):
                line.append(PLAYER_CHAR)
            elif cell == WALL:
                line.append('█')
            elif cell == GUARD:
                line.append('E')
            else:
                line.append(cell)
        lines.append(''.join(line))

    lines.append(f"\nLangkah: {steps} | Waktu: {timer_left}s  (WASD / Arrow = gerak, q = keluar)")
    lines.append("@ = Adalah ANDA,   Temukan Pintu Asli Diantara Pintu Palsu yang di jaga")
    lines.append("Jika anda salah menjawab pertanyaan maka GAME OVER")
    print("\n".join(lines))
#===========================================#



#================ Translate Key ============#
def translate_key(ch):
    if ch in ('w','W'): return (0,-1)
    if ch in ('s','S'): return (0,1)
    if ch in ('a','A'): return (-1,0)
    if ch in ('d','D'): return (1,0)

    if ch == '\x1b[A': return (0,-1)
    if ch == '\x1b[B': return (0,1)
    if ch == '\x1b[C': return (1,0)
    if ch == '\x1b[D': return (-1,0)

    if ch in ('\x00H','\xe0H'): return (0,-1)
    if ch in ('\x00P','\xe0P'): return (0,1)
    if ch in ('\x00M','\xe0M'): return (1,0)
    if ch in ('\x00K','\xe0K'): return (-1,0)

    return None
#===========================================#



#================== MAIN GAME ==================#
def play():
    slowprint("SELAMAT DATANG DI LABIRIN TANTANGAN\n")
    print(f"Dalam labirin ini kalian hanya pelru satu aturan, Temukan pintu asli dari {NUM_GUARD} Pintu yang ada ")
    print("Jika anda terkena pintu palsu maka anda akan dihadang oleh guardian pertanyaan")
    print("Jawab pertanyaan yang diberikan dengan benar, jika salah GAME OVER\n")
    slowprint("GAME AKAN DIMULAI DALAM 5 DETIK", 0.03)
    slowprint("SELAMAT MENIKMATI PERMAINAN", 0.02)
    time.sleep(5)

    maze = make_maze(WIDTH, HEIGHT)
    px, py = 1, 1
    steps = 0

    # Timer
    global timer_left, timer_running
    timer_left = 0
    timer_running = True
    threading.Thread(target=count_up, daemon=True).start()

    try:
        while True:
            render(maze, (px, py), steps)
            ch = getch()

            if ch is None:
                continue

            if ch.lower() == 'q':
                timer_running = False
                return "exit"

            move = translate_key(ch)
            if not move:
                continue

            dx, dy = move
            nx, ny = px + dx, py + dy

            if maze[ny][nx] == WALL:
                continue

            px, py = nx, ny
            steps += 1

            if maze[py][px] == GUARD:
                render(maze, (px, py), steps)
                print("\nGuardian menghadangmu! Jawab soal:")

                q, a = pick_random_question(questions)
                if q is None:
                    print("Error: Tidak ada soal!")
                    return "exit"

                print("\nSoal:", q)
                jawaban = input("Jawaban: ").strip().lower()

                if jawaban.lower().strip() == a.lower().strip():
                    print("\nBenar! Guardian menghilang.")
                    maze[py][px] = PATH
                    time.sleep(0.8)
                else:
                    print("\nSALAH! GAME OVER.")
                    print("Jawaban benar:", a)
                    timer_running = False
                    time.sleep(1.4)
                    return "exit"

            if maze[py][px] == EXIT:
                timer_running = False
                render(maze, (px, py), steps)
                print("\n🎉 Kamu berhasil keluar!")
                slowprint("Selamat kamu berhasil menemukan pintu keluar yang asli...", 0.04)
                return "WIN"

    except KeyboardInterrupt:
        timer_running = False
        clear()
        print("\nDihentikan.")
        return "exit"