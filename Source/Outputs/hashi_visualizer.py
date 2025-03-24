def print_board(board):
    grid = [["." for _ in range(board.width)] for _ in range(board.height)]

    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)

    for row in grid:
        print(" ".join(row))

def read_model_from_file(filename):
    model = []
    with open(filename, "r") as f:
        lines = f.readlines()
        if lines[0].strip() != "SAT":
            print("❌ No SAT solution found.")
            return []

        model = list(map(int, lines[1].strip().split()))
        model = [var for var in model if var != 0]
    return model

def print_board_with_bridges(board, selected_vars):
    width = board.width
    height = board.height
    grid = [['.' for _ in range(width)] for _ in range(height)]

    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)

    from collections import defaultdict
    bridge_count = defaultdict(int)

    if all(isinstance(var, int) for var in selected_vars):  # CNF output
        for var in selected_vars:
            if var > 0:
                i1, i2, num = board.reverse_var_map[var]
                key = tuple(sorted([i1, i2]))
                bridge_count[key] += 1
    else:  # Danh sách cầu từ A*
        for (x1, y1, x2, y2), count in selected_vars.items():
            key = tuple(sorted([(x1, y1), (x2, y2)]))
            bridge_count[key] += count

    for (i1, i2), count in bridge_count.items():
        if i1[0] == i2[0]:  # vertical
            x = i1[0]
            for y in range(min(i1[1], i2[1]) + 1, max(i1[1], i2[1])):
                grid[y][x] = "|" if count == 1 else "$"
        elif i1[1] == i2[1]:  # horizontal
            y = i1[1]
            for x in range(min(i1[0], i2[0]) + 1, max(i1[0], i2[0])):
                grid[y][x] = "-" if count == 1 else "="

    for row in grid:
        print("[ " + " , ".join(row) + " ]")

def write_output_map(board, selected_vars, width, height):
        # Khởi tạo bản đồ với "0"
        map_grid = [["0" for _ in range(width)] for _ in range(height)]

        # Ghi số required_bridges vào map
        for island in board.islands:
            map_grid[island.y][island.x] = str(island.required_bridges)

        # Đếm số cầu giữa các cặp đảo
        from collections import defaultdict
        bridge_count = defaultdict(int)
        for var in selected_vars:
            if var > 0:
                i1, i2, num = board.reverse_var_map[var]
                # i1, i2 là tuple (x, y), nên dùng i1[0], i1[1]
                key = tuple(sorted([i1, i2], key=lambda x: (x[0], x[1])))
                bridge_count[key] += 1

        # Cập nhật cầu vào map
        for (i1, i2), count in bridge_count.items():
            if i1[0] == i2[0]:  # Cầu dọc (−)
                x = i1[0]
                for y in range(min(i1[1], i2[1]) + 1, max(i1[1], i2[1])):
                    map_grid[y][x] = "|" if count == 1 else "$"
            elif i1[1] == i2[1]:  # Cầu ngang (=)
                y = i1[1]
                for x in range(min(i1[0], i2[0]) + 1, max(i1[0], i2[0])):
                    map_grid[y][x] = "−" if count == 1 else "="

        # In kết quả
        with open("output.txt", "w", encoding="utf-8") as f:
            for row in map_grid:
                f.write("[ " + " , ".join(row) + " ]\n")