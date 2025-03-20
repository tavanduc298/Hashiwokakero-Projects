from pysat.formula import CNF
from pysat.solvers import Glucose3
import pickle
from hashi_visualizer import write_output_map
from cnf_generator import export_cnf

def solve_with_pysat(board):
    export_cnf(board, "solution.cnf")

    cnf = CNF(from_file="solution.cnf")
    solver = Glucose3()
    solver.append_formula(cnf.clauses)

    if solver.solve():
        model = solver.get_model()
        selected_vars = [var for var in model if var > 0]
        print("✅ Các biến được chọn (selected_vars):", selected_vars)

        with open("Reverse_map.pkl", "rb") as f:
            reverse_map = pickle.load(f)

        for var in selected_vars:
            if var in reverse_map:
                island1, island2, bridge_num = reverse_map[var]
                x1, y1 = island1
                x2, y2 = island2
                print(f"{x1},{y1} <-> {x2},{y2} : {bridge_num} bridge(s)")

        write_output_map(board, model, board.width, board.height)
        print("✅ Đã ghi kết quả vào output.txt")
    else:
        print("❌ Không có lời giải (UNSAT)")
