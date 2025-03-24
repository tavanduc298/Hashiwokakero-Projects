from puzzle_parser import *
from hashi_visualizer import *
from cnf_generator import *
from sat_solver import solve_with_pysat
from a_star_solver import a_star_solver
import os   # Thư viện thao tác với file hệ thống

# Định nghĩa đường dẫn tuyệt đối cho file input
script_dir = os.path.dirname(os.path.abspath(__file__)) # Lấy thư mục chứa script hiện tại
file_path = os.path.join(script_dir, "..", "Inputs", "input1.txt")

# Load dữ liệu từ file
board = load_board_from_file(file_path) # Đọc và phân tích file input
print(" Board layout:")
print_board(board)  # Hiển thị bàn chơi ban đầu (chỉ có các đảo)

# Cho phép người dùng chọn phương pháp giải
print("\n Chọn phương pháp giải:")
print("1.   Giải bằng PySAT (CNF)")
print("2.   Giải bằng A* (Heuristic)")
choice = input(" Nhập lựa chọn (1 hoặc 2): ").strip()

# Xử lý lựa chọn của người dùng
if choice == "1":
    solve_with_pysat(board)
elif choice == "2":
    a_star_solver(board,"solution.cnf")
else:
    print("Lựa chọn không hợp lệ!")
