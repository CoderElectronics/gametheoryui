"""
Always steal game theory strategy for GameTheoryUI.
by: Ari Stehney

Customize the class below with your metadata and fill out the play function
"""

class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        # This is where your metadata will go:
        super().__init__(name="Sharing Strategy", author="Ari S.", description="Always shares, no matter what")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """

        return GameMove.SHARE

# This line is required!
userGame = ImportedStrat()
