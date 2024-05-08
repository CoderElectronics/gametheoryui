"""
GameTheoryUI
by: Ari Stehney

a lovely little app for simulating the effectiveness of prisoners dilemna strategies.

Usage:
    Run the script with Python3.11

    $ python server.py

Data:
    scores.csv: Saves the scoreboard and game history from the Results tab on restarts.
    strategies.bin: Python strategies class-list save state to persist imported scripts.
"""

from nicegui import ui, events, app

import time, atexit, copy, io, uuid
import dill as pickle
import numpy as np
import pandas as pd
import os.path as path
import plotly.graph_objects as go
import plotly.express as px

from threading import Timer
from pprint import pprint
from fastapi.responses import StreamingResponse
from game_class import GameStrategy, GameMove

# Match engine states
strategies = []
match_games = []
match_active = False
match_results = pd.DataFrame(columns=['strategy', 'score'])

# Match status
match_parameters = {
    "num_rounds": 20,
    "steal_amount": 5,
    "steal_min_amount": 1,
    "share_amount": 3
}

match_plays = [[], []]
match_scores = [[], []]

def run_strategy_game(params, mgs):
    match_state = [[], []]
    scores = [[], []]

    for rnd in range(int(params["num_rounds"])):
        prev_match_state = copy.deepcopy(match_state)

        match_state[0].append(mgs[0].next_play(prev_match_state[0], prev_match_state[1]))
        match_state[1].append(mgs[1].next_play(prev_match_state[1], prev_match_state[0]))

    for rnd in zip(match_state[0], match_state[1]):
        if rnd[0] == GameMove.STEAL and rnd[1] == GameMove.STEAL:
            scores[0].append(params["steal_min_amount"])
            scores[1].append(params["steal_min_amount"])
        elif rnd[0] == GameMove.SHARE and rnd[1] == GameMove.SHARE:
            scores[0].append(params["share_amount"])
            scores[1].append(params["share_amount"])
        elif rnd[0] == GameMove.STEAL:
            scores[0].append(params["steal_amount"])
            scores[1].append(0)
        elif rnd[1] == GameMove.STEAL:
            scores[1].append(params["steal_amount"])
            scores[0].append(0)
        else:
            print("Invalid game state")
            pprint(rnd)

    return match_state, scores

"""
Score dataframe persistence functions.
"""
def load_dframe(pth, pth_strats):
    global match_results
    global strategies

    if path.exists(pth):
        print("Loading data from", pth)
        match_results = pd.read_csv(pth, header=0)
        print(match_results)
    else:
        print("No data, starting from scratch.")

    if path.exists(pth_strats):
        print("Loading strategy data from", pth_strats)
        with open(pth_strats, "rb") as f:
            strategies = pickle.load(f)
    else:
        print("No strategy data, starting from scratch.")

def save_dframe(pth, pth_strats):
    global match_results
    global strategies
    print("Saving data to", pth)

    match_results.to_csv(pth, index=False)
    with open(pth_strats, "wb") as f:
        pickle.dump(strategies, f)

def clear_matches():
    match_games.clear()
    match_active = False

    match_view.refresh()
    match_panel_view.refresh()

def exit_stop_server():
    save_dframe("scores.csv", "strategies.bin")
    exit()

"""
Random UI stuff
"""
class NullContextManager(object):
    def __init__(self, dummy_resource=None):
        self.dummy_resource = dummy_resource
    def __enter__(self):
        return self.dummy_resource
    def __exit__(self, *args):
        pass

dark_mode_status = 0
def dark_mode_toggle():
    global dark_mode_status
    if dark_mode_status == 1:
        ui.dark_mode().disable()
        dark_mode_status = 0
    else:
        ui.dark_mode().enable()
        dark_mode_status = 1

