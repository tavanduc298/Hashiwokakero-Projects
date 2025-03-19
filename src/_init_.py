class Island:
    def __init__(self, x, y, required_bridges):
        self.x = x
        self.y = y
        self.required_bridges = required_bridges
        self.connections = {}

    def total_bridges(self):
        return sum(self.connections.values())

    def is_satisfied(self):
        return self.total_bridges() == self.required_bridges

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.islands = []
        self.var_map = {}  # Mapping from (island1, island2) to variable ID
        self.reverse_var_map = {}  # Để ánh xạ biến → (island1, island2, bridge_num)
        self.clauses = []
        self.variable_counter = 1

    def add_island(self, x, y, required_bridges):
        self.islands.append(Island(x, y, required_bridges))

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
                if self.get_island_at(island1.x, y):
                    return False
        else:
            x_range = range(min(island1.x, island2.x) + 1, max(island1.x, island2.x))
            for x in x_range:
                if self.get_island_at(x, island1.y):
                    return False

        return True
