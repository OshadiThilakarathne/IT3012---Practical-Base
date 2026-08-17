import random
from collections import deque
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']

        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Goal-based agent using BFS, DFS, or UCS to plan paths to food."""

    def __init__(self):
        # Offline plan that will be executed one action at a time
        self.plan = []

        # Change this to BFS, DFS, or UCS for the observation task
        self.active_algo = 'BFS'

    def get_neighbors(self, state, grid_size, walls):
        """Return valid neighboring states and their actions."""

        x, y = state
        width, height = grid_size

        # These directions match execute_action() in visual_grid_game.py
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

        # Graph-search reached set
        reached = {start}

        while frontier:
            state, path = frontier.popleft()

            # Goal reached
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

        # No path found
        return []

    def dfs_search(self, start, goal, grid_size, walls):
        """Depth-First Search."""

        # LIFO stack
        frontier = [(start, [])]

        # Graph-search reached set
        reached = {start}

        while frontier:
            state, path = frontier.pop()

            # Goal reached
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

        # No path found
        return []

    def ucs_search(self, start, goal, grid_size, walls):
        """Uniform-Cost Search."""

        # Priority queue:
        # (total_cost, state, path)
        frontier = []

        heapq.heappush(
            frontier,
            (0, start, [])
        )

        # Store the cheapest cost found for each state
        reached = {
            start: 0
        }

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            # Goal reached
            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):

                # Every grid movement has cost 1
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
                    abs(current_position[0] - food[0])
                    + abs(current_position[1] - food[1])
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

            else:
                raise ValueError(
                    f"Unknown algorithm: {self.active_algo}"
                )

        # Execute the first action in the plan
        if self.plan:
            return self.plan.pop(0)

        # No valid path
        return None
