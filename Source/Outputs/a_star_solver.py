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
        self.board = board
        self.bridges = bridges  # {(x1, y1, x2, y2): count}
        self.cost = cost
        self.heuristic = self.calculate_heuristic()

    def calculate_heuristic(self):
        total_missing = 0
        for island in self.board.islands:
            connected = sum(island.connections.values())
            missing = max(0, island.required_bridges - connected)

            # Ưu tiên đảo cô lập và xa trung tâm (dễ bị kẹt)
            distance_score = abs(island.x - self.board.width // 2) + abs(island.y - self.board.height // 2)

            total_missing += missing + distance_score * 0.2  # Hệ số có thể tinh chỉnh

        num_disconnected = sum(1 for island in self.board.islands if not island.connections)
        return total_missing + 5 * num_disconnected

    def is_goal(self):
        """Check if the puzzle is fully solved (all islands have required bridges)."""
        for island in self.board.islands:
            connected = sum(island.connections.values())
            if connected != island.required_bridges:
                return False
        return True

    def __lt__(self, other):
        """Priority queue comparison: prioritize lower (cost + heuristic)."""
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)
    
    def __eq__(self, other):
        return isinstance(other, HashiState) and self.bridges == other.bridges
    
    def __hash__(self):
        """Consistent hashing for visited states."""
        normalized_bridges = frozenset(
            (tuple(sorted([(x1, y1), (x2, y2)])), count) 
            for (x1, y1, x2, y2), count in self.bridges.items()
        )
        return hash(normalized_bridges)

def decode_var(var, board):
    """Decode CNF variable into a bridge (x1, y1, x2, y2, n)."""
    for key, value in board.var_map.items():
        if value == var:
            (x1, y1), (x2, y2), n = key  # Unpack đúng định dạng
            return x1, y1, x2, y2, n  # Trả về tuple 5 giá trị
    return None

def parse_cnf_file(cnf_path, board):
    """Extract valid bridges from a CNF solution file."""
    valid_bridges = set()

    with open(cnf_path, "r") as file:
        for line in file:
            if line.startswith("c") or line.startswith("p"):  
                continue  # Skip comments and problem definition

            vars = list(map(int, line.strip().split()))[:-1]  # Remove trailing 0

            for var in vars:
                if var > 0:
                    bridge = decode_var(var, board)
                    if bridge is not None:  # ✅ Fix: Kiểm tra tránh lỗi TypeError
                        valid_bridges.add(bridge)

    return valid_bridges

def get_neighbors(state, valid_bridges, visited_states):
    neighbors = []

    for (x1, y1, x2, y2, max_n) in valid_bridges:
        if (x1, y1) not in state.board.island_positions or (x2, y2) not in state.board.island_positions:
            continue
        if state.board._is_blocked(x1, y1, x2, y2):
            continue

        bridge_count = state.bridges.get((x1, y1, x2, y2), 0)
        if bridge_count >= max_n:
            continue

        new_count = bridge_count + 1
        new_board = state.board.clone()
        new_bridges = state.bridges.copy()
        new_bridges[(x1, y1, x2, y2)] = new_count

        new_board.add_bridge(x1, y1, x2, y2, count=1)  # ✅ Chỉ cộng thêm 1 cầu

        state_signature = tuple(sorted(new_bridges.items()))
        if state_signature in visited_states:
            continue
        visited_states[state_signature] = True

        new_state = HashiState(new_board, new_bridges, state.cost + 1)
        neighbors.append(new_state)

    return neighbors

def a_star_solver(board, cnf_path):
    """Solve Hashiwokakero using A* search with CNF constraints."""
    export_cnf(board, "solution.cnf")
    load_reverse_map(board)
    valid_bridges = parse_cnf_file(cnf_path, board)
    print("Valid Bridges:", sorted(valid_bridges))  # ✅ Sorted for better readability

    for island in board.islands:
        connected = sum(island.connections.values())
        print(f"Island at ({island.x}, {island.y}) needs {island.required_bridges} bridges, currently {connected}.")

    if not valid_bridges:
        return None

    initial_state = HashiState(board, {}, 0)
    open_set = []
    heapq.heappush(open_set, initial_state)  # ✅ Push trực tiếp HashiState (nhờ đã override __lt__)
    visited = set()

    steps = 0

    while open_set:
        current = heapq.heappop(open_set)
        steps += 1

        if current.is_goal():
            print(f"✅ Solution found in {steps} steps")

            with open("output.txt", "w", encoding="utf-8") as f:
                original_stdout = sys.stdout
                sys.stdout = f
                print_board_with_bridges(board, current.bridges)
                sys.stdout = original_stdout  # Restore stdout sau khi ghi file

            print("✅ Đã ghi kết quả vào output.txt")
            return current.bridges

        state_signature = frozenset(current.bridges.items())
        if state_signature in visited:
            continue
        visited.add(state_signature)

        neighbors = get_neighbors(current, valid_bridges, visited_states={})
        for neighbor in neighbors:
            heapq.heappush(open_set, neighbor)

    print("❌ No solution found")
    return None
