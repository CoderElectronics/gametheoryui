from functools import reduce
from random import choice


class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        super().__init__(name="Nicer Bob", author="Nobu", description="too lazy to explain")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """

        share_weight = sum(opponent_history)
        steal_weight = len(opponent_history) - share_weight

        return choice([GameMove.SHARE, GameMove.STEAL], (steal_weight, share_weight))


# This line is required!
userGame = ImportedStrat()
