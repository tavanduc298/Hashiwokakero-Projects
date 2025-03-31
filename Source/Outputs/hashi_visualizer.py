def print_board(board):
    """Display the initial board state."""
    grid = [["." for _ in range(board.width)] for _ in range(board.height)]
    
    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)
    
    for row in grid:
        print(" ".join(row))

def print_board_with_bridges(board, bridges):
    """Display board with bridges."""
    grid = [["0" for _ in range(board.width)] for _ in range(board.height)]
    
    # Add islands
    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)
    
    # Handle different bridge formats
    if isinstance(bridges, dict):  # A* solver format
        for (x1, y1, x2, y2), count in bridges.items():
            if x1 == x2:  # Vertical bridge
                for y in range(min(y1, y2) + 1, max(y1, y2)):
                    grid[y][x1] = '$' if count == 2 else '│'
            else:  # Horizontal bridge
                for x in range(min(x1, x2) + 1, max(x1, x2)):
                    grid[y1][x] = '═' if count == 2 else '─'
    else:  # Backtracking format
        for bridge in bridges:
            if isinstance(bridge, tuple):
                if len(bridge) == 4:  # (x1, y1, x2, y2)
                    x1, y1, x2, y2 = bridge
                    count = 1
                else:  # (x1, y1, x2, y2, count)
                    x1, y1, x2, y2, count = bridge
                
                if x1 == x2:  # Vertical bridge
                    for y in range(min(y1, y2) + 1, max(y1, y2)):
                        grid[y][x1] = '$' if count == 2 else '│'
                else:  # Horizontal bridge
                    for x in range(min(x1, x2) + 1, max(x1, x2)):
                        grid[y1][x] = '═' if count == 2 else '─'

    # Print grid
    for row in grid:
        print("[ " + " , ".join(row) + " ]")

def read_model_from_file(filename):
    """Read SAT solver output."""
    model = []
    with open(filename, "r") as f:
        lines = f.readlines()
        if lines[0].strip() != "SAT":
            return []
        model = [var for var in map(int, lines[1].strip().split()) if var != 0]
    return model

def write_output_map(board, selected_vars, width, height):
    """
    Xuất bản đồ kết quả ra file `output.txt`, thể hiện số cầu đã nối giữa các đảo.

    Parameters:
        board: Bảng chơi Hashiwokakero.
        selected_vars: Danh sách các biến CNF dương đại diện cho cầu được chọn.
        width: Chiều rộng của bảng.
        height: Chiều cao của bảng.
    """
    # Khởi tạo bản đồ với "0"
    map_grid = [["0" for _ in range(width)] for _ in range(height)]

    # Ghi số required_bridges vào bản đồ
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

    # Cập nhật cầu vào bản đồ
    for (i1, i2), count in bridge_count.items():
        if i1[0] == i2[0]:  # Cầu dọc "|"
            x = i1[0]
            for y in range(min(i1[1], i2[1]) + 1, max(i1[1], i2[1])):
                map_grid[y][x] = "|" if count == 1 else "$"
        elif i1[1] == i2[1]:  # Cầu ngang "-"
            y = i1[1]
            for x in range(min(i1[0], i2[0]) + 1, max(i1[0], i2[0])):
                map_grid[y][x] = "−" if count == 1 else "="

    # In kết quả
    with open("output.txt", "w", encoding="utf-8") as f:
        for row in map_grid:
            f.write("[ " + " , ".join(row) + " ]\n")