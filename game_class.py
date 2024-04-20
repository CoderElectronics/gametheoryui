class GameStrategy:
    meta = {}
    game_plays = []

    def __init__(self, **args):
        self.meta = args

    def get_meta(self):
        return self.meta

    def get_plays(self):
        return self.game_plays

    # Game logic
    """
    def next_play(self):
        pass
    """

class DemoStrat0(GameStrategy):
    def __init__(self):
        super().__init__(name="Demo Strategy 0", author="John Doe", description="zeroth demo strategy")

    def next_play(self):
        pass

class DemoStrat1(GameStrategy):
    def __init__(self):
        super().__init__(name="Demo Strategy 1", author="Jane Doe", description="first demo strategy")

    def next_play(self):
        pass