class Island:
    def __init__(self, x, y, required_bridges):
        self.x = x
        self.y = y
        self.required_bridges = required_bridges
        self.connections = {}

    def clone(self):
        """Create a copy of the Island object, including its connections."""
        # Use required_bridges instead of bridges_needed (since that's the correct attribute name)
        new_island = Island(self.x, self.y, self.required_bridges)  # Properly pass `required_bridges`
        new_island.connections = self.connections.copy()  # Copy the connections dictionary
        return new_island

    def total_bridges(self):
        return sum(self.connections.values())

    def is_satisfied(self):
        return self.total_bridges() == self.required_bridges

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.islands = []
        self.island_positions = set()  # Thêm tập hợp lưu vị trí các đảo
        self.var_map = {}  
        self.reverse_var_map = {}  
        self.clauses = []
        self.variable_counter = 1

    def clone(self):
        """Create a copy of the Board object, including its islands and other attributes."""
        # Create a new Board instance with the same width and height
        cloned_board = Board(self.width, self.height)

        # Manually copy the list of islands
        cloned_board.islands = []
        for island in self.islands:
            cloned_island = island.clone()  # Call the clone method for each island
            cloned_board.islands.append(cloned_island)

        # Manually copy other attributes
        cloned_board.island_positions = self.island_positions.copy()  # Copy the set of island positions
        cloned_board.var_map = self.var_map.copy()  # Copy the var_map dictionary
        cloned_board.reverse_var_map = self.reverse_var_map.copy()  # Copy the reverse_var_map dictionary
        cloned_board.clauses = self.clauses.copy()  # Copy the clauses list
        cloned_board.variable_counter = self.variable_counter  # Copy the variable_counter

        return cloned_board

    def add_island(self, x, y, required_bridges):
        island = Island(x, y, required_bridges)
        self.islands.append(island)
        self.island_positions.add((x, y))  # Cập nhật danh sách vị trí đảo

    def add_bridge(self, x1, y1, x2, y2, count=1):
        """Thêm cầu giữa hai đảo trên bảng."""
        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)

        if not island1 or not island2:
            print(f"❌ ERROR: ({x1}, {y1}) or ({x2}, {y2}) is not an island!")
            return  

        # Kiểm tra xem đã có cầu chưa
        if (x2, y2) in island1.connections:
            island1.connections[(x2, y2)] += count
            island2.connections[(x1, y1)] += count
        else:
            island1.connections[(x2, y2)] = count
            island2.connections[(x1, y1)] = count

    def get_island_at(self, x, y):
        for island in self.islands:
            if island.x == x and island.y == y:
                return island
        return None

    def can_connect(self, island1, island2):
        if island1.x != island2.x and island1.y != island2.y:
            return False

        if island1.x == island2.x:
            y_range = range(min(island1.y, island2.y) + 1, max(island1.y, island2.y))
            for y in y_range:
                if (island1.x, y) in self.island_positions:
                    return False
        else:
            x_range = range(min(island1.x, island2.x) + 1, max(island1.x, island2.x))
            for x in x_range:
                if (x, island1.y) in self.island_positions:
                    return False

        return True
    
    def get_possible_bridges(self):
        """Trả về tất cả các cặp đảo có thể nối được với nhau theo luật Hashi (gần nhất theo 4 hướng, không vướng đảo khác)."""
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
        x1, y1, x2, y2 = new_bridge

        # Cầu trùng
        if new_bridge in current_bridges or (x2, y2, x1, y1) in current_bridges:
            return False

        for bx1, by1, bx2, by2 in current_bridges:
            # Cầu mới là dọc
            if x1 == x2:
                if bx1 == bx2:
                    if x1 == bx1 and not (max(y1, y2) < min(by1, by2) or min(y1, y2) > max(by1, by2)):
                        return False  # trùng trục dọc và giao nhau
                elif by1 == by2:
                    if min(bx1, bx2) <= x1 <= max(bx1, bx2) and min(y1, y2) <= by1 <= max(y1, y2):
                        return False  # dọc-ngang cắt nhau
            # Cầu mới là ngang
            elif y1 == y2:
                if by1 == by2:
                    if y1 == by1 and not (max(x1, x2) < min(bx1, bx2) or min(x1, x2) > max(bx1, bx2)):
                        return False  # trùng trục ngang và giao nhau
                elif bx1 == bx2:
                    if min(by1, by2) <= y1 <= max(by1, by2) and min(x1, x2) <= bx1 <= max(x1, x2):
                        return False  # ngang-dọc cắt nhau
        return True
    