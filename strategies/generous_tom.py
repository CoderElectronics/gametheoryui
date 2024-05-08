class ImportedStrat(GameStrategy):
    def __init__(self) -> None:
        super().__init__(name="Generous Tom", author="Nobu", description="Tom is very, very, very generous.")

    def next_play(self, player_history: list[GameMove], opponent_history: list[GameMove]) -> GameMove:
        """
        :param player_history: List of your moves
        :param opponent_history: List of the opponent's moves
        :return: Your next move
        """
        return GameMove.STEAL if sum(player_history[-6:-1]) == 0 else GameMove.SHARE

# This line is required!
userGame = ImportedStrat()

