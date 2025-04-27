from sokoban import Map
from .solver import Solver

class LRTAStarSolver(Solver):
    def __init__(self, map: Map, max_steps=1000, max_restarts=1000):
        super().__init__(map)
        self.max_steps = max_steps
        self.max_restarts = max_restarts

    def solve(self, heuristic):
        # Live estimation table from current state to goal
        H = {}
        expanded_states = 0

        for _ in range(self.max_restarts):
            current = self.map.copy()
            path_history = [current.copy()]

            for _ in range(self.max_steps):
                if current.is_solved():
                    path_history.append(current.copy())
                    return expanded_states, path_history

                curr_key = str(current)

                # Adds an estimation for current state if there is no one in the table
                if curr_key not in H:
                    H[curr_key] = heuristic(current)

                expanded_states += len(current.get_neighbours())

                neighbors = current.get_neighbours()
                if not neighbors:
                    break

                # Uniform cost for every move
                cost = 1
                neighbor_costs = []

                for neighbor in neighbors:
                    n_key = str(neighbor)

                    if n_key not in H:
                        H[n_key] = heuristic(neighbor)
                    
                    # lrta* idea: cost (s -> s') + heur(s')
                    f = cost + H[n_key]
                    neighbor_costs.append((f, neighbor))

                # Most promising move
                best_f, best_neighbor = min(neighbor_costs, key=lambda x: x[0])

                # Update the current state's estimated cost in H based on the best neighbor
                H[curr_key] = best_f

                # Executes the action
                current = best_neighbor
                path_history.append(current.copy())

        # If there is no solution after max steps
        return expanded_states, path_history
