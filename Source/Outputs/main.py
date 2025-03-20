from puzzle_parser import *
from hashi_visualizer import *
from cnf_generator import *
from sat_solver import solve_with_pysat
from a_star_solver import a_star_solver
# --- MENU ---
def main():
    board = load_board_from_file("D:\\study\\ttnt\\New folder\\Source\\Inputs\\input1.txt")
    print("📍 Board layout:")
    print_board(board)

    print("\n🔹 Chọn phương pháp giải:")
    print("1️⃣ Giải bằng PySAT (CNF)")
    print("2️⃣ Giải bằng A* (Heuristic)")
    choice = input("👉 Nhập lựa chọn (1 hoặc 2): ").strip()

    if choice == "1":
        solve_with_pysat(board)
    elif choice == "2":
        a_star_solver(board)
    else:
        print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
