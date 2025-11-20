#=============Library==============#
import os, sys, time, random, threading, json, atexit

#=============VARIABEL KONSTAN==============#
WIDTH, HEIGHT = 71, 31
WALL = '█'
PATH = ' '
PLAYER_CHAR = '@'
EXIT_LOCKED = 'X'
EXIT_OPEN = 'E'
ITEM_CHAR = '?'
NUM_REQUIRED_ITEMS = 5
ITEM_NAMES = ["Onde-onde", "Brem", "Gethuk Pisang", "Wingko Babat", "Madumongso"]

#=============VARIABEL GAME STATE==============#
timer_left = 300
timer_running = False
timer_done = False
game_over = False
player_pos = {"x": 1, "y": 1}
collected_items = []
items_to_find = []

#=============TERMINAL SETUP & TEARDOWN==============#
def enable_alt_screen():
    sys.stdout.write("\033[?1049h\033[?25l")
    sys.stdout.flush()

def disable_alt_screen():
    sys.stdout.write("\033[?1049l\033[?25h")
    sys.stdout.flush()

atexit.register(disable_alt_screen)

#=============SLOWPRINT & CLEAR SCREEN & RESET==============#
def slowprint(text, delay=0.02):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def clear():
    #print("\033[2J\033[H", end='')
    print("\033[H", end='')

def reset():
    global timer_left, game_over, player_pos, collected_items
    timer_left = 300
    game_over = False
    player_pos = {"x": 1, "y": 1}
    collected_items = []

#=============MAKE MAP (KONSTAN)==============#
def make_maze_constant():
    maze = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(1, HEIGHT-1):
        for x in range(1, WIDTH-1):
            if y % 2 == 1 or x % 4 == 1:
                maze[y][x] = PATH
    for i in range(3, HEIGHT-3, 6):
        for j in range(3, WIDTH-3, 8):
            maze[i][j] = WALL
    maze[HEIGHT-2][WIDTH-2] = EXIT_LOCKED
    maze[1][1] = PATH
    return [list(row) for row in maze]

MAZE_TEMPLATE = make_maze_constant()
maze = [list(row) for row in MAZE_TEMPLATE]

#=============SOAL & ITEM LOGIC==============#
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if os.path.exists(os.path.abspath(__file__)) else os.getcwd()
SOAL_PATH = os.path.join(BASE_DIR, "makanan.json")