"""
Actual tabs and UI elements
"""
@ui.refreshable
def class_view(cls, actions=True, card=True):
    meta = cls.get_meta()
    with (ui.card() if card else NullContextManager()):
        ui.markdown('**{}** by {}<br>*{}*'.format(meta["name"], meta["author"], meta["description"]))

        if actions:
            with ui.row():
                # Add class
                def add_to_view():
                    match_games.append(cls)
                    match_view.refresh()

                with ui.button('', on_click=add_to_view):
                    ui.icon('add')
                    ui.label("add to match")

                # Remove class
                def remove_strategy():
                    strategies.remove(cls)
                    save_dframe("scores.csv", "strategies.bin")

                    match_view.refresh()
                    main_panel.refresh()

                with ui.button('', color='red', on_click=remove_strategy):
                    ui.icon('delete')
                    ui.label("Remove")

                ui.button('View results', on_click=lambda: panels.set_value('Results'))

# Home page match options and current match status section view
@ui.refreshable
def match_view(clss):
    global match_active, panels, match_parameters
    with ui.column():
        ui.markdown('####Match Queue')

        with ui.row():
            def start_match():
                global match_active, panels, match_scores, match_plays, match_parameters

                if len(match_games) == 2:
                    match_active = True
                    match_panel_view.refresh()

                    ui.notify('Match started, jumping to match tab', type='success')

                    match_plays, match_scores = run_strategy_game(match_parameters, match_games)

                    match_panel_view.refresh()

                    Timer(1, lambda: panels.set_value('Match View')).start()
                else:
                    ui.notify('Please select 2 teams before starting a match', type='warning')

            def set_game_param(param, e):
                global match_parameters
                print("Param updated: {}, {}".format(param, e))
                match_parameters[param] = e

            with ui.column():
                with ui.expansion('Match Options', icon='work'):
                    with ui.column():
                        with ui.row():
                            ui.number(label='Number of Rounds', value=match_parameters["num_rounds"],
                                      on_change=lambda e: set_game_param('num_rounds', e.value))

                            ui.number(label='Share Amount (pts/$)', value=match_parameters["share_amount"],
                                      on_change=lambda e: set_game_param('share_amount', e.value))

                        with ui.row():
                            ui.number(label='Single Steal Amount (pts/$)', value=match_parameters["steal_amount"],
                                      on_change=lambda e: set_game_param('steal_amount', e.value))

                            ui.number(label='Double Steal Amount (pts/$)', value=match_parameters["steal_min_amount"],
                                      on_change=lambda e: set_game_param('steal_min_amount', e.value))


                with ui.row():
                    ui.button('Start Match', on_click=start_match)

                    with ui.button('', on_click=clear_matches):
                        ui.icon('delete')

    with ui.splitter().style('width: 30rem') as splitter:
        with splitter.before:
            with ui.column().classes('pl-2'):
                if len(clss) > 0:
                    class_view(clss[0], actions=False, card=False)
                else:
                    ui.label("No match selected")
        with splitter.after:
            with ui.column().classes('pl-2'):
                if len(clss) == 2:
                    class_view(clss[1], actions=False, card=False)
                else:
                    ui.label("No match selected")

    return clss

