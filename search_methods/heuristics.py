import math
import numpy as np
from scipy.optimize import linear_sum_assignment
from sokoban import Map


def heur_displaced(map_state: Map):
    count = 0

    for box_pos in map_state.positions_of_boxes:
        if box_pos not in map_state.targets:
            count += 1

    return count

def heur_manhattan_distance(map_state: Map):
    '''the sum Manhattan distances of the boxes to their closest goal. ''' 
    # an admissible heuristic which underestimates the cost to get from the current state to the goal.
    total = 0

    for box_pos in map_state.positions_of_boxes:
        dists = [abs(box_pos[0] - goal[0]) + abs(box_pos[1] - goal[1]) for goal in map_state.targets]
        total += min(dists)

    return total

def heur_euclidean_distance(map_state: Map):
    '''the sum Euclidean distances of the boxes to their closest goal. ''' 
    total = 0

    for box_pos in map_state.positions_of_boxes:
        dists = [math.sqrt((box_pos[0] - goal[0])**2 + (box_pos[1] - goal[1])**2) for goal in map_state.targets]
        total += min(dists)

    return total

def heur_hungarian(map_state: Map):
    boxes = map_state.positions_of_boxes
    goals = map_state.targets
    cost_matrix = np.zeros((len(boxes), len(goals)))

    for i, box in enumerate(boxes):
        for j, goal in enumerate(goals):
            cost_matrix[i][j] = abs(box[0] - goal[0]) + abs(box[1] - goal[1])

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total = cost_matrix[row_ind, col_ind].sum()

    return total


''' In addition next 4 functions are the implementation for a smarter heuristic'''
''' It helps for LRTA* (implemented without pulls or restarts) on easy and medium maps'''
def corner_deadlock(map_state: Map, box_pos: tuple[int, int]) -> bool:
    '''Checks if a box is corner-deadlocked'''
    x, y = box_pos
    width, height = map_state.width, map_state.length

    up_block = (y == 0) or ((x, y - 1) in map_state.obstacles)
    down_block = (y == height - 1) or ((x, y + 1) in map_state.obstacles)
    left_block = (x == 0) or ((x - 1, y) in map_state.obstacles)
    right_block = (x == width - 1) or ((x + 1, y) in map_state.obstacles)

    return (up_block or down_block) and (left_block or right_block)

def edge_deadlock(map_state: Map, box_pos: tuple[int, int]) -> bool:
    '''Checks if a box is on a wall edge AND no target exists aligned along that wall'''
    x, y = box_pos

    if x == 0 or x == map_state.width - 1:
        if not any(tx == x for tx, _ in map_state.targets):
            return True

    if y == 0 or y == map_state.length - 1:
        if not any(ty == y for _, ty in map_state.targets):
            return True

    return False

def box_unpushable(map_state: Map, box_pos: tuple[int, int]) -> bool:
    '''Checks if the box is surrounded in such a way it can no longer be pushed meaningfully'''
    x, y = box_pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # LEFT, RIGHT, UP, DOWN

    for dx, dy in directions:
        px, py = x - dx, y - dy  # player position
        bx, by = x + dx, y + dy  # where the box would be pushed

        if not (0 <= px < map_state.width and 0 <= py < map_state.length):
            continue

        if not (0 <= bx < map_state.width and 0 <= by < map_state.length):
            continue

        # box can be pushed if there's space ahead AND player can be behind it
        if (px, py) in map_state.obstacles or (px, py) in map_state.positions_of_boxes:
            continue

        if (bx, by) in map_state.obstacles or (bx, by) in map_state.positions_of_boxes:
            continue

        # avoid pushing box into immediate deadlock
        if not corner_deadlock(map_state, (bx, by)) and not edge_deadlock(map_state, (bx, by)):
            return False  # found at least one valid direction

    return True  # no valid push directions

def heur_improved(map_state: Map):
    '''Improved heuristic: Manhattan + deadlocks + clutter'''
    total = 0

    for box_pos in map_state.positions_of_boxes:
        if box_pos in map_state.targets:
            continue

        if box_unpushable(map_state, box_pos):
            return float('inf')

        dist_sum = min(abs(box_pos[0] - t[0]) + abs(box_pos[1] - t[1]) for t in map_state.targets)
        total += dist_sum

    return total
