"""
Tit for tat game theory strategy for GameTheoryUI.
by: Ari Stehney

Customize the class below with your metadata and fill out the play function
"""
from game_class import GameMove


class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        # This is where your metadata will go:
        super().__init__(name="Tit for Tat", author="Ari S.", description="This one is the winner")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """
        # This is where your strategy logic goes
        # Each item in the history arrays will be equal to GameMove.STEAL or GameMove.SHARE

        if len(opponent_history) < 1:
            return GameMove.SHARE
        else:
            return opponent_history[-1]

# This line is required!
userGame = ImportedStrat()
