#========Library===========#
import os
import sys
import time
from textwrap import fill
import lvl1
import lvl2
import lvl3

#========Library===========#

#==========SISTEM============#

def slowprint(text, delay=0.1, newline=True):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()
    
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    
#==========SISTEM============#

#========Awal Opening==========#

clear()

print("========================================")

print(" Selamat datang di Dunia Labyrinth  🎉🎉🎉")

print("========================================")

def opening():
    while True:

        slowprint(" WARNING!!!! : ", 0.08)
        slowprint("\nGame ini dibuat dengan tujuan melatih ketelitian dan alur pemecahan masalah yang anda miliki\n", 0.04)
        slowprint("Game ini memiliki 3 Jenis Labyrinth, yang masing masing Labyrinth memiliki kesulitan tersendiri",0.03)

        text1 = "Labyrinth ini merupakan labyrinth dimana untuk dapat keluar anda harus berpetualang mengumpulkan 5 item makanan misterius dengan memecahkan teka teki yang ada, anda harus mengumpulkan 5 item untuk dapat keluar dari labyrinth ini"
        slowprint(f"\n[1] Labyrinth Pencari Harta : {fill(text1, 50)}", 0.02)

        text2 = "Labyrinth ini merupakan labyrinth yang ditingkatkan. Dimana musuh menyerbu kota anda, anda harus mengalahkan semua musuh yang ada untuk dapat membuka sebuah pintu keluar. Musuh dapat anda kalahkan dengan menjawab pertanyaan dengan benar, namun jika anda salah menjawab maka GAME OVER. Kalahkan semua musuh dan lindungi Kota mu!!!"
        slowprint(f"\n[2] Labyrinth Grilya : {fill(text2, 50)}", 0.02)

        text3 = "Labyrinth ini merupakan tingkat tersulit, dimana anda harus mencari jalan keluar asli yang tercampur dengan jalan keluar palsu, jalan keluar palsu adalah yang dijaga oleh guardian pertanyaan, Dimana jika anda salah Menjawab maka GAME OVER"
        slowprint(f"\n[3] Labyrinth Tantangan : {fill(text3, 50)}", 0.02)

        slowprint("\n*******HARAP MEMBACA SEMUA TEKS YANG ADA SEBELUM MEMAINKAN GAME INI*******", 0.03)
        
        print()
        pilihan = input("\n Apakah anda sudah memahami semua teks yang ada? (Y/T): ").strip().upper()
        
        if pilihan == "Y":
            slowprint("\nBagus Mari kita Mulai Permainan...", 0.05)
            time.sleep(0.5)
            break
        elif pilihan == "T":
            slowprint("\nBaik saya akan ulangi Penjelasannya...\n")
            time.sleep(1)
        else:
            slowprint("\nMasukkan hanya Y/T saja, jangan huruf lain")
            time.sleep(1)
            return
            
opening()
clear()

#=============End Opening==============#

#=============Pilihan===================#

def lose_menu():
    while True:
        clear()
        print("\n ========GAME OVER, ANDA DIKALAHKAN OLEH WAKTU========  ")
        print("\n[1]. Ulangi stage ini ")
        print("[2]. Kembali ke menu stage ")
        print("[3]. Keluar Permainan\n")
        try:
            pilih = int(input("Pilih opsi (1-3) : ").strip())
        except ValueError:
            print("MASUKKAN ANGKA YANG VALID")
        
        if pilih == int(1):
            return "replay"
        elif pilih == int(2):
            clear()
            return "menu"
        elif pilih == int(3):
            return "exit"
        else:
            print("MASUKKAN ANGKA YANG VALID")
            
            
