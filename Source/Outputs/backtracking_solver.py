from collections import deque
import sys
from puzzle_parser import *
from hashi_visualizer import *
from cnf_generator import *

def combine_bridges(bridges):
    """Combine bridges between same islands, respecting max 2 bridges limit."""
    combined = {}
    for x1, y1, x2, y2, count in bridges:
        key = tuple(sorted([(x1, y1), (x2, y2)]))
        if key in combined:
            combined[key] = min(combined[key] + count, 2)  # Limit to maximum 2 bridges
        else:
            combined[key] = min(count, 2)
    
    result = []
    for (p1, p2), count in combined.items():
        x1, y1 = p1
        x2, y2 = p2
        result.append((x1, y1, x2, y2, count))
    return result

def get_bridge_count(bridges, x1, y1, x2, y2):
    """Get current number of bridges between two points."""
    count = 0
    for bx1, by1, bx2, by2, num in bridges:
        if (x1, y1) in [(bx1, by1), (bx2, by2)] and (x2, y2) in [(bx1, by1), (bx2, by2)]:
            count += num
    return count

def backtrack_solve(board, bridges):
    """Attempt to solve the puzzle using backtracking with improvements."""
    if all(island.is_satisfied() for island in board.islands):
        return True

    # Find most constrained unsatisfied island
    current_island = None
    min_remaining = float('inf')
    for island in board.islands:
        if not island.is_satisfied():
            remaining = island.required_bridges - island.total_bridges()
            options = sum(1 for n in board.islands if board.can_connect(island, n))
            score = remaining / (options if options > 0 else 1)
            if score < min_remaining:
                min_remaining = score
                current_island = island
    
    if not current_island:
        return True

    # Sort neighbors by constraints
    neighbors = []
    x1, y1 = current_island.x, current_island.y
    for neighbor in board.islands:
        if neighbor != current_island and board.can_connect(current_island, neighbor):
            x2, y2 = neighbor.x, neighbor.y
            remaining = neighbor.required_bridges - neighbor.total_bridges()
            current_bridges = get_bridge_count(bridges, x1, y1, x2, y2)
            if current_bridges < 2:  # Only consider if below max bridges
                neighbors.append((remaining, neighbor))
    
    # Sort by remaining bridges count using lambda key
    neighbors.sort(key=lambda x: x[0], reverse=True)
    
    for _, neighbor in neighbors:
        x2, y2 = neighbor.x, neighbor.y
        bridges_needed1 = current_island.required_bridges - current_island.total_bridges()
        bridges_needed2 = neighbor.required_bridges - neighbor.total_bridges()
        current_bridges = get_bridge_count(bridges, x1, y1, x2, y2)
        max_bridges = min(bridges_needed1, bridges_needed2, 2 - current_bridges)
        
        for num_bridges in range(max_bridges, 0, -1):
            if board.can_add_bridge(x1, y1, x2, y2, num_bridges):
                board.add_bridge(x1, y1, x2, y2, num_bridges)
                bridges.append((x1, y1, x2, y2, num_bridges))
                
                if backtrack_solve(board, bridges):
                    return True
                
                bridges.pop()
                board.remove_bridge(x1, y1, x2, y2, num_bridges)
    
    return False

def backtracking(board):
    """Main function to run the backtracking solver."""
    bridges = []
    initial_board = board.clone()
    
    # Try to solve the puzzle
    if backtrack_solve(initial_board, bridges):
        combined_bridges = combine_bridges(bridges)
        print("Solution found!")
        print(f"Total unique bridges: {len(combined_bridges)}")
        with open("output.txt", "w", encoding="utf-8") as f:
                original_stdout = sys.stdout
                sys.stdout = f
                print_board_with_bridges(board, combined_bridges)    # Xuất kết quả vào file
                sys.stdout = original_stdout   # Khôi phục stdout

        print("Đã ghi kết quả vào output.txt")
        return True
    
    print("\nNo solution found!")
    return False
