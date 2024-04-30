"""
Template game theory strategy for GameTheoryUI.
by: Ari Stehney

Customize the class below with your metadata and fill out the play function, play history is available in the self.game_plays list.
"""

class ImportedStrat(GameStrategy):
    def __init__(self):
        super().__init__(name="Imported Strategy", author="Ari S.", description="my imported script file")

    # history of your moves and if you won
    def next_play(history):
        return # {

        # }[[0, 1, 2],[0,1,2]]
        pass

# Do not change, userGame is a preset variable that will be imported.
userGame = ImportedStrat()