class Island:
    def __init__(self, x, y, required_bridges):
        self.x = x
        self.y = y
        self.required_bridges = required_bridges # Số cầu cần có để hoàn thành đảo
        self.connections = {} # Từ điển lưu các kết nối với các đảo khác
    
    def total_bridges(self):
        return self.current_bridges  # Đảm bảo phương thức này tồn tại


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

    def get_all_bridges(self):
        """Trả về tất cả các cầu giữa các đảo trong bảng."""
        bridges = []
        for island in self.islands:
            for (x2, y2), count in island.connections.items():
                # Chỉ thêm cầu vào danh sách nếu nó chưa tồn tại, tránh trùng lặp
                if (x2, y2) > (island.x, island.y):  # Đảm bảo không thêm trùng cầu đã được thêm trước
                    bridges.append(((island.x, island.y), (x2, y2), count))
        return bridges

    def get_bridge_variable(self, bridge):
        """Trả về biến liên quan đến cầu từ var_map, nếu không có thì tạo mới."""
        if bridge not in self.var_map:
            self.var_map[bridge] = self.variable_counter
            self.reverse_var_map[self.variable_counter] = bridge
            self.variable_counter += 1
        return self.var_map[bridge]
    
    def get_bridge_count(self, bridge):
        """Trả về số lượng cầu hiện tại giữa hai đảo."""
        (x1, y1), (x2, y2) = bridge

        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)

        if not island1 or not island2:
            return 0  # Nếu một trong hai không phải đảo, không có cầu

        return island1.connections.get((x2, y2), 0)

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

    def remove_bridge(self, x1, y1, x2, y2, count=1):
        """Remove a specified number of bridges between two islands."""
        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)

        if not island1 or not island2:
            print(f"ERROR: ({x1}, {y1}) or ({x2}, {y2}) is not an island!")
            return

        if (x2, y2) in island1.connections:
            island1.connections[(x2, y2)] -= count
            island2.connections[(x1, y1)] -= count

            if island1.connections[(x2, y2)] <= 0:
                del island1.connections[(x2, y2)]
                del island2.connections[(x1, y1)]

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

    def can_add_bridge(self, x1, y1, x2, y2, count=1):
        """Check if it's possible to add a bridge between two points."""
        # Get islands at both endpoints
        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)
        
        if not island1 or not island2:
            return False

        # Check if adding more bridges would exceed the required number
        current_bridges1 = island1.total_bridges()
        current_bridges2 = island2.total_bridges()
        
        if (current_bridges1 + count > island1.required_bridges or 
            current_bridges2 + count > island2.required_bridges):
            return False

        # Check if there's a path between islands
        if not self.can_connect(island1, island2):
            return False

        # Check if adding this bridge would cross any existing bridges
        bridge_points = [(x1, y1), (x2, y2)]
        for existing_bridge in self.get_all_bridges():
            if self._bridges_cross(bridge_points, [existing_bridge[0], existing_bridge[1]]):
                return False

        return True

    def _bridges_cross(self, bridge1, bridge2):
        """Helper method to check if two bridges cross each other."""
        (x1, y1), (x2, y2) = bridge1
        (x3, y3), (x4, y4) = bridge2

        # Check if bridges are parallel
        if (x1 == x2 and x3 == x4) or (y1 == y2 and y3 == y4):
            return False

        # Check if one bridge is vertical and other is horizontal
        if x1 == x2:  # bridge1 is vertical
            if y3 == y4:  # bridge2 is horizontal
                # Check if they intersect
                return (min(x3, x4) < x1 < max(x3, x4) and 
                        min(y1, y2) < y3 < max(y1, y2))
        else:  # bridge1 is horizontal
            if x3 == x4:  # bridge2 is vertical
                # Check if they intersect
                return (min(x1, x2) < x3 < max(x1, x2) and 
                        min(y3, y4) < y1 < max(y3, y4))
        
        return False

    def is_bridge_valid(self, x1, y1, x2, y2, count=1):
        """Check if adding a bridge would create a valid state."""
        # Check if islands exist
        island1 = self.get_island_at(x1, y1)
        island2 = self.get_island_at(x2, y2)
        
        if not island1 or not island2:
            return False
            
        # Check bridge count limits
        current1 = island1.total_bridges()
        current2 = island2.total_bridges()
        
        if current1 + count > island1.required_bridges:
            return False
        if current2 + count > island2.required_bridges:
            return False
            
        # Check if bridge would cross existing bridges
        return not any(self._bridges_cross([(x1, y1), (x2, y2)], 
                                         [bridge[0], bridge[1]]) 
                      for bridge in self.get_all_bridges())
