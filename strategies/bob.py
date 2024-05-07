from functools import reduce
from random import choices


class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        super().__init__(name="Bob", author="Nobu", description="too lazy to explain")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """

        share_weight = reduce(
            lambda acc, move: acc + 1 if move == GameMove.SHARE else acc,
            opponent_history,
        )
        steal_weight = len(opponent_history) - share_weight

        return choices([GameMove.SHARE, GameMove.STEAL], (share_weight, steal_weight))[0]


# This line is required!
userGame = ImportedStrat()
