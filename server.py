from nicegui import ui, events
import time, atexit
import dill as pickle
import numpy as np
import pandas as pd
import os.path as path
from threading import Timer
import plotly.graph_objects as go
import plotly.express as px

from game_class import GameStrategy, DemoStrat0, DemoStrat1

# Match engine states
strategies = [DemoStrat0(), DemoStrat1()]
match_games = []
match_active = False
match_results = pd.DataFrame(columns=['strategy', 'score'])
server_process = None

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

# Random utility stuff
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

def exit_stop_server():
    save_dframe("scores.csv", "strategies.bin")
    exit()

# Data views
@ui.refreshable
def class_view(cls, actions=True, card=True):
    meta = cls.get_meta()
    with (ui.card() if card else NullContextManager()):
        ui.markdown('**{}** by {}<br>*{}*'.format(meta["name"], meta["author"], meta["description"]))

        if actions:
            with ui.row():
                def add_to_view():
                    match_games.append(cls)
                    match_view.refresh()

                with ui.button('', on_click=add_to_view):
                    ui.icon('add')
                    ui.label("add to match")
                ui.button('View results', on_click=lambda: panels.set_value('Results'))

@ui.refreshable
def match_view(clss):
    global match_active, panels
    with ui.column():
        ui.markdown('####Match Queue')

        with ui.row():
            def start_match():
                global match_active, panels
                if len(match_games) == 2:
                    match_active = True
                    match_panel_view.refresh()

                    ui.notify('Match started, jumping to match tab', type='success')
                    Timer(2, lambda: panels.set_value('Match View')).start()
                else:
                    ui.notify('Please select 2 teams before starting a match', type='warning')

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

@ui.refreshable
def results_view():
    global match_results
    with ui.row():
        fig = px.bar(match_results, x='strategy', y='score')

        ui.plotly(fig)

@ui.refreshable
def match_panel_view():
    global match_active
    global match_results

    if len(match_games) == 2 and match_active:
        with ui.row():
            with ui.column():
                fig = go.Figure(go.Waterfall(
                    name="20", orientation="v",
                    measure=["relative", "relative", "total", "relative", "relative", "total"],
                    x=["Play {}".format(x) for x in range(5)],
                    textposition="outside",
                    text=["+60", "+80", "", "-40", "-20", "Total"],
                    y=[60, 80, 0, -40, -20, 0],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))

                fig.update_layout(
                    title=match_games[0].get_meta()["name"]+" vs. "+match_games[1].get_meta()["name"],
                    showlegend=True
                )

                ui.plotly(fig)

            with ui.column().classes("pl-2"):
                ui.markdown("####Match Plays")
                with ui.timeline(side='right').classes('pl-3'):
                    ui.timeline_entry('+15 to Demo Strategy 0 by fair split.',
                                      title='Play 0',
                                      subtitle='Demo Strategy 0')
                    ui.timeline_entry('+5 to Demo Strategy 1 by fair split.',
                                      title='Play 1',
                                      subtitle='Demo Strategy 1')

            def add_fake_scores():
                global match_results
                ndf = pd.DataFrame([{'strategy': obj.get_meta()["name"], 'score': np.random.randint(0, 100)} for obj in strategies])

                match_results = pd.concat([match_results, ndf])
                print(match_results)
                results_view.refresh()

            ui.button('Register scores', on_click=add_fake_scores)
    else:
        ui.markdown("#### No Match Started<br>")
        ui.markdown("Select two teams and start a match to view statistics.")

# Strategy class uploader
def handle_upload(e: events.UploadEventArguments):
    text = e.content.read().decode('utf-8')
    game_args = {}
    exec(text, {'GameStrategy': GameStrategy}, game_args)

    strategies.append(game_args['userGame'])
    print(strategies)
    main_panel.refresh()

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

# App run loop
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
            ui.button('Stop Server', icon='logout', on_click=exit_stop_server).classes('mr-2')

    with ui.footer(value=False) as footer:
        ui.label('Footer')

    dark_mode_toggle()
    main_panel()
    ui.run()
