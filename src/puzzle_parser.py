from src._init_ import *

def load_board_from_file(filename):
    matrix = []
    with open(filename, 'r') as file:
        for line in file:
            row = [int(cell.strip()) for cell in line.strip().split(',')]
            matrix.append(row)

    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0

    board = Board(width, height)

    for y in range(height):
        for x in range(width):
            if matrix[y][x] != 0:
                board.add_island(x, y, matrix[y][x])

    return board