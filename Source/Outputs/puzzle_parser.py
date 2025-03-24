from _init_ import *

def load_board_from_file(filename):
    """
    Đọc file đầu vào chứa ma trận và tạo đối tượng Board từ dữ liệu đó.
    
    :param filename: Đường dẫn đến file input.
    :return: Đối tượng Board đã được khởi tạo với các đảo và số cầu yêu cầu.
    """
    matrix = [] # Danh sách lưu trữ ma trận từ file

    # Đọc file và chuyển dữ liệu thành ma trận số nguyên
    with open(filename, 'r') as file:
        for line in file:
            row = [int(cell.strip()) for cell in line.strip().split(',')]   # Tách số theo dấu phẩy
            matrix.append(row)

    # Xác định kích thước của ma trận
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0 # Lấy chiều rộng từ dòng đầu tiên

    # Tạo một đối tượng Board với kích thước đã xác định
    board = Board(width, height)

    # Duyệt qua ma trận để tìm các đảo và thêm chúng vào board
    for y in range(height):
        for x in range(width):
            if matrix[y][x] != 0:   # Nếu ô không phải 0, nghĩa là có đảo
                board.add_island(x, y, matrix[y][x])    # Thêm đảo vào board

    return board