def lose():
    while True:
        clear()
        print("\n ========GAME OVER, ANDA KALAH========  ")
        print("\n[1]. Ulangi stage ini ")
        print("[2]. Kembali ke menu stage ")
        print("[3]. Keluar Permainan\n")
        try:
            pilih = int(input("Pilih opsi (1-3) : ").strip())
        except ValueError:
            print("MASUKKAN ANGKA YANG VALID")
        
        if pilih == int(1):
            return "replay"
        elif pilih == int(2):
            clear()
            return "menu"
        elif pilih == int(3):
            return "exit"
        else:
            print("MASUKKAN ANGKA YANG VALID")
#=============end==============#

def win_menu():
    while True:
        clear()
        print("\n ==========SELAMAT ANDA BERHASIL MEMENANGKAN PERMAINAN========== ")
        print("\n[1]. Ulangi stage ini ")
        print("[2]. Kembali ke menu stage ")
        print("[3]. Keluar Permainan\n")
        try:
            pilih = int(input("Pilih opsi (1-3) : ").strip())
        except ValueError:
            print("MASUKKAN ANGKA YANG VALID")
        
        if pilih == int(1):
            return "replay"
        elif pilih == int(2):
            return "menu"
        elif pilih == int(3):
            return "exit"
        else:
            print("MASUKKAN ANGKA YANG VALID")
            
#=============end==============#
            
def level(play_func, reset_func=None):
    while True:
        if reset_func:
            reset_func()    
        status = play_func()
        
        if status == "exit":
            print("Kembali ke menu stage labyrinth...")
            time.sleep(0.7)
            clear()
            return
        
        if status == "WIN":
            clear()
            aksi = win_menu()
            
            if aksi == "replay":
                continue
            elif aksi == "menu":
                return
            elif aksi == "exit":
                slowprint("Terimakasih Telah Bermain, Pengalaman anda hal yang utama bagi kami", 0.04)
                slowprint("Kami tunggu kedatangan anda kembali ~R.E")
                exit()
            else:
                print("Error Data tidak Valid...")
                time.sleep(1)
                return
            
        elif status == "TIMEOUT":
            clear()
            aksi = lose_menu()
            
            if aksi == "replay":
                continue
            elif aksi == "menu":
                return
            elif aksi == "exit":
                slowprint("Terimakasih Telah Bermain, Pengalaman anda hal yang utama bagi kami", 0.04)
                slowprint("Tertanda ~R.E")
                exit()
            else:
                print("Error Data tidak Valid...")
                time.sleep(1)
                return
            
        elif status == "LOSE":
            clear()
            aksi = lose()
            
            if aksi == "replay":
                continue
            elif aksi == "menu":
                return
            elif aksi == "exit":
                slowprint("Terimakasih Telah Bermain, Pengalaman anda hal yang utama bagi kami", 0.04)
                slowprint("Tertanda ~R.E")
                exit()
            else:
                print("Error Data tidak Valid...")
                time.sleep(1)
                return
        
        

def main():
    while True:
        clear()
        
        print("======================")
        print("\n[1]. Labyrinth Pencari Harta")
        print("[2]. Labyrinth Grilya")
        print("[3]. Labyrinth Tantangan")
        print("[4]. Keluar Permainan\n")
        print("======================\n")
        
        try:
            pilih = int(input("Silahkan Masukkan Nomor yang anda pilih : "))
        except ValueError:
            print("MASUKKAN HANYA BERUPA ANGKA 1/2/3.")
            continue 
        except (EOFError, KeyboardInterrupt):
            print("\nKeluar dari game...")
            break
        
        if pilih == 1:
            clear()
            level(lvl1.play)           
                        
        elif pilih == 2:
            clear()
            level(lvl2.play)
            
        elif pilih == 3:
            clear()
            level(lvl3.play)
            
        elif pilih == 4:
            clear()
            print("Keluar Permainan...")
            slowprint("Terimaksih Telah Memainkan Game Kami, ~R.E")
            slowprint("Kunjungi GitHub Kami RE-Hive ", 0.08)
            time.sleep(1.5)
            break
            
        else:
            print("Masukkan angka yang valid....")
            time.sleep(0.7)
            
if __name__ == '__main__':
            main()
