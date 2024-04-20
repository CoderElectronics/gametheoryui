"""
Template game theory strategy for GameTheoryUI.
by: Ari Stehney

Customize the class below with your metadata and fill out the play function, play history is available in the self.game_plays list.
"""

class ImportedStrat(GameStrategy):
    def __init__(self):
        super().__init__(name="Imported Strategy", author="Ari S.", description="my imported script file")

    def next_play(self):
        pass

# Do not change, userGame is a preset variable that will be imported.
userGame = ImportedStrat()