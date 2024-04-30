from enum import Enum


class GameMove(Enum):
    STEAL = 0
    SHARE = 1


class GameStrategy:
    meta = {}

    def __init__(self, name: str, author: str, description: str) -> None:
        self.meta = {'name': name, 'author': author, 'description': description}

    def get_meta(self) -> dict[str, str]:
        return self.meta

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """
        pass


class DemoStrat0(GameStrategy):
    def __init__(self):
        super().__init__(name="Demo Strategy 0", author="John Doe", description="zeroth demo strategy")


class DemoStrat1(GameStrategy):
    def __init__(self):
        super().__init__(name="Demo Strategy 1", author="Jane Doe", description="first demo strategy")