def load_soal():
    if not os.path.exists(SOAL_PATH):
        return []
    try:
        with open(SOAL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception:
        return []

soal_list = load_soal()

def place_items_randomly():
    global items_to_find
    items_to_find = []
    required_names = ITEM_NAMES[:NUM_REQUIRED_ITEMS]
    valid_paths = []
    for y in range(1, HEIGHT - 1):
        for x in range(1, WIDTH - 1):
            if maze[y][x] == PATH and not (x == 1 and y == 1):
                valid_paths.append((x, y))
    if len(valid_paths) < NUM_REQUIRED_ITEMS:
        return
    item_locations = random.sample(valid_paths, NUM_REQUIRED_ITEMS)
    for i in range(NUM_REQUIRED_ITEMS):
        x, y = item_locations[i]
        items_to_find.append({"name": required_names[i], "x": x, "y": y})

#=============INPUT THREAD FOR NON-BLOCKING ANSWERS==============
jawaban_thread_running = False
jawaban_result = None

def _input_worker(prompt):
    global jawaban_thread_running, jawaban_result
    try:
        jawaban_result = input(prompt)
    except Exception:
        jawaban_result = ''
    jawaban_thread_running = False

# =========================================================
def check_item_encounter():
    global collected_items, items_to_find, jawaban_thread_running, jawaban_result

    for item in list(items_to_find):
        if player_pos["x"] == item["x"] and player_pos["y"] == item["y"]:
            time.sleep(0.1)
            slowprint(f"\nAnda menemukan item misterius! Jawab pertanyaan berikut untuk membukanya!", 0.03)

            if not soal_list:
                slowprint("Tidak ada soal tersedia. Item didapatkan secara otomatis.", 0.03)
                collected_items.append(item["name"])
                items_to_find.remove(item)
                return

            question = random.choice(soal_list)
            slowprint(f"Soal: {question['q']}", 0.03)

            jawaban_result = None
            jawaban_thread_running = True
            t = threading.Thread(target=_input_worker, args=("Jawaban: ",), daemon=True)
            t.start()

            # wait for answer in background without blocking other threads (timer runs)
            while jawaban_thread_running:
                time.sleep(0.01)

            answer = (jawaban_result or "").strip()

            if answer.lower().strip() == question["a"].lower().strip():
                slowprint(f"Jawaban benar! Item ini adalah: **{item['name']}**!", 0.02)
                slowprint(f"Anda berhasil mendapatkan **{item['name']}**!", 0.02)
                collected_items.append(item["name"])
                items_to_find.remove(item)
                if len(collected_items) == NUM_REQUIRED_ITEMS:
                    slowprint("Semua item terkumpul! Pintu keluar terbuka!", 0.03)
            else:
                slowprint(f"Jawaban salah! Item ini tetap misterius dan tidak Anda dapatkan.", 0.03)
                slowprint("Item diacak kembali lokasinya. Cari lagi!", 0.03)
                place_items_randomly()
            time.sleep(1)
            return
# =========================================================

#=============GETCH PLATFORM INDEPENDENT==============#
if os.name == 'nt':
    import msvcrt
    def getch():
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                ch += msvcrt.getwch()
                return ch
            return ch
else:
    import termios, tty, select

    def filter_scroll(ch):
        if ch is None:
            return None
        try:
            if ch.startswith("\x1b[<64") or ch.startswith("\x1b[<65"):
                return None
        except Exception:
            pass
        return ch

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            r, _, _ = select.select([sys.stdin], [], [], 0.01)
            if r:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    r, _, _ = select.select([sys.stdin], [], [], 0.005)
                    if not r:
                        return filter_scroll('\x1b')
                    next1 = sys.stdin.read(1)
                    if not next1:
                        return filter_scroll('\x1b')
                    if next1 == '[':
                        r, _, _ = select.select([sys.stdin], [], [], 0.005)
                        if not r:
                            return filter_scroll('\x1b[')
                        next2 = sys.stdin.read(1)
                        if next2 == '<':
                            buf = ''
                            start = time.time()
                            while True:
                                r2, _, _ = select.select([sys.stdin], [], [], 0.01)
                                if not r2:
                                    if time.time() - start > 0.2:
                                        break
                                    continue
                                c = sys.stdin.read(1)
                                if not c:
                                    break
                                buf += c
                                if c in ('M', 'm'):
                                    break
                            return None
                        seq = '\x1b[' + next2
                        return filter_scroll(seq)
                    return filter_scroll('\x1b' + next1)
                return filter_scroll(ch)
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

#=============TRANSLATE KEY==============#
def translate_key(ch):
    if ch in ('w', 'W'): return (0, -1)
    if ch in ('s', 'S'): return (0, 1)
    if ch in ('a', 'A'): return (-1, 0)
    if ch in ('d', 'D'): return (1, 0)
    if ch == '\x1b[A': return (0, -1)
    if ch == '\x1b[B': return (0, 1)
    if ch == '\x1b[C': return (1, 0)
    if ch == '\x1b[D': return (-1, 0)
    if ch in ('\x00H', '\xe0H'): return (0, -1)
    if ch in ('\x00P', '\xe0P'): return (0, 1)
    if ch in ('\x00M', '\xe0M'): return (1, 0)
    if ch in ('\x00K', '\xe0K'): return (-1, 0)
    return None

#=============RENDER==============#
def render(steps):
    try:
        clear()
    except NameError:
        os.system('cls' if os.name == 'nt' else 'clear')

    item_pos = {(item["x"], item["y"]) for item in items_to_find}

    lines = []
    for y, row in enumerate(maze):
        row_chars = []
        for x, cell in enumerate(row):
            if (x, y) == (player_pos["x"], player_pos["y"]):
                row_chars.append(PLAYER_CHAR)
            elif (x, y) in item_pos:
                row_chars.append(ITEM_CHAR)
            else:
                row_chars.append(cell)
        lines.append(''.join(row_chars))

    items_status = f"Item terkumpul: {len(collected_items)}/{NUM_REQUIRED_ITEMS} ({', '.join(collected_items)})"
    status = f"Langkah: {steps} | Sisa Waktu: {timer_left}s"
    controls = "(WASD / q=keluar)"

    lines.append("-" * WIDTH)
    lines.append(items_status)
    lines.append(status + " " * (WIDTH - len(status) - len(controls)) + controls)

    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

#=============TIMER=================#
def countdown():
    global timer_left, timer_done
    while timer_left > 0 and timer_running and not game_over:
        time.sleep(1)
        timer_left -= 1
    if timer_left <= 0:
        timer_done = True

#=============GAME LOOP (Diperbarui untuk Alt Screen)==============#
def play():
    global timer_running, timer_done, game_over, maze
    timer_running = True
    timer_done = False
    game_over = False

    maze = [list(row) for row in MAZE_TEMPLATE]
    place_items_randomly()

    enable_alt_screen()
    sys.stdout.write("\033[?1000l\033[?1002l\033[?1003l\033[?1006l\033[?1015l")
    sys.stdout.flush()

    threading.Thread(target=countdown, daemon=True).start()

    slowprint("SELAMAT DATANG DI LABIRIN PENCARI HARTA", 0.02)
    slowprint(f"KUMPULKAN {NUM_REQUIRED_ITEMS} ITEM UNTUK MEMBUKA PINTU KELUAR\n", 0.02)
    
    print("\nPERATURAN!!!\n")
    print("Kumpulkan semua item misterius untuk membuka (X) dan Keluar Melalui (E)")
    print("Item Misterius ditandai dengan tanda ? ")
    print("\nPermainan akan dimulai dalam 5 detik.....")
    time.sleep(5)

    steps = 0
    try:
        while True:
            start_loop = time.time()

            if timer_done:
                render(steps)
                slowprint("WAKTU HABIS!! GAME OVER", 0.03)
                timer_running = False
                return "TIMEOUT"
            if game_over:
                render(steps)
                slowprint("ANDA KALAH!", 0.03)
                time.sleep(0.7)
                timer_running = False
                return "LOSE"

            render(steps)
            ch = getch()

            if ch is not None:
                if ch in ('q', 'Q'):
                    timer_running = False
                    return "exit"

                mv = translate_key(ch)
                if mv:
                    dx, dy = mv
                    nx, ny = player_pos["x"] + dx, player_pos["y"] + dy

                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and maze[ny][nx] != WALL:
                        player_pos["x"], player_pos["y"] = nx, ny
                        steps += 1

                        check_item_encounter()

            if len(collected_items) == NUM_REQUIRED_ITEMS:
                if maze[HEIGHT-2][WIDTH-2] == EXIT_LOCKED:
                    maze[HEIGHT-2][WIDTH-2] = EXIT_OPEN
            else:
                maze[HEIGHT-2][WIDTH-2] = EXIT_LOCKED

            if maze[player_pos["y"]][player_pos["x"]] == EXIT_OPEN:
                render(steps)
                slowprint("\n🎉 Semua item terkumpul! Kamu keluar dengan selamat!", 0.03)
                timer_running = False
                return "WIN"

            elapsed = time.time() - start_loop
            time.sleep(max(0.01 - elapsed, 0))
    except Exception:
        return "ERROR"
    finally:
        disable_alt_screen()

#=============MAIN==============#