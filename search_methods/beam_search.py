from sokoban import Map
from .solver import Solver
import random

class BeamSearchSolver(Solver):
    def __init__(self, map: Map, beam_width=450, max_steps=1000, restart_threshold=15, randomness_factor=0.3):
        ''' beam_width - number of steps kept in each iteration
            max_steps - maximum number of iterations before stopping
            restart_threshold - when to restart if progress stalls
            randomness_factor - strength of the randomness added to heuristic '''
        super().__init__(map)
        self.beam_width = beam_width

        self.max_steps = max_steps
        self.restart_threshold = restart_threshold

        self.randomness_factor = randomness_factor
        random.seed(0)

    def solve(self, heuristic):
        initial_state = self.map.copy()
        
        # Used to avoid visiting the same state multiple times (caching)
        visited = set()

        beam = [(heuristic(initial_state), initial_state, [])]
        visited.add(str(initial_state))

        best_state = initial_state
        best_path = []

        best_h = float('inf')
        stagnation = 0
        expanded_states = 0

        for _ in range(self.max_steps):
            new_beam = []

            # Expand each state in the current beam
            for _, state, path in beam:
                if state.is_solved():
                    return expanded_states, path + [state]

                expanded_states += len(state.get_neighbours())

                # Generate all valid next states (neighbors)
                for neighbor in state.get_neighbours():
                    neighbor_str = str(neighbor)

                    # Skip visited states to avoid cycles
                    if neighbor_str in visited:
                        continue
                    visited.add(neighbor_str)

                    # Evaluate heuristic and add randomness (to avoid shoulders)
                    h = heuristic(neighbor)
                    h += random.uniform(-self.randomness_factor, self.randomness_factor) * h

                    new_beam.append((h, neighbor, path + [state]))

                    # Track the best neigbor state seen so far
                    if h < best_h:
                        best_h = h
                        best_state = neighbor
                        best_path = path + [state]
                        stagnation = 0

            stagnation += 1
            
            # If there are no succesors, restart from initial state
            if not new_beam:
                beam = [(heuristic(initial_state), initial_state, [])]
                visited = {str(initial_state)}
                continue

            # Keep only the top-k best scoring succesors (the beam idea)
            beam = sorted(new_beam, key=lambda x: x[0])[:self.beam_width]

            # Restart search from scratch to escape local minimum
            if stagnation >= self.restart_threshold:
                beam = [(heuristic(initial_state), initial_state.copy(), [])]
                visited = {str(initial_state)}
                stagnation = 0

        # If no solution found, return best effort path
        return expanded_states, best_path + [best_state]
