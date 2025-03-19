from src._init_ import *
from src.puzzle_parser import *
from src.hashi_visualizer import *
from src.cnf_generator import *
from pysat.formula import CNF
from pysat.solvers import Glucose3
import pickle

# --- MAIN ---
board = load_board_from_file("Data\\puzzles\\puzzles1.txt")
print("📍 Board layout:")
print_board(board)

# Xuất CNF tự động
export_cnf(board,"Data\\solutions\\solution.cnf")

# Đọc lại CNF từ file
cnf = CNF(from_file="Data\\solutions\\solution.cnf")

# Giải CNF bằng Glucose3
solver = Glucose3()
solver.append_formula(cnf.clauses)

if solver.solve():
    model = solver.get_model()

    # Lọc các biến dương (tức là các cầu được chọn)
    selected_vars = [var for var in model if var > 0]

    # In ra danh sách biến được chọn
    print("✅ Các biến được chọn (selected_vars):", selected_vars)

    # Đọc reverse map (từ biến → thông tin cầu nối)
    import pickle
    with open("Data\\solutions\\Reverse_map.pkl", "rb") as f:
        reverse_map = pickle.load(f)

    # In thử nội dung reverse_map để kiểm tra
    print("📂 Nội dung reverse_map (ví dụ vài phần tử):")
    for i, (key, val) in enumerate(reverse_map.items()):
        print(f"  Var {key} -> {val}")
        if i >= 4: break  # In thử 5 phần tử đầu tiên

    for var in selected_vars:
        if var in reverse_map:
            island1, island2, bridge_num = reverse_map[var]
            x1, y1 = island1
            x2, y2 = island2
            line = f"{x1},{y1} <-> {x2},{y2} : {bridge_num} bridge(s)"
            print(line + "\n")
        else:
            print(f"⚠️ Không tìm thấy var={var} trong reverse_map")

    # Xây dựng bản đồ từ model
    write_output_map(board,model, board.width, board.height)
    print("✅ Đã ghi kết quả vào output.txt")
else:
    print("❌ Không có lời giải (UNSAT)")