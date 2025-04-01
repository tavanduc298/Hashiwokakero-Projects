from _init_ import *
from hashi_visualizer import *
import sys
from collections import deque

def is_fully_connected(board):
    """Kiểm tra xem tất cả các đảo đã được kết nối đầy đủ chưa"""
    if not board.islands:
        return True
        
    # Kiểm tra mỗi đảo có đủ số cầu yêu cầu không
    for island in board.islands:
        if island.total_bridges() != island.required_bridges:
            return False
    
    # BFS để kiểm tra kết nối
    visited = set()
    start = max(board.islands, key=lambda x: x.required_bridges)  # Bắt đầu từ đảo có nhiều cầu nhất
    queue = deque([start])
    
    while queue:
        island = queue.popleft()
        if (island.x, island.y) not in visited:
            visited.add((island.x, island.y))
            # Chỉ xét đảo có đủ số cầu theo yêu cầu
            if island.total_bridges() == island.required_bridges:
                for (nx, ny), bridge_count in island.connections.items():
                    next_island = board.get_island_at(nx, ny)
                    if next_island and (next_island.x, next_island.y) not in visited:
                        # Kiểm tra cả hai đầu cầu đều có số cầu đúng
                        if next_island.total_bridges() == next_island.required_bridges:
                            queue.append(next_island)
    
    return len(visited) == len(board.islands)

def validate_puzzle(board):
    """Kiểm tra tính hợp lệ của puzzle trước khi giải"""
    # Kiểm tra tổng số cầu phải chẵn
    total_required = sum(island.required_bridges for island in board.islands)
    if total_required % 2 != 0:
        return False
        
    # Kiểm tra khả năng kết nối của mỗi đảo
    for island in board.islands:
        # Đếm số đảo có thể kết nối được
        reachable_islands = 0
        potential_bridges = 0
        x, y = island.x, island.y
        
        # Kiểm tra 4 hướng
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            while 0 <= nx < board.width and 0 <= ny < board.height:
                if (nx, ny) in board.island_positions:
                    reachable_islands += 1
                    potential_bridges += 2  # Mỗi hướng tối đa 2 cầu
                    break
                nx += dx
                ny += dy
                
        # Kiểm tra các điều kiện không thể có giải pháp
        if reachable_islands == 0 and island.required_bridges > 0:
            return False
        if potential_bridges < island.required_bridges:
            return False
        if reachable_islands == 1 and island.required_bridges > 2:
            return False
            
    return True

def get_required_double_bridges(value):
    """Tính số cầu đôi bắt buộc cho mỗi giá trị"""
    if value >= 8: return 4
    if value == 7: return 3
    if value == 6: return 2
    if value == 5: return 1
    return 0

def calculate_required_doubles(island):
    """Tính số cầu đôi tối thiểu cần thiết"""
    value = island.required_bridges
    if value >= 8: return 4
    if value == 7: return 3
    if value == 6: return 2
    if value == 5: return 1
    return 0

def get_possible_moves(board, island):
    """Lấy các nước đi khả thi cho một đảo"""
    moves = []
    x, y = island.x, island.y
    center_x = board.width // 2
    
    # Ưu tiên theo thứ tự: cột giữa trước, sau đó là vertical, cuối cùng là horizontal
    directions = []
    
    # Nếu đảo nằm ở cột giữa, thêm các hướng vertical trước
    if x == center_x:
        directions.extend([(0, -1, 30), (0, 1, 30)])
    
    # Thêm các hướng còn lại
    directions.extend([(-1, 0, 10), (1, 0, 10)])
    if x != center_x:
        directions.extend([(0, -1, 20), (0, 1, 20)])
    
    for dx, dy, priority in directions:
        nx, ny = x + dx, y + dy
        while 0 <= nx < board.width and 0 <= ny < board.height:
            if (nx, ny) in board.island_positions:
                other = board.get_island_at(nx, ny)
                if other and other.total_bridges() < other.required_bridges:
                    # Tính độ ưu tiên dựa trên số cầu đôi cần thiết
                    required_doubles = max(
                        calculate_required_doubles(island),
                        calculate_required_doubles(other)
                    )
                    final_priority = priority + required_doubles * 5
                    moves.append((other, final_priority))
                break
            nx += dx
            ny += dy
    
    return sorted(moves, key=lambda x: -x[1])

def get_island_priority(board, island):
    """Get priority score for island processing"""
    center_x = board.width // 2
    required_doubles = get_required_double_bridges(island.required_bridges)
    current_doubles = sum(1 for count in island.connections.values() if count == 2)
    
    # Give very high priority to islands needing exactly 4 double bridges (value 8)
    if island.required_bridges == 8 and current_doubles < 4:
        return 10000
        
    # High priority for islands needing 3 double bridges (value 7)
    if island.required_bridges == 7 and current_doubles < 3:
        return 5000
        
    # Normal priority calculation
    return (1000 if island.x == center_x else 0) + \
           (island.required_bridges * 100) + \
           ((required_doubles - current_doubles) * 50)

def solve(board):
    """Giải bài toán Hashiwokakero"""
    if all(island.total_bridges() == island.required_bridges for island in board.islands):
        return board.get_all_bridges() if is_fully_connected(board) else None

    # Find next island to process with updated priority
    unfinished = []
    for island in board.islands:
        if island.total_bridges() < island.required_bridges:
            priority = get_island_priority(board, island)
            
            # Early validation for islands needing double bridges
            required_doubles = get_required_double_bridges(island.required_bridges)
            current_doubles = sum(1 for count in island.connections.values() if count == 2)
            remaining_connections = len(get_possible_moves(board, island))
            
            # If we can't satisfy double bridge requirement, backtrack
            if required_doubles - current_doubles > remaining_connections:
                return None
                
            unfinished.append((island, priority))

    if not unfinished:
        return None

    current = max(unfinished, key=lambda x: x[1])[0]
    required_doubles = get_required_double_bridges(current.required_bridges)
    current_doubles = sum(1 for count in current.connections.values() if count == 2)

    # For islands requiring all double bridges (value 8), try only double bridges
    must_use_doubles = current.required_bridges == 8 or \
                      (current.required_bridges == 7 and current_doubles < 3) or \
                      (current.required_bridges == 6 and current_doubles < 2)

    # Get moves sorted by priority
    moves = get_possible_moves(board, current)
    
    # Try each possible move
    for other, _ in moves:
        # For value 8, only try double bridges
        if must_use_doubles:
            bridges = [2]
        else:
            bridges = [2, 1] if required_doubles > current_doubles else [1, 2]
            
        for bridge_count in bridges:
            if board.can_add_bridge(current.x, current.y, other.x, other.y, bridge_count):
                test = board.clone()
                test.add_bridge(current.x, current.y, other.x, other.y, bridge_count)
                result = solve(test)
                if result:
                    return result

    return None

def solve_brute_force(board):
    """Giải puzzle Hashiwokakero bằng brute-force"""
    # Kiểm tra tính hợp lệ trước
    if not validate_puzzle(board):
        print("Không tìm thấy giải pháp hợp lệ.")
        return None

    try:
        solution_bridges = solve(board)
        if not solution_bridges:
            print("Không tìm thấy giải pháp hợp lệ.")
            return None

        # Verify solution
        test_board = board.clone()
        
        # Thử từng cầu và kiểm tra
        for (x1, y1), (x2, y2), count in solution_bridges:
            if not test_board.can_add_bridge(x1, y1, x2, y2, count):
                print("Không tìm thấy giải pháp hợp lệ.")
                return None
            test_board.add_bridge(x1, y1, x2, y2, count)
            
            # Kiểm tra sau mỗi lần thêm cầu
            island1 = test_board.get_island_at(x1, y1)
            island2 = test_board.get_island_at(x2, y2)
            if (island1.total_bridges() > island1.required_bridges or
                island2.total_bridges() > island2.required_bridges):
                print("Không tìm thấy giải pháp hợp lệ.")
                return None

        # Kiểm tra cuối cùng
        if not test_board.verify_all_bridges() or not is_fully_connected(test_board):
            print("Không tìm thấy giải pháp hợp lệ.")
            return None

        # In kết quả nếu pass hết các kiểm tra
        result = [['0'] * board.width for _ in range(board.height)]
        
        # Place islands first
        for island in board.islands:
            result[island.y][island.x] = str(island.required_bridges)
            
        # Process bridges in specific order: horizontal first, then vertical
        horizontal_bridges = []
        vertical_bridges = []
        
        for (x1, y1), (x2, y2), count in solution_bridges:
            if y1 == y2:  # Horizontal bridge
                horizontal_bridges.append(((x1, y1), (x2, y2), count))
            else:  # Vertical bridge
                vertical_bridges.append(((x1, y1), (x2, y2), count))
                
        # Place horizontal bridges first
        for (x1, y1), (x2, y2), count in horizontal_bridges:
            bridge_char = '═' if count == 2 else '-'
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                result[y1][x] = bridge_char
                
        # Then place vertical bridges
        for (x1, y1), (x2, y2), count in vertical_bridges:
            bridge_char = '│' if count == 1 else '$'
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                # Only place vertical bridge if there isn't a horizontal bridge there
                if result[y][x1] == '0':
                    result[y][x1] = bridge_char

        # Display result
        with open("output.txt", "w", encoding="utf-8") as f:
            original_stdout = sys.stdout
            sys.stdout = f
            for i, row in enumerate(result):
                print("[ ", end="")
                print(" , ".join(row), end="")
                print(" ]", end="")
                if i < len(result) - 1:
                    print()
            sys.stdout = original_stdout   # Khôi phục stdout

        print("Đã ghi kết quả vào output.txt")
        
        return solution_bridges
    except:
        print("Không tìm thấy giải pháp hợp lệ.")
        return None
