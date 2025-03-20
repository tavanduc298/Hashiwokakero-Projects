import heapq
from copy import deepcopy
from collections import deque

class HashiState:
    """Đại diện cho một trạng thái trong Hashiwokakero."""
    def __init__(self, grid, bridges, cost):
        self.grid = grid  # Bản đồ hiện tại
        self.bridges = bridges  # Danh sách cầu hiện có (set)
        self.cost = cost  # G(n): Chi phí đi từ đầu đến trạng thái này
        self.heuristic = self.calculate_heuristic()
        self.f_score = self.cost + self.heuristic  # F(n) = G(n) + H(n)
    
    def __lt__(self, other):
        return self.f_score < other.f_score  # So sánh để dùng trong hàng đợi ưu tiên
    
    def calculate_heuristic(self):
        """Hàm heuristic: Đếm tổng số cầu còn thiếu để hoàn thành bài toán."""
        missing_bridges = 0
        
        # Kiểm tra nếu self.grid.islands là list, chuyển đổi thành dict
        if isinstance(self.grid.islands, list):
            if all(hasattr(island, "x") and hasattr(island, "y") and hasattr(island, "num") for island in self.grid.islands):
                self.grid.islands = { (island.x, island.y): island.num for island in self.grid.islands }
            else:
                print("❌ ERROR: Định dạng dữ liệu của grid.islands không hợp lệ!")
                return float('inf')

        for (x, y), num in self.grid.islands.items():
            connected_bridges = sum(1 for (a, b, c, d) in self.bridges if (x, y) in [(a, b), (c, d)])
            missing_bridges += abs(num - connected_bridges)
        
        return missing_bridges

def is_fully_connected(grid, bridges):
    """Kiểm tra xem tất cả các đảo có nằm trong cùng một thành phần liên thông không."""
    islands = list(grid.islands.keys())
    if not islands:
        return False

    if not bridges:
        return len(islands) == 1  

    visited = set()
    queue = deque([islands[0]])  # Bắt đầu BFS từ đảo đầu tiên
    
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        # Thêm các đảo có kết nối với (x, y)
        for (a, b, c, d) in bridges:
            if (x, y) == (a, b) and (c, d) not in visited:
                queue.append((c, d))
            elif (x, y) == (c, d) and (a, b) not in visited:
                queue.append((a, b))
    
    return len(visited) == len(islands)  # Nếu duyệt hết đảo thì đồ thị liên thông

def get_neighbors(state):
    """Sinh ra các trạng thái kế tiếp bằng cách thêm cầu hợp lệ."""
    neighbors = []
    
    # Kiểm tra nếu `get_possible_bridges()` có tồn tại trong grid
    if not hasattr(state.grid, "get_possible_bridges"):
        raise AttributeError("Lớp grid thiếu phương thức get_possible_bridges()")

    for (x1, y1), (x2, y2) in state.grid.get_possible_bridges():
        if ((x1, y1, x2, y2) not in state.bridges) and state.grid.is_valid_bridge(state.bridges, (x1, y1, x2, y2)):
            new_bridges = set(state.bridges)
            new_bridges.add((x1, y1, x2, y2))
            new_state = HashiState(state.grid, new_bridges, state.cost + 1)
            neighbors.append(new_state)
    return neighbors

def a_star_solver(grid):
    """Giải Hashiwokakero bằng thuật toán A*."""

    # Debug: Kiểm tra kiểu dữ liệu của grid.islands
    print("DEBUG: Type of grid.islands =", type(grid.islands))
    print("DEBUG: Content of grid.islands =", grid.islands)

    # Nếu grid.islands không phải dictionary, thử chuyển đổi
    if isinstance(grid.islands, list):
        if all(hasattr(island, "x") and hasattr(island, "y") and hasattr(island, "num") for island in grid.islands):
            grid.islands = { (island.x, island.y): island.num for island in grid.islands }
        else:
            print("❌ ERROR: Định dạng dữ liệu của grid.islands không hợp lệ!")
            return None

    # Khởi tạo trạng thái ban đầu
    initial_state = HashiState(grid, set(), 0)

    open_set = []
    heapq.heappush(open_set, initial_state)
    visited = set()
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if current.heuristic == 0 and is_fully_connected(grid, current.bridges):
            return current.bridges  # Tìm thấy lời giải
        
        visited.add(frozenset(current.bridges))

        for neighbor in get_neighbors(current):
            if frozenset(neighbor.bridges) not in visited:
                heapq.heappush(open_set, neighbor)
    
    return None  # Không tìm thấy lời giải

if __name__ == "__main__":
    from puzzle_parser import Puzzle  # Giả sử Puzzle là lớp xử lý đầu vào
    puzzle = Puzzle("data/puzzles/puzzle1.txt")

    print("DEBUG: Type of puzzle.islands =", type(puzzle.islands))

    solution = a_star_solver(puzzle)
    
    if solution:
        print("✅ Lời giải tìm thấy:")
        for bridge in solution:
            print(bridge)
    else:
        print("❌ Không tìm thấy lời giải!")
