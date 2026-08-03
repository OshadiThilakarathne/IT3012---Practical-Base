# agent.py
class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    def sense_and_act(self, percept):
        if percept["food_here"]:
            return "Stay"
        elif percept["wall_ahead"]:
            return "Left"
        else:
            return "Up"
class ModelBasedAgent:
    def __init__(self):
        self.last_action = None
        self.failed_moves = 0
    def sense_and_act(self, percept):
        if percept["wall_ahead"]:
            self.failed_moves += 1
        else:
            self.failed_moves = 0
        if percept["food_here"]:
            action = "Stay"
        elif percept["wall_ahead"]:
            if self.failed_moves == 1:
                action = "Left"
            elif self.failed_moves == 2:
                action = "Right"
            else:
                action = "Down"
        else:
            action = "Up"
        self.last_action = action
        return action
