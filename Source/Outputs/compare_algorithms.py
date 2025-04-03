import time
from a_star_solver import a_star_solver
from backtracking_solver import backtracking
from brute_force_solver import solve_brute_force  # Import giải pháp brute-force

def compare_algorithms(board):
    """So sánh thời gian chạy của A*, Backtracking và Brute-force."""
    print("\nĐang so sánh các thuật toán...")

    # Chạy A*
    board_copy = board.clone()
    start_time = time.time()
    a_star_solver(board_copy, "solution.cnf")
    a_star_time = time.time() - start_time
    print(f"\nA* hoàn thành trong {a_star_time:.4f} giây.")

    # Chạy Backtracking
    board_copy = board.clone()
    start_time = time.time()
    backtracking(board_copy)
    backtracking_time = time.time() - start_time
    print(f"\nBacktracking hoàn thành trong {backtracking_time:.4f} giây.")

    # Chạy Brute-force
    board_copy = board.clone()
    start_time = time.time()
    solve_brute_force(board_copy)
    brute_force_time = time.time() - start_time
    print(f"\nBrute-force hoàn thành trong {brute_force_time:.4f} giây.")

    # So sánh kết quả
    best_time = min(a_star_time, backtracking_time, brute_force_time)
    print("\n🆚 Kết quả so sánh:")
    if best_time == a_star_time:
        print("🔹 A* nhanh nhất.")
    elif best_time == backtracking_time:
        print("🔹 Backtracking nhanh nhất.")
    else:
        print("🔹 Brute-force nhanh nhất.")

    print(f"⏳ Thời gian: A* = {a_star_time:.4f}s, Backtracking = {backtracking_time:.4f}s, Brute-force = {brute_force_time:.4f}s.")
