import heapq
import sys
from copy import deepcopy
from collections import defaultdict
from _init_ import *
from puzzle_parser import *
from hashi_visualizer import *
from cnf_generator import *

class HashiState:
    def __init__(self, board, bridges, cost):
        """
        Khởi tạo một trạng thái của bài toán.
        - board: Bản đồ hiện tại
        - bridges: Dictionary lưu số cầu giữa các đảo {(x1, y1, x2, y2): count}
        - cost: Chi phí từ trạng thái ban đầu đến trạng thái hiện tại
        """
        self.board = board
        self.bridges = bridges  # {(x1, y1, x2, y2): count}
        self.cost = cost
        self.heuristic = self.calculate_heuristic() # Tính toán giá trị heuristic

    def calculate_heuristic(self):
        """
        Tính toán heuristic dựa trên tổng số cầu còn thiếu và số đảo bị cô lập.
        """
        total_missing = 0
        for island in self.board.islands:
            connected = sum(island.connections.values())    # Số cầu đã kết nối
            missing = max(0, island.required_bridges - connected)   # Cầu còn thiếu

            # Đánh giá khoảng cách đến trung tâm để ưu tiên giải quyết các đảo cô lập
            distance_score = abs(island.x - self.board.width // 2) + abs(island.y - self.board.height // 2)

            total_missing += missing + distance_score * 0.2  # Hệ số 0.2 có thể tinh chỉnh
        # Đếm số đảo chưa có kết nối nào
        num_disconnected = sum(1 for island in self.board.islands if not island.connections)
        return total_missing + 5 * num_disconnected # Ưu tiên giảm số đảo bị cô lập

    def is_goal(self):
        """
        Kiểm tra xem trạng thái hiện tại có phải là nghiệm hay không (tất cả đảo có đủ số cầu yêu cầu).
        """
        for island in self.board.islands:
            connected = sum(island.connections.values())
            if connected != island.required_bridges:
                return False
        return True

    def __lt__(self, other):
        """So sánh ưu tiên giữa hai trạng thái trong hàng đợi ưu tiên."""
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)
    
    def __eq__(self, other):
        """Hai trạng thái được xem là bằng nhau nếu danh sách cầu giống nhau."""
        return isinstance(other, HashiState) and self.bridges == other.bridges
    
    def __hash__(self):
        """Hàm băm để sử dụng trong tập visited, giúp tránh lặp lại trạng thái."""
        normalized_bridges = frozenset(
            (tuple(sorted([(x1, y1), (x2, y2)])), count) 
            for (x1, y1, x2, y2), count in self.bridges.items()
        )
        return hash(normalized_bridges)

def decode_var(var, board):
    """Giải mã biến CNF thành một cầu (x1, y1, x2, y2, n)."""
    for key, value in board.var_map.items():
        if value == var:
            (x1, y1), (x2, y2), n = key  # Giải mã đúng định dạng
            return x1, y1, x2, y2, n  # Trả về tuple 5 giá trị
    return None

def parse_cnf_file(cnf_path, board):
    """Trích xuất các cầu hợp lệ từ tệp lời giải CNF."""
    valid_bridges = set()

    with open(cnf_path, "r") as file:
        for line in file:
            if line.startswith("c") or line.startswith("p"):  
                continue  # Bỏ qua dòng chú thích hoặc khai báo vấn đề

            vars = list(map(int, line.strip().split()))[:-1] # Loại bỏ số 0 cuối dòng

            for var in vars:
                if var > 0:
                    bridge = decode_var(var, board)
                    if bridge is not None:
                        valid_bridges.add(bridge)

    return valid_bridges

def get_neighbors(state, valid_bridges, visited_states):
    """
    Sinh các trạng thái con từ trạng thái hiện tại bằng cách thêm cầu hợp lệ.
    """
    neighbors = []

    for (x1, y1, x2, y2, max_n) in valid_bridges:
        # Kiểm tra tọa độ hợp lệ
        if (x1, y1) not in state.board.island_positions or (x2, y2) not in state.board.island_positions:
            continue
        if state.board._is_blocked(x1, y1, x2, y2):
            continue

        # Lấy số cầu hiện có giữa hai đảo
        bridge_count = state.bridges.get((x1, y1, x2, y2), 0)
        if bridge_count >= max_n:
            continue

        # Tạo trạng thái mới
        new_count = bridge_count + 1
        new_board = state.board.clone()
        new_bridges = state.bridges.copy()
        new_bridges[(x1, y1, x2, y2)] = new_count

        new_board.add_bridge(x1, y1, x2, y2, count=1)  # Thêm 1 cầu

        # Kiểm tra tránh trùng lặp trạng thái
        state_signature = tuple(sorted(new_bridges.items()))
        if state_signature in visited_states:
            continue
        visited_states[state_signature] = True

        new_state = HashiState(new_board, new_bridges, state.cost + 1)
        neighbors.append(new_state)

    return neighbors

def a_star_solver(board, cnf_path):
    """Giải bài toán Hashiwokakero sử dụng thuật toán A* với ràng buộc từ CNF."""
    export_cnf(board, "solution.cnf")   # Xuất ràng buộc CNF từ board
    load_reverse_map(board) # Tải bản đồ biến đảo ngược
    valid_bridges = parse_cnf_file(cnf_path, board) # Trích xuất cầu hợp lệ
    print("Valid Bridges:", sorted(valid_bridges))  # Hiển thị các cầu hợp lệ

    for island in board.islands:
        connected = sum(island.connections.values())
        print(f"Island at ({island.x}, {island.y}) needs {island.required_bridges} bridges, currently {connected}.")

    if not valid_bridges:
        return None

    initial_state = HashiState(board, {}, 0)
    open_set = []
    heapq.heappush(open_set, initial_state)  # Thêm trạng thái ban đầu vào hàng đợi ưu tiên
    visited = set()

    steps = 0   # Đếm số bước duyệt

    while open_set:
        current = heapq.heappop(open_set)   # Lấy trạng thái tốt nhất ra
        steps += 1

        if current.is_goal():
            print(f"Solution found in {steps} steps")

            with open("output.txt", "w", encoding="utf-8") as f:
                original_stdout = sys.stdout
                sys.stdout = f
                print_board_with_bridges(board, current.bridges)    # Xuất kết quả vào file
                sys.stdout = original_stdout   # Khôi phục stdout

            print("Đã ghi kết quả vào output.txt")
            return current.bridges

        state_signature = frozenset(current.bridges.items())
        if state_signature in visited:
            continue
        visited.add(state_signature)

        neighbors = get_neighbors(current, valid_bridges, visited_states={})
        for neighbor in neighbors:
            heapq.heappush(open_set, neighbor)  # Đưa trạng thái mới vào hàng đợi

    print("No solution found")
    return None
