from random import choice

class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        super().__init__(name="Grudgy Arthur", author="Nobu", description="")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """
        return GameMove.STEAL if (sum(opponent_history) / len(opponent_history)) < 0.5 else choice([GameMove.SHARE, GameMove.STEAL], (2, 1))

# This line is required!
userGame = ImportedStrat()

