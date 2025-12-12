#=============Library==============#
import os, sys, time, random, threading,json

#=============VARIABEL==============#
WIDTH, HEIGHT = 71, 31
WALL = '█'
PATH = ' '
PLAYER_CHAR = '@'
EXIT_LOCKED = 'X'
EXIT_OPEN = 'E'
timer_left = 300
timer_running = False
timer_done = False
game_over = False
num_enemies = 7
enemies = []
player_pos = {"x":1,"y":1}
input_mode = False

#=============SLOWPRINT==============#
def slowprint(text, delay=0.02):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

#=============CLEAR SCREEN==============#
def clear():
    #os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H\033[J", end='')
    
def reset():
    global timer_left, game_over, player_pos, enemies
    timer_left = 300
    game_over = False

    # reset posisi player
    player_pos = {"x": 1, "y": 1}

    # reset musuh
    enemies = [{"x": 10, "y": 10}]

#=============MAKE MAP==============#
def make_maze():
    maze = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(1, HEIGHT-1):
        for x in range(1, WIDTH-1):
            if y % 2 == 1 or x % 4 == 1:
                maze[y][x] = PATH
    for i in range(3, HEIGHT-3, 6):
        for j in range(3, WIDTH-3, 8):
            maze[i][j] = WALL
    # Exit terkunci
    maze[HEIGHT-2][WIDTH-2] = EXIT_LOCKED
    # Start point
    maze[1][1] = PATH
    return maze

maze = make_maze()

#=============PLACE ENEMIES RANDOM==============#
def place_enemies():
    global enemies
    enemies = []
    while len(enemies) < num_enemies:
        x = random.randint(1, WIDTH-2)
        y = random.randint(1, HEIGHT-2)
        if maze[y][x] == PATH and (x, y) != (player_pos["x"], player_pos["y"]) and not any(e["x"]==x and e["y"]==y for e in enemies):
            enemies.append({"x":x, "y":y})

#=============SOAL MUSUH==============#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOAL_PATH = os.path.join(BASE_DIR, "soal.json")

with open(SOAL_PATH, "r") as f:
    soal_list = json.load(f)

