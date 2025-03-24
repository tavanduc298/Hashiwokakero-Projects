class Island:
    def __init__(self, x, y, required_bridges):
        self.x = x
        self.y = y
        self.required_bridges = required_bridges # Số cầu cần có để hoàn thành đảo
        self.connections = {} # Từ điển lưu các kết nối với các đảo khác

    def clone(self):
        """Tạo một bản sao của đối tượng Island, bao gồm cả các kết nối của nó."""
        # Sử dụng đúng tên thuộc tính `required_bridges` khi tạo bản sao
        new_island = Island(self.x, self.y, self.required_bridges)  # Tạo một đảo mới có cùng tọa độ và số cầu cần thiết
        new_island.connections = self.connections.copy()  # Sao chép danh sách kết nối để tránh ảnh hưởng bản gốc
        return new_island

    def total_bridges(self):
        """Tính tổng số cầu hiện có kết nối với đảo này."""
        return sum(self.connections.values())

    def is_satisfied(self):
        """Kiểm tra xem số cầu hiện tại đã đúng với số cầu yêu cầu hay chưa."""
        return self.total_bridges() == self.required_bridges

class Board:
    def __init__(self, width, height):
        """Khởi tạo bảng chơi với kích thước width x height."""
        self.width = width
        self.height = height
        self.islands = []
        self.island_positions = set()  # Tập hợp lưu vị trí các đảo để tra cứu nhanh
        self.var_map = {}  # Bản đồ biến, có thể dùng cho xử lý logic hoặc binding
        self.reverse_var_map = {}  # Bản đồ biến ngược (để tra cứu ngược)
        self.clauses = []   # Danh sách các ràng buộc (có thể dùng trong xử lý logic)
        self.variable_counter = 1   # Bộ đếm để cấp phát biến mới nếu cần

    def clone(self):
        """Tạo một bản sao của đối tượng Board, bao gồm các đảo và thuộc tính khác."""
        cloned_board = Board(self.width, self.height)

        # Sao chép danh sách các đảo
        cloned_board.islands = []
        for island in self.islands:
            cloned_island = island.clone()  # Sao chép từng đảo bằng phương thức clone của Island
            cloned_board.islands.append(cloned_island)

        # Sao chép các thuộc tính khác
        cloned_board.island_positions = self.island_positions.copy()
        cloned_board.var_map = self.var_map.copy()
        cloned_board.reverse_var_map = self.reverse_var_map.copy()
        cloned_board.clauses = self.clauses.copy()
        cloned_board.variable_counter = self.variable_counter

        return cloned_board

    def add_island(self, x, y, required_bridges):
        """Thêm một đảo vào bảng với tọa độ (x, y) và số cầu yêu cầu."""
        island = Island(x, y, required_bridges) # Tạo đối tượng Island
        self.islands.append(island) # Thêm đảo vào danh sách
        self.island_positions.add((x, y))  # Cập nhật tập hợp vị trí đảo để tra cứu nhanh

    def add_bridge(self, x1, y1, x2, y2, count=1):
        """Thêm cầu giữa hai đảo trên bảng."""
        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)

        if not island1 or not island2:
            print(f"ERROR: ({x1}, {y1}) or ({x2}, {y2}) is not an island!")
            return  

        # Nếu đã có cầu nối giữa hai đảo, tăng số lượng cầu
        if (x2, y2) in island1.connections:
            island1.connections[(x2, y2)] += count
            island2.connections[(x1, y1)] += count
        else:# Nếu chưa có cầu, tạo kết nối mới
            island1.connections[(x2, y2)] = count
            island2.connections[(x1, y1)] = count

    def get_island_at(self, x, y):
        """Tìm và trả về đảo tại tọa độ (x, y), nếu không có trả về None."""
        for island in self.islands:
            if island.x == x and island.y == y:
                return island
        return None

    def can_connect(self, island1, island2):
        """Kiểm tra xem có thể kết nối hai đảo theo luật Hashiwokakero không."""
        if island1.x != island2.x and island1.y != island2.y:
            return False    # Hai đảo không cùng hàng hoặc cùng cột thì không thể nối cầu

        # Kiểm tra có đảo nào chặn đường nối cầu không
        if island1.x == island2.x:
            y_range = range(min(island1.y, island2.y) + 1, max(island1.y, island2.y))
            for y in y_range:
                if (island1.x, y) in self.island_positions:
                    return False    # Có đảo nằm giữa hai điểm => không thể nối
        else:
            x_range = range(min(island1.x, island2.x) + 1, max(island1.x, island2.x))
            for x in x_range:
                if (x, island1.y) in self.island_positions:
                    return False     # Có đảo nằm giữa hai điểm => không thể nối

        return True
    
    def get_possible_bridges(self):
        """Trả về danh sách các cặp đảo có thể kết nối với nhau."""
        possible = []
        for island in self.islands:
            x1, y1 = island.x, island.y

            # Hướng phải
            x = x1 + 1
            while True:
                if (x, y1) in self.island_positions:
                    if not self._is_blocked(x1, y1, x, y1):
                        possible.append(((x1, y1), (x, y1)))
                    break
                if x > max(pos[0] for pos in self.island_positions): break
                x += 1

            # Hướng xuống
            y = y1 + 1
            while True:
                if (x1, y) in self.island_positions:
                    if not self._is_blocked(x1, y1, x1, y):
                        possible.append(((x1, y1), (x1, y)))
                    break
                if y > max(pos[1] for pos in self.island_positions): break
                y += 1

        return possible

    def _is_blocked(self, x1, y1, x2, y2):
        """Kiểm tra xem có đảo nào nằm giữa hai điểm không."""
        for island in self.islands:
            # Bỏ qua hai đầu cầu
            if (island.x, island.y) == (x1, y1) or (island.x, island.y) == (x2, y2):
                continue

            # Nếu cầu dọc, kiểm tra có đảo nằm giữa trên cùng cột
            if x1 == x2 and island.x == x1 and min(y1, y2) < island.y < max(y1, y2):
                return True

            # Nếu cầu ngang, kiểm tra có đảo nằm giữa trên cùng hàng
            if y1 == y2 and island.y == y1 and min(x1, x2) < island.x < max(x1, x2):
                return True

        return False

    def is_valid_bridge(self, current_bridges, new_bridge):
        """Kiểm tra xem cầu mới có hợp lệ không (không trùng và không cắt cầu khác)."""
        x1, y1, x2, y2 = new_bridge

        # Kiểm tra trùng cầu
        if new_bridge in current_bridges or (x2, y2, x1, y1) in current_bridges:
            return False

        for bx1, by1, bx2, by2 in current_bridges:
            if x1 == x2: # Cầu mới là dọc
                if bx1 == bx2:
                    if x1 == bx1 and not (max(y1, y2) < min(by1, by2) or min(y1, y2) > max(by1, by2)):
                        return False  # trùng trục dọc và giao nhau
                elif by1 == by2:
                    if min(bx1, bx2) <= x1 <= max(bx1, bx2) and min(y1, y2) <= by1 <= max(y1, y2):
                        return False  # dọc-ngang cắt nhau
            elif y1 == y2:  # Cầu mới là ngang
                if by1 == by2:
                    if y1 == by1 and not (max(x1, x2) < min(bx1, bx2) or min(x1, x2) > max(bx1, bx2)):
                        return False  # trùng trục ngang và giao nhau
                elif bx1 == bx2:
                    if min(by1, by2) <= y1 <= max(by1, by2) and min(x1, x2) <= bx1 <= max(x1, x2):
                        return False  # ngang-dọc cắt nhau
        return True
    