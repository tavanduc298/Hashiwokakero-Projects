def print_board(board):
    """
    Hiển thị bảng chơi ban đầu (chỉ có các đảo, chưa có cầu).

    Parameters:
        board: Bảng chơi Hashiwokakero.
    """
    # Khởi tạo lưới rỗng với ký tự "."
    grid = [["." for _ in range(board.width)] for _ in range(board.height)]

    # Điền số lượng cầu yêu cầu tại vị trí các đảo
    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)

    # In lưới ra màn hình
    for row in grid:
        print(" ".join(row))

def read_model_from_file(filename):
    """
    Đọc mô hình kết quả từ file đầu ra của SAT solver.

    Parameters:
        filename: Tên file chứa kết quả SAT.

    Returns:
        Danh sách các biến CNF dương đại diện cho cầu được chọn.
    """
    model = []
    with open(filename, "r") as f:
        lines = f.readlines()

        # Kiểm tra xem có lời giải hay không
        if lines[0].strip() != "SAT":
            print("No SAT solution found.")
            return []
        
        # Đọc dòng thứ hai chứa các biến CNF
        model = list(map(int, lines[1].strip().split()))
        
        # Lọc bỏ số 0 (SAT solver sử dụng 0 để kết thúc dòng)
        model = [var for var in model if var != 0]

    return model

def print_board_with_bridges(board, selected_vars):
    """
    Hiển thị bảng chơi với các cầu được tạo ra từ kết quả của SAT solver hoặc thuật toán tìm đường (A*).

    Parameters:
        board: Bảng chơi Hashiwokakero.
        selected_vars: Danh sách các biến CNF dương hoặc danh sách cầu từ thuật toán A*.
    """
    width = board.width
    height = board.height
    grid = [['.' for _ in range(width)] for _ in range(height)]

    # Điền số lượng cầu yêu cầu tại vị trí các đảo
    for island in board.islands:
        grid[island.y][island.x] = str(island.required_bridges)

    from collections import defaultdict
    bridge_count = defaultdict(int)

    if all(isinstance(var, int) for var in selected_vars):  # Kết quả từ SAT solver
        for var in selected_vars:
            if var > 0:
                i1, i2, num = board.reverse_var_map[var]
                key = tuple(sorted([i1, i2]))
                bridge_count[key] += 1
    else:  # Kết quả từ thuật toán A*
        for (x1, y1, x2, y2), count in selected_vars.items():
            key = tuple(sorted([(x1, y1), (x2, y2)]))
            bridge_count[key] += count

    # Vẽ các cây cầu trên lưới
    for (i1, i2), count in bridge_count.items():
        if i1[0] == i2[0]:  # Cầu dọc "|"
            x = i1[0]
            for y in range(min(i1[1], i2[1]) + 1, max(i1[1], i2[1])):
                grid[y][x] = "|" if count == 1 else "$" # "$" đại diện cho cầu đôi
        elif i1[1] == i2[1]:  # Cầu ngang "-"
            y = i1[1]
            for x in range(min(i1[0], i2[0]) + 1, max(i1[0], i2[0])):
                grid[y][x] = "-" if count == 1 else "=" # "=" đại diện cho cầu đôi

    for row in grid:
        print("[ " + " , ".join(row) + " ]")

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