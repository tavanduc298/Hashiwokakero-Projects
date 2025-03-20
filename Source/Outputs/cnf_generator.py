from itertools import combinations
import pickle

def get_var(board, island1, island2, bridge_num):
        key = tuple(sorted([(island1.x, island1.y), (island2.x, island2.y)])) + (bridge_num,)
        if key not in board.var_map:
            board.var_map[key] = board.variable_counter
            board.reverse_var_map[board.variable_counter] = key
            board.variable_counter += 1
        return board.var_map[key]

def generate_cnf_constraints(board):
        # Constraint: Mỗi cặp đảo có tối đa 2 cầu
        for i, island1 in enumerate(board.islands):
            for j in range(i + 1, len(board.islands)):
                island2 = board.islands[j]
                if board.can_connect(island1, island2):
                    v1 = get_var(board,island1, island2, 1)
                    v2 = get_var(board,island1, island2, 2)

                    # Nếu có cầu thứ 2 thì phải có cầu thứ nhất (v2 → v1): ¬v2 ∨ v1
                    board.clauses.append([-v2, v1])

        # Constraint: Tổng cầu đến mỗi đảo = required_bridges
        for island in board.islands:
            connected_vars = []
            for other in board.islands:
                if island == other:
                    continue
                if board.can_connect(island, other):
                    v1 = get_var(board,island, other, 1)
                    v2 = get_var(board,island, other, 2)
                    connected_vars += [v1, v2]

            # Ràng buộc AT MOST (≤ required_bridges)
            for comb in combinations(connected_vars, island.required_bridges + 1):
                board.clauses.append([-v for v in comb])

            # Ràng buộc AT LEAST (≥ required_bridges)
            # Nếu required_bridges > 0 thì sinh tổ hợp ít hơn required_bridges biến → không đủ → loại bỏ
            if island.required_bridges > 0:
                for comb in combinations(connected_vars, len(connected_vars) - island.required_bridges + 1):
                    # Ít nhất 1 biến trong tổ hợp này phải là TRUE
                    board.clauses.append([v for v in comb])

def export_cnf(board, filename="output.cnf"):
        generate_cnf_constraints(board)
        num_vars = board.variable_counter - 1
        num_clauses = len(board.clauses)

        with open(filename, "w") as f:
            f.write(f"p cnf {num_vars} {num_clauses}\n")
            for clause in board.clauses:
                f.write(" ".join(str(lit) for lit in clause) + " 0\n")

        # ✅ Lưu reverse_var_map vào file reverse_map.pkl
        with open("Reverse_map.pkl", "wb") as f:
            pickle.dump(board.reverse_var_map, f)

        print(f"✅ CNF exported to '{filename}' with {num_vars} variables and {num_clauses} clauses.")