# Results tab UI layout
@ui.refreshable
def results_view():
    global match_results

    with ui.row():
        # Match result visualization UI code
        if match_results[match_results.columns[0]].count() > 0:
            fig = px.bar(match_results, x='strategy', y='score')

            ui.plotly(fig)

            fig_scatter = px.scatter(match_results, x='strategy', y='score', size=list(match_results['score']), color=list(match_results['score']), hover_data=['score'])

            ui.plotly(fig_scatter)
        else:
            with ui.column():
                ui.markdown("#### No Data<br>")
                ui.markdown("Run some games to show stats.")

    with ui.row().classes('w-full'):
        ui.space()

        # Leaderboard clear function (mostly for debugging)
        def erase_scores():
            global match_results

            match_results = match_results.iloc[0:0]
            results_view.refresh()
            save_dframe("scores.csv", "strategies.bin")

        ui.button("Erase score board", on_click=erase_scores)

        # Excel export function
        file_name = f'scores-{uuid.uuid4()}.xlsx'
        download_path = f'/download/' + file_name
        @app.get(download_path)
        def download():
            global match_results

            df_out = io.BytesIO()
            match_results.to_excel(df_out)  # write to BytesIO buffer
            df_out.seek(0)

            headers = {'Content-Disposition': f'attachment; filename={file_name}'}
            return StreamingResponse(df_out, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

        ui.button('Download results', on_click=lambda: ui.download(download_path))

@ui.refreshable
def match_panel_view():
    global match_active, match_results, match_scores, match_plays

    if len(match_games) == 2 and match_active:
        with ui.row():
            """
            1st team visualization
            """
            fig_one = go.Figure(go.Waterfall(
                name="20", orientation="v",
                measure=["relative"]*len(match_scores[0]),
                x=["Play {}".format(x) for x in range(len(match_scores[0]))],
                textposition="outside",
                text=["Steal" if pl == GameMove.STEAL else "Share" for pl in match_plays[0]],
                y=match_scores[0],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig_one.update_layout(
                title=match_games[0].get_meta()["name"],
                showlegend=True
            )

            ui.plotly(fig_one)

            """
            2nd team visualization
            """
            fig_two = go.Figure(go.Waterfall(
                name="20", orientation="v",
                measure=["relative"] * len(match_scores[1]),
                x=["Play {}".format(x) for x in range(len(match_scores[1]))],
                textposition="outside",
                text=["Steal" if pl == GameMove.STEAL else "Share" for pl in match_plays[1]],
                y=match_scores[1],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig_two.update_layout(
                title=match_games[1].get_meta()["name"],
                showlegend=True
            )

            ui.plotly(fig_two)

        def add_match_scores():
            global match_results

            ndf = pd.DataFrame([
                {'strategy': match_games[0].get_meta()["name"], 'score': np.sum(match_scores[0])},
                {'strategy': match_games[1].get_meta()["name"], 'score': np.sum(match_scores[1])}
            ])

            match_results = pd.concat([match_results, ndf])
            print(match_results)
            results_view.refresh()

            save_dframe("scores.csv", "strategies.bin")

            ui.notify('Scores saved, jumping to leaderboard tab', type='success')
            Timer(2, lambda: panels.set_value('Results')).start()

        with ui.row().classes('w-full'):
            ui.space()
            ui.button('Save scores', on_click=add_match_scores)
    else:
        ui.markdown("#### No Match Started<br>")
        ui.markdown("Select two teams and start a match to view statistics.")

# Strategy class uploader
def handle_upload(e: events.UploadEventArguments):
    text = e.content.read().decode('utf-8')
    game_args = {}
    exec(text, {'GameStrategy': GameStrategy, 'GameMove': GameMove}, game_args)

    strategies.append(game_args['userGame'])
    main_panel.refresh()
    save_dframe("scores.csv", "strategies.bin")

# Home page layout
@ui.refreshable
def main_panel():
    global panels
    with ui.tab_panels(tabs, value='Game Classes').classes('w-full') as panels:
        with ui.tab_panel('Game Classes'):
            with ui.row().classes('w-full'):
                match_view(match_games)
                ui.space()
                ui.upload(on_upload=handle_upload).classes('')

            ui.space()
            ui.separator()

            with ui.row():
                for cl in strategies:
                    class_view(cl)

        with ui.tab_panel('Match View'):
            match_panel_view()

        with ui.tab_panel('Results'):
            results_view()

"""
Main app runtime loop
"""

if __name__ in {"__main__", "__mp_main__"}:
    # Register dataframe callbacks
    load_dframe("scores.csv", "strategies.bin")
    #atexit.register(lambda: save_dframe("scores.csv"))

    # Main window UI stuff
    with ui.header().classes(replace='row items-center w-full') as header:
        with ui.tabs().classes('w-full') as tabs:
            ui.tab('Game Classes')
            ui.tab('Match View')
            ui.tab('Results')
            ui.space()
            ui.button('UI Theme', icon='brightness_6', on_click=dark_mode_toggle).classes('mr-2')
            ui.button('Stop Server', icon='logout', on_click=exit_stop_server).classes('mr-2').props('color="red"')

    with ui.footer(value=False) as footer:
        ui.label('Footer')

    dark_mode_toggle()
    main_panel()
    ui.run()
