import random
from collections import deque
import heapq
import math


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']

        return random.choice(self.actions_pool)


class SearchAgent:
    """Goal-based agent using BFS, DFS, UCS, or A* to plan paths to food."""

    def __init__(self):
        # Offline plan that will be executed one action at a time
        self.plan = []

        # Select the search algorithm
        self.active_algo = 'AStar'

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance."""
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    def get_neighbors(self, state, grid_size, walls):
        """Return valid neighboring states and their actions."""

        x, y = state
        width, height = grid_size

        moves = [
            ((x, y + 1), 'Up'),
            ((x, y - 1), 'Down'),
            ((x - 1, y), 'Left'),
            ((x + 1, y), 'Right')
        ]

        neighbors = []

        for next_state, action in moves:
            nx, ny = next_state

            # Check grid boundaries
            if 0 <= nx < width and 0 <= ny < height:

                # Don't move through walls
                if next_state not in walls:
                    neighbors.append((next_state, action))

        return neighbors

    def bfs_search(self, start, goal, grid_size, walls):
        """Breadth-First Search."""

        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:
            state, path = frontier.popleft()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):
                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    def dfs_search(self, start, goal, grid_size, walls):
        """Depth-First Search."""

        frontier = [(start, [])]

        reached = {start}

        while frontier:
            state, path = frontier.pop()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):
                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    def ucs_search(self, start, goal, grid_size, walls):
        """Uniform-Cost Search."""

        frontier = []

        heapq.heappush(
            frontier,
            (0, start, [])
        )

        reached = {
            start: 0
        }

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):

                new_cost = cost + 1

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            new_path
                        )
                    )

        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """A* Search using f(n) = g(n) + h(n)."""

        # Priority queue
        frontier = []

        # Reached states
        reached_states = set()

        # Starting node
        g_cost = 0

        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )
        elif heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )
        else:
            raise ValueError(
                f"Unknown heuristic: {heuristic_type}"
            )

        # f(n) = g(n) + h(n)
        f_cost = g_cost + h_cost

        # Required A* tuple:
        # (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(
            frontier,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        while frontier:

            # Get node with the lowest f_cost
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                frontier
            )

            # Goal reached
            if current_pos == goal_pos:
                return path_taken

            # Skip states that have already been processed
            if current_pos in reached_states:
                continue

            # Mark current state as reached
            reached_states.add(current_pos)

            # Expand the four neighboring cells
            for next_state, action in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                # Skip already reached states
                if next_state in reached_states:
                    continue

                # Calculate g(n)
                new_g_cost = g_cost + 1

                # Calculate h(n)
                if heuristic_type == 'manhattan':
                    new_h_cost = self.manhattan_distance(
                        next_state,
                        goal_pos
                    )
                else:
                    new_h_cost = self.euclidean_distance(
                        next_state,
                        goal_pos
                    )

                # Calculate f(n)
                new_f_cost = new_g_cost + new_h_cost

                # Add the new action to the path
                new_path = path_taken + [action]

                # Add node to priority queue
                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        next_state,
                        new_path
                    )
                )

        # No path found
        return []

    def sense_and_act(self, percept: dict) -> str:
        """Create an offline plan and execute it one action at a time."""

        # Create a new plan only when the current plan is empty
        if not self.plan:

            # Current agent position
            current_position = tuple(
                percept['agent_pos']
            )

            # All available food
            all_food = percept['all_food']

            # No food remaining
            if not all_food:
                return None

            # Find the closest food using Manhattan distance
            target_food = min(
                all_food,
                key=lambda food:
                    self.manhattan_distance(
                        current_position,
                        tuple(food)
                    )
            )

            target_food = tuple(target_food)

            # Get global environment information
            grid_size = percept['grid_size']

            walls = {
                tuple(wall)
                for wall in percept['walls']
            }

            # Select the search algorithm
            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    current_position,
                    target_food,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    current_position,
                    target_food,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    current_position,
                    target_food,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    current_position,
                    target_food,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )

            else:

                raise ValueError(
                    f"Unknown algorithm: {self.active_algo}"
                )

        # Execute the first action in the plan
        if self.plan:
            return self.plan.pop(0)

        # No valid path
        return None


# Testing checkpoint for the heuristic functions
if __name__ == "__main__":
    agent = SearchAgent()

    print(
        "Manhattan:",
        agent.manhattan_distance((0, 0), (3, 4))
    )

    print(
        "Euclidean:",
        agent.euclidean_distance((0, 0), (3, 4))
    )