from pysat.formula import CNF
from pysat.solvers import Glucose3
import pickle
from hashi_visualizer import write_output_map
from cnf_generator import export_cnf

def solve_with_pysat(board):
    """
    Giải bài toán Hashi bằng PySAT (SAT Solver).
    
    :param board: Đối tượng Board chứa thông tin về bản đồ và các đảo.
    """
    # Xuất công thức CNF ra file "solution.cnf"
    export_cnf(board, "solution.cnf")

    # Đọc lại công thức CNF từ file
    cnf = CNF(from_file="solution.cnf")
    
    # Khởi tạo bộ giải SAT Glucose3
    solver = Glucose3()

    # Nạp công thức CNF vào bộ giải 
    solver.append_formula(cnf.clauses)

    # Kiểm tra xem bài toán có lời giải hay không
    if solver.solve():
        # Lấy mô hình lời giải (danh sách biến được gán giá trị TRUE)
        model = solver.get_model()

        # Chỉ lấy các biến dương (được chọn trong lời giải)
        selected_vars = [var for var in model if var > 0]
        print(" Các biến được chọn (selected_vars):", selected_vars)

        # Nạp bản đồ ánh xạ từ biến CNF về cặp đảo + số cầu từ file "Reverse_map.pkl"
        with open("Reverse_map.pkl", "rb") as f:
            reverse_map = pickle.load(f)

        # Hiển thị danh sách các cầu được tạo
        for var in selected_vars:
            if var in reverse_map:
                island1, island2, bridge_num = reverse_map[var] # Lấy thông tin từ biến CNF
                x1, y1 = island1
                x2, y2 = island2
                print(f"{x1},{y1} <-> {x2},{y2} : {bridge_num} bridge(s)")

        write_output_map(board, model, board.width, board.height)
        print(" Đã ghi kết quả vào output.txt")
    else:
        print(" Không có lời giải (UNSAT)")