def load_soal():
    try:
        with open("soal.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print("Gagal memuat soal.json:", e)
        return []
    soal_list = load_soal()


#=============GETCH PLATFORM INDEPENDENT==============#
if os.name=='nt':
    import msvcrt
    def getch():
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00','\xe0'):
                ch += msvcrt.getwch()
                return ch
            return ch
        return None
else:
    import select, tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            r,_,_ = select.select([sys.stdin],[],[],0.01)
            if r:
                ch = sys.stdin.read(1)
                if ch=='\x1b':
                    ch += sys.stdin.read(2)
                return ch
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

#=============TRANSLATE KEY==============#
def translate_key(ch):
    if ch in ('w','W'): return (0,-1)
    if ch in ('s','S'): return (0,1)
    if ch in ('a','A'): return (-1,0)
    if ch in ('d','D'): return (1,0)
    if ch=='\x1b[A': return (0,-1)
    if ch=='\x1b[B': return (0,1)
    if ch=='\x1b[C': return (1,0)
    if ch=='\x1b[D': return (-1,0)
    if ch in ('\x00H','\xe0H'): return (0,-1)
    if ch in ('\x00P','\xe0P'): return (0,1)
    if ch in ('\x00M','\xe0M'): return (1,0)
    if ch in ('\x00K','\xe0K'): return (-1,0)
    return None

#=============RENDER=================#
import sys

def render(steps):
    try:
        clear()
    except NameError:
        os.system('cls' if os.name == 'nt' else 'clear')
    enemy_pos = {(e["x"], e["y"]) for e in enemies}

    lines = []
    for y, row in enumerate(maze):
        row_chars = []
        for x, cell in enumerate(row):
            if (x, y) == (player_pos["x"], player_pos["y"]):
                row_chars.append(PLAYER_CHAR)
            elif (x, y) in enemy_pos:
                row_chars.append('K')
            else:
                row_chars.append(cell)
        lines.append(''.join(row_chars))

    status = f"Langkah: {steps} | Sisa Waktu: {timer_left}s | Musuh tersisa: {len(enemies)} (WASD / q=keluar)"
    lines.append(status)
    lines.append(" @ = ANDA    K = Musuh    X = Pintu Yang Terkunci     E = Pintu keluar ")
    
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

#=============ENEMY LOGIC==============#
def move_enemies():
    while not game_over:
        for e in enemies:
            dx,dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
            nx,ny = e["x"]+dx, e["y"]+dy
            if 0 < nx < WIDTH-1 and 0 < ny < HEIGHT-1 and maze[ny][nx] == PATH:
                if not any(en["x"]==nx and en["y"]==ny for en in enemies):
                    e["x"], e["y"] = nx, ny
        time.sleep(1.5)


def flush_input():
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        
def enemy_encounter():
    global game_over, input_mode

    for e in enemies:
        if abs(e["x"] - player_pos["x"]) <= 1 and abs(e["y"] - player_pos["y"]) <= 1:

            input_mode = True
            
            slowprint("\nMusuh menangkap Anda! Jawab soal untuk melawan.", 0.03)
            time.sleep(0.5)
            question = random.choice(soal_list)
            
            slowprint(f"Soal: {question['q']}", 0.03)

            flush_input()
            
            answer = input("Jawaban: ")
            
            input_mode = False

            if answer.lower().strip() == question["a"].lower().strip():
                slowprint("Musuh kalah!\n", 0.02)
                enemies.remove(e)
                return
            else:
                slowprint("Salah! Kamu kalah...", 0.03)
                game_over = True
                return


#=============TIMER=================#
def countdown():
    global timer_left, timer_done
    while timer_left>0 and timer_running and not game_over:
        time.sleep(1)
        timer_left -= 1
    if timer_left<=0: timer_done=True

#=============GAME LOOP==============#
def play():
    global timer_running, timer_done, game_over
    timer_running=True
    timer_done=False
    game_over=False

    place_enemies()
    threading.Thread(target=countdown,daemon=True).start()
    threading.Thread(target=move_enemies,daemon=True).start()

    slowprint("SELAMAT DATANG DI LABIRIN GERILYA",0.02)
    slowprint("HABISI SEMUA PENJAJAH  (K)  UNTUK DAPAT KELUAR\n",0.02)
    print("Kalahkan Semua Musuh (K) Untuk Membuka Pintu Yang Terkunci (X)")
    print(" @ = ANDA    K = Musuh    X = Pintu Yang Terkunci     E = Pintu keluar \n")
    slowprint("Baca dengan cermat, GAME AKAN DIMULAI DALAM 5 DETIK....")
    time.sleep(5)

    steps=0
    while True:
        start_loop=time.time()
        if timer_done:
            render(steps)
            slowprint("WAKTU HABIS!! GAME OVER",0.03)
            timer_running=False
            return "TIMEOUT"
        if game_over:
            render(steps)
            slowprint("ANDA KALAH DALAM PERTEMPURAN!",0.03)
            time.sleep(0.7)
            timer_running=False
            return "LOSE"

        render(steps)
        
        if not input_mode:
            ch = getch()
            
        if ch is not None:
            if ch in ('q','Q'):
                timer_running=False
                return "exit"
            mv=translate_key(ch)
            if mv:
                dx,dy=mv
                nx,ny=player_pos["x"]+dx,player_pos["y"]+dy
                if 0<=nx<WIDTH and 0<=ny<HEIGHT and maze[ny][nx]!=WALL:
                    player_pos["x"],player_pos["y"]=nx,ny
                    steps+=1
                    enemy_encounter()

        # buka exit 
        if len(enemies)==0:
            for y in range(len(maze)):
                for x in range(len(maze[y])):
                    if maze[y][x] == EXIT_LOCKED:
                        maze[y][x] = EXIT_OPEN

        if maze[player_pos["y"]][player_pos["x"]]==EXIT_OPEN:
            render(steps)
            slowprint("\n🎉 Semua musuh dikalahkan! Kamu keluar dengan selamat!",0.03)
            slowprint("Anda Berhasil Memenangkan Permainan....")
            timer_running=False
            return "WIN"

        elapsed=time.time()-start_loop
        time.sleep(max(0.01-elapsed,0))

#=============MAIN==============#