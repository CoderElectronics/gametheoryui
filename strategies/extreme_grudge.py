"""
Grudge game theory strategy for GameTheoryUI.
by: Ari Stehney

Customize the class below with your metadata and fill out the play function
"""
from game_class import GameMove

class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        # This is where your metadata will go:
        super().__init__(name="Extreme grudge", author="Ari S.", description="Will hold a grudge for the rest of the rounds if provoked")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """
        # This is where your strategy logic goes
        # Each item in the history arrays will be equal to GameMove.STEAL or GameMove.SHARE

        if not GameMove.STEAL in opponent_history:
            return GameMove.SHARE
        else:
            return GameMove.STEAL

# This line is required!
userGame = ImportedStrat()
