import json
import time

import pandas as pd
import numpy as np

import plotly
from plotly.offline import plot
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import base64

def get_as_base64(player_name):
    """Return local .png image for player."""   
    try:
        with open('./player_images/{}.png'.format(player_name), 'rb') as f:
            image = f.read()
    except:
        with open('./player_images/Ali Gabr.png', 'rb') as f:
            image = f.read()
    return(base64.b64encode(image).decode())

graph_styles = {
    'light':{
        'bg_color': 'rgb(239, 239, 239)',
        'color': 'rgb(57, 57, 57)',
        'titlefont': {
            'size': 25,
            'family': 'Bebas Neue, Roboto Condensed, Roboto, Helvetica Narrow, Arial Narrow, Helvetica, Arial',
            'color': 'rgb(68, 68, 68)'
        },
        'axis_color': 'rgb(68, 68, 68)',
        'legendfont': {
            'color': 'rgb(68, 68, 68)'
        },
        'grid_color': 'rgb(180, 180, 180)'
    },
    
    'dark':{
        'bg_color': 'rgb(57, 57, 57)',
        'color': 'rgb(239, 239, 239)',
        'titlefont': {
            'size': 25,
            'family': 'Bebas Neue, Roboto Condensed, Roboto, Helvetica Narrow, Arial Narrow, Helvetica, Arial',
            'color': 'rgb(255, 255, 255)'
        },
        'axis_color': 'rgb(180, 180, 180)',
        'legendfont': {
            'color': 'rgb(180, 180, 180)'
        },
        'grid_color': 'rgb(100, 100, 100)'
    },
    
}

field_style = {
    '1' : {
        'fill_color': 'rgba(45, 134, 45, 1)',
        'line_color': 'rgba(128, 0, 128, 1)'
    },

    '2' : {
        'fill_color': 'rgba(162, 185, 97, 1)',
        'line_color': 'rgba(28, 32, 14, 1)'
    },
}

field_theme = '2'

matches = pd.read_json('./data/matches/43.json', encoding='utf-8').sort_values('match_id')

matches =  (matches
            .assign(home = matches.home_team.apply(lambda x: x['home_team_name']),
                    away = matches.away_team.apply(lambda x: x['away_team_name']),
                    home_score = matches.home_score.astype(int),
                    away_score = matches.away_score.astype(int),
                    match_id = matches.match_id.astype(int),
                    stage = ((['Group Stage'] * 47) + (['Round of 16'] * 8)
                            + (['Quarter Final'] * 4) + (['Semi Final'] * 2)
                            + (['Third Place Match']) + (['Final'])),
                    description = lambda x: x['stage'] + ' : ' + x['home'] + ' vs ' + x['away'],
                    match_date = pd.to_datetime(matches.match_date),
                    display_date = lambda x: x.match_date.dt.strftime('%d %B %Y').str.strip('0')))

team_colors = {
    'home': 'rgba(255,77,77, 1)',
    'away': 'rgba(77,77,255, 1)'
}

# XG PLOT

def create_xg_plot(shots_df, events, top_xg, match_info, theme):
    """Return XG plot figure"""
    
    shots_df = shots_df.sort_values(['period','dec_time'])

    trace1 = go.Scatter(
                    x = [0] + list(shots_df[shots_df.team == match_info['teams']['home']].dec_time) + [events.minute.max() + 1],
                    y = [0] + list(shots_df[shots_df.team == match_info['teams']['home']].cum_xg) + [list(shots_df[shots_df.team == match_info['teams']['home']].cum_xg)[-1]],
                    line = dict(color = team_colors['home'], shape='hv', width=2),
                    mode = 'lines',
                    name = match_info['teams']['home'].upper(),
                    text = [''] + list(shots_df[shots_df.team == match_info['teams']['home']].hover_text) + [''],
                    hoverinfo = 'text'
    )

    trace2 = go.Scatter(
                    x = [0] + list(shots_df[shots_df.team == match_info['teams']['away']].dec_time) + [events.minute.max() + 1],
                    y = [0] + list(shots_df[shots_df.team == match_info['teams']['away']].cum_xg) + [list(shots_df[shots_df.team == match_info['teams']['away']].cum_xg)[-1]],
                    line = dict(color = team_colors['away'], shape='hv', width=2),
                    mode = 'lines',
                    name = match_info['teams']['away'].upper(),
                    text = [''] + list(shots_df[shots_df.team == match_info['teams']['away']].hover_text) + [''],
                    hoverinfo = 'text'
    )

    #to plot top three player histogram
    top_xg = top_xg.sort_values('total_xg', ascending=False)
    trace3 = go.Bar(
                x = top_xg.name,
                y = top_xg.total_xg,
                marker=dict(
                    color = [team_colors['home'] if team == match_info['teams']['home'] else team_colors['away'] for team in top_xg.team],
                    line=dict(
                        color=graph_styles[theme]['axis_color'],
                        width=1.5),
                    opacity = 0.8
                    ),
#                 opacity=1,
                name='Top Players by XG',
#                 text = top_xg.hover_text,
                text = top_xg.name.apply(lambda x: x.split()[-1]),
                hoverinfo = 'x',
                textposition = 'inside',
                textfont = {
                    'color': graph_styles[theme]['axis_color']
                },
                showlegend=False,
                xaxis='x2',
                yaxis='y2',
                )


    shot_trace_1 = go.Scatter(
                        x = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['home'])].dec_time,
                        y = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['home'])].cum_xg + 0.15,
                        mode = 'markers',
                        marker = {
                                'size': 10,
                                'color': team_colors['home'],
                                'opacity': 0.8,
                                 },
                        text = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['home'])].hover_text,
                        hoverinfo = 'text',
                        name = '{}'.format(match_info['teams']['home']),
                        showlegend=False,
                        )

    shot_trace_2 = go.Scatter(
                        x = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['away'])].dec_time,
                        y = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['away'])].cum_xg + 0.15,
                        mode = 'markers',
                        marker = {
                                'size': 10,
                                'color': team_colors['away'],
                                'opacity': 0.8,
                                 },
                        text = shots_df[(shots_df.outcome == 'Goal') & (shots_df.team == match_info['teams']['away'])].hover_text,
                        hoverinfo = 'text',
                        name = '{}'.format(match_info['teams']['away']),
                        showlegend=False,
                        )

    #for line chart, we'll add two traces into data list
    data = [trace1, trace2, shot_trace_1, shot_trace_2, trace3]

    layout = go.Layout(
#             title = 'EXPECTED GOALS (xG) CHART',
            plot_bgcolor = graph_styles[theme]['bg_color'],
            paper_bgcolor = graph_styles[theme]['bg_color'],
            titlefont= {
                    'color': graph_styles[theme]['titlefont']['color'],
#                     'size': graph_styles[theme]['titlefont']['size'],
    #                 'family': graph_styles[theme]['titlefont']['family'],
                    },
    #         font = {'size': 30},
            legend =  {
                'orientation': 'h',
                'y': 0.92, 'x': 0.1, 
                'xanchor': 'center',
                'font': {
#                         'size': 50,
                        'color': graph_styles[theme]['legendfont']['color']
                    }
                  },
    #     width = 3029,
    #     height = 800,
        xaxis=dict(
            domain=[0, 0.75],
            title = 'Minutes' ,
            color = graph_styles[theme]['axis_color'],
            gridcolor = graph_styles[theme]['grid_color'],
            tickvals = np.linspace(0, 120, 9),
    #         tickfont = {'size': 20}
        ),
        yaxis=dict(
            title = 'Expected Goals (xG)',
            domain = [0, 0.8],
            color = graph_styles[theme]['axis_color'],
            gridcolor = graph_styles[theme]['grid_color'],
    #         tickfont = {'size': 20}
        ),

        xaxis2=dict(
            domain=[0.87, 1],
            color = graph_styles[theme]['axis_color'],
            showticklabels = False,
#             gridcolor = graph_styles[theme]['grid_color'],
    #         tickfont = {'size': 20}
        ),
        yaxis2=dict(
            domain=[0.05, 0.75],
            anchor='x2',
            title='Total Expected Goals (xG)',
            color = graph_styles[theme]['axis_color'],
            gridcolor = graph_styles[theme]['grid_color'],
    #         tickfont = {'size': 20}
        ),
        margin = {
            't': 0,
            'r': 5,
            'l': 45,
            'b': 35,
        },
        hovermode = 'closest',
        annotations = [
        {
                'x': 0.5,
                'y': 1.0,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {
                        'family': graph_styles[theme]['titlefont']['family'],
                        'size': graph_styles[theme]['titlefont']['size'],
                        'color': graph_styles[theme]['titlefont']['color'],
                },
                'text': 'EXPECTED GOALS (xG) CHART',
        },
        {
                'x': 0.5,
                'y': 0.875,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {
                        'family': graph_styles[theme]['titlefont']['family'],
                        'size': 20,
                        'color': graph_styles[theme]['titlefont']['color'],
                },
                'text': '{} {:.2f} - {:.2f} {}'.format(match_info['teams']['home'],
                                                       shots_df[shots_df.team == match_info['teams']['home']].cum_xg.max(),
                                                       shots_df[shots_df.team == match_info['teams']['away']].cum_xg.max(),
                                                       match_info['teams']['away']),
        },
        ]
    )
    
    
    return({'data': data, 'layout': layout})

# plot(create_xg_plot(), 'test_plot.html', auto_open=True)

# Shot Plot

def create_shot_scatter(shots_df, match_info, team):
    """Create shot scatter for home/away team."""
    shots_df_team = shots_df[(shots_df.team == match_info['teams'][team]) & 
                            (shots_df.location.apply(lambda x: x[0]) > 60)]
    shot_trace = go.Scatter(
                        x = shots_df_team.location.apply(lambda x: x[0]),
                        y = shots_df_team.location.apply(lambda x: x[1]),
                        mode = 'markers',
                        marker = {
                                'size': 5 + (20 * shots_df_team.xg),
                                'color': shots_df_team.shot_color,
                                'opacity': 0.8
                                 },
                        text = shots_df_team.hover_text,
                        hoverinfo = 'text',
                        name = '{}'.format(match_info['teams'][team].upper())
                        )
    return shot_trace

def create_shot_plot(shots_df, match_info, theme):
    """Create shot plot for both teams."""
    
    trace_home = create_shot_scatter(shots_df, match_info, 'home')
    trace_away = create_shot_scatter(shots_df, match_info, 'away')

    data = [trace_home, trace_away]

    half_field = {
            'type': 'rect',
            'x0':60,
            'x1':120,
            'y0':0,
            'y1':80,
            'line': {
                'color': graph_styles[theme]['titlefont']['color']
                },
            'layer': 'below',
            'fillcolor': field_style[field_theme]['fill_color']
            }

    penalty = {
                'type': 'rect',
                'x0':102,
                'x1':120,
                'y0':18,
                'y1':62,
                'line': {
                    'color': graph_styles[theme]['titlefont']['color']
                    },
                'layer': 'below'
                }

    goal = {
            'type': 'rect',
            'x0':114,
            'x1':120,
            'y0':30,
            'y1':50,
            'line': {
                'color': graph_styles[theme]['titlefont']['color']
                },
            'layer': 'below'
            }

    post = {
            'type': 'rect',
            'x0':120,
            'x1':122,
            'y0':36,
            'y1':44,
            'line': {
                'color': graph_styles[theme]['titlefont']['color']
                },
            'layer': 'below'
            }

    centre_line = {
                    'type': 'line',
                    'x0':60,
                    'x1':60,
                    'y0':0,
                    'y1':80,
                    'line': {
                        'color': graph_styles[theme]['titlefont']['color']
                        },
                    'layer': 'below'
                }

    shapes = [half_field, penalty, goal,
              centre_line, post]

    layout = {
        'shapes': shapes,
        'hovermode': 'closest',
        'yaxis': {'range': [82,-2], 'visible': False},
        'xaxis': {'range': [57,123], 'visible': False},
        'plot_bgcolor': graph_styles[theme]['bg_color'],
        'paper_bgcolor': graph_styles[theme]['bg_color'],
        'legend': {
                'orientation': 'h',
                'y': 1.08, 'x': 0.5, 
                'xanchor': 'center',
                'font': {
    #                     'size': 50,
                    'color': graph_styles[theme]['legendfont']['color']
                    }
                  },
        'titlefont': {
    #                 'size': 30,
#                     'family': 'ObelixPro',
                    'color': graph_styles[theme]['titlefont']['color'],
                    },
    #     'paper_bgcolor': 'rgba(0, 0, 0, 0.5)',
    #     'height': 800,
    #     'width': 2500,
        'margin' : {
            't': 60,
            'r': 5,
            'l': 5,
            'b': 5
        },
        'annotations': [
                {
                        'x': 0.5,
                        'y': 1.18,
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                                'family': graph_styles[theme]['titlefont']['family'],
                                'size': graph_styles[theme]['titlefont']['size'],
                                'color': graph_styles[theme]['titlefont']['color'],
                        },
                        'text': 'SHOT PLOT',
                },
        ]
        # 'title': 'MATCH SHOT CHART'
    }
    
    
    return({'data': data, 'layout': layout})

# plot(create_shot_plot(), 'test_plot.html', auto_open=True)

# Spider Chart

angles = {
    'dribble': ([0, 0, 22.5, 22.5], 'rgba(240, 18, 190, 1)', 'Dribbles', 'Possession', 'DRIBBLES'),
    'pass_length': ([22.5, 22.5, 45, 45], 'rgba(240, 18, 190, 1)', 'Average Pass Length', 'Possession', 'APL'),
    'progressive_passes': ([45, 45, 67.5, 67.5], 'rgba(240, 18, 190, 1)', 'Progressive Passes', 'Possession', 'PP'),
    'passes': ([67.5, 67.5, 90, 90], 'rgba(240, 18, 190, 1)', 'Passes', 'Possession', 'PASSES'),
    'is_cross': ([90, 90, 112.5, 112.5], 'rgba(0, 116, 217, 1)', 'Crosses', 'Attack', 'CROSSES'),
    'sog': ([112.5, 112.5, 135, 135], 'rgba(0, 116, 217, 1)', 'Shots on Goal', 'Attack', 'SOG'),
    'xg': ([135, 135, 157.5, 157.5], 'rgba(0, 116, 217, 1)', ' Expected Goals(xG)', 'Attack', 'xG'),
    'goals': ([157.5, 157.5, 180, 180], 'rgba(0, 116, 217, 1)', 'Goals', 'Attack', 'GOALS'),
    'pressure': ([180, 180, 202.5, 202.5], 'rgba(255, 133, 27, 1)', 'Defensive Pressure', 'Defense', 'PRESSURE'),
    'clearance': ([202.5, 202.5, 225, 225], 'rgba(255, 133, 27, 1)', 'Clearances', 'Defense', 'CL'),
    'block': ([225, 225, 247.5, 247.5], 'rgba(255, 133, 27, 1)', 'Blocks', 'Defense', 'BLOCKS'),
    'interception': ([247.5, 247.5, 270, 270], 'rgba(255, 133, 27, 1)', 'Interceptions', 'Defense', 'INT'),
    'dispossessed': ([270, 270, 292.5, 292.5], 'rgba(61, 153, 112, 1)', 'Dispossessions', 'Aggression', 'DP'),
    'foul_committed': ([292.5, 292.5, 315, 315], 'rgba(61, 153, 112, 1)', 'Fouls Committed', 'Aggression', 'FC'),
    'foul_won': ([315, 315, 337.5, 337.5], 'rgba(61, 153, 112, 1)', 'Fouls Won', 'Aggression', 'FW'),
    'headers': ([337.5, 337.5, 360, 360], 'rgba(61, 153, 112, 1)', 'Attacking Headers', 'Aggression', 'HEADERS'),
}

# radar_angles = {key: value[0][2] - 11.25 for key, value in angles.items()}

radar_angles = {'dribble': 11.25,
                 'pass_length': 33.75,
                 'progressive_passes': 56.25,
                 'passes': 78.75,
                 'is_cross': 101.25,
                 'sog': 123.75,
                 'xg': 146.25,
                 'goals': 168.75,
                 'pressure': 191.25,
                 'clearance': 213.75,
                 'block': 236.25,
                 'interception': 258.75,
                 'dispossessed': 281.25,
                 'foul_committed': 303.75,
                 'foul_won': 326.25,
                 'headers': 348.75}

def create_spider_chart(events, shots_df, passing_df, match_info, theme):
    """Create spider chart for tracking teams' performance."""
    
    passing_stats = (passing_df[passing_df.outcome.isnull()]
                     .groupby('team')
                     .agg({
                         'id': 'count',
                         'length': 'mean',
                         'angle': lambda x: np.sum(np.where((x<90) & (x>-90), 1, 0))
                     })
                     .rename(columns = {'id': 'passes',
                                        'length': 'pass_length',
                                        'angle': 'progressive_passes'}))

    crossing_stats = (passing_df
                     .groupby('team')
                     .is_cross.sum())

    req_cols = ['Pressure','Dribble','Block','Foul Committed','Clearance','Foul Won','Interception','Dispossessed']

    overall_stats = (events
                    .assign(team_name = lambda x: x['team'].apply(lambda y: y['name']),
                            event_type = lambda x: x['type'].apply(lambda y: y['name']))
                    .groupby('team_name')
                    .event_type.value_counts()
                    .unstack()
                    .loc[:, req_cols]
                    .rename_axis('team'))

    shooting_stats = (shots_df
                      .groupby('team')
                      .agg({
                          'xg': 'sum',
                          'outcome': {'goals': lambda x: np.sum(np.where(x == 'Goal', 1, 0)),
                                      'sog': lambda x: np.sum(np.where(x.isin(['Goal','Post','Saved']), 1, 0))},
                          'body_part': lambda x: np.sum(np.where(x == 'Head', 1, 0))
                      }))

    shooting_stats.columns = ['xg','goals','sog','headers']

    team_stats = (overall_stats
                 .join(shooting_stats)
                 .join(passing_stats)
                 .join(crossing_stats)
                 .rename(columns=lambda x: x.replace(' ', '_').lower())
                 .transpose()
                 .assign(angle = lambda x: x.index.map(lambda x: radar_angles[x]).values)
                 .sort_values('angle')
                 .drop('angle', 1))

    plot_stats = (team_stats.div(team_stats.sum(axis=1), axis=0)
                  .fillna(0))

    plot_stats = (plot_stats
                  .assign(angle = lambda x: x.index.map(lambda x: radar_angles[x]).values,
                          abbv = lambda x: x.index.map(lambda x: angles[x][4]).values,
                          attribute = lambda x: x.index.map(lambda x: angles[x][2]).values,
                          style_type = lambda x: x.index.map(lambda x: angles[x][3]).values,
                          style_col = lambda x: x.index.map(lambda x: angles[x][1]).values)
                  .sort_values('angle'))

    plot_attributes = list(plot_stats.attribute.values) + [plot_stats.attribute.values[0]]

    radar_1 = go.Scatterpolar(
                        r = list(plot_stats[match_info['teams']['home']].values) + [plot_stats[match_info['teams']['home']].values[0]],
                        theta = plot_attributes,
                        fill = 'toself',
    #                     fillcolor = 'rgba(255,77,77, 0.5)',
                        line = {
                            'color': team_colors['home']
                        },
                        name = match_info['teams']['home'],
    #                     legendgroup = '{}'.format(angles[idx][3]),
    #                     showlegend = True if idx in ['passes','xg','pressure','headers'] else False,
                        text = (plot_stats.attribute.values + ' : ' + team_stats[match_info['teams']['home']].map('{:.1f}'.format)),
                        hoverinfo = 'text'
    )

    radar_2 = go.Scatterpolar(
                        r = list(plot_stats[match_info['teams']['away']].values) + [plot_stats[match_info['teams']['away']].values[0]],
                        theta = plot_attributes,
                        fill = 'toself',
    #                     fillcolor = 'rgba(77,77,255, 0.5)',
                        line = {
                            'color': team_colors['away']
                        },
                        name = match_info['teams']['away'],
    #                     legendgroup = '{}'.format(angles[idx][3]),
    #                     showlegend = True if idx in ['passes','xg','pressure','headers'] else False,
                        text = (plot_stats.attribute.values + ' : ' + team_stats[match_info['teams']['away']].map('{:.1f}'.format)),
                        hoverinfo = 'text'
    )

    labels = go.Scatterpolar(
                        r = [1.2] * 16,
                        theta = plot_stats.attribute.values,
                        mode = 'text',
                        text = plot_stats.abbv.values,
                        textfont = {
    #                             'size': 12,
                                'color': plot_stats.style_col.values
                                },
                        hoverinfo = 'theta',
                        showlegend= False)

    data = [radar_1, radar_2, labels]

    layout = go.Layout(
                      polar = {
                          'bgcolor': graph_styles[theme]['bg_color'],
                          'angularaxis': {
                              'rotation': 11.25,
                              'showline': False,
                              'showticklabels': False,
                              'color': graph_styles[theme]['axis_color'],
                              'gridcolor': graph_styles[theme]['grid_color'],
                          },
                          'radialaxis': {
                              'range': [0, 1.2],
                              'tickvals': [0, 0.2, 0.4, 0.6, 0.8, 1],
                              'showline': True,
                              'color': graph_styles[theme]['axis_color'],
                              'gridcolor': graph_styles[theme]['grid_color'],
                          }
                      },
                      hovermode = 'closest',
                      showlegend = False,
                      margin = {
                          'l': 10,
                          'r': 10,
                          't': 60,
                          'b': 10,
                      },
                    plot_bgcolor = graph_styles[theme]['bg_color'],
                    paper_bgcolor = graph_styles[theme]['bg_color'],
    #                 polar = {
    #                     'radialaxis': {
    #                             'visible': True,
    #                             'tickvals': [1],
    #                             'showline': False,
    #                             'showticklabels': False
    #                     },
    #                     'angularaxis': {
    #                             'visible': True,
    #                             'showline': False,
    #                             'showticklabels': False,
    #                             'tickvals': np.arange(0, 360, 22.5)
    #                     }
    #                 },
    #                 showlegend = False,
    #                 legend = {'font':{'size': 50}},
    #                 width = 1100,
    #                 height = 1100,
                    titlefont = {
    #                         'size': 40,
#                             'family': 'ObelixPro',
                            'color': graph_styles[theme]['titlefont']['color'],
                            },
                    annotations = [
                    {
                            'x': 0.5,
                            'y': 1.18,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                    'family': graph_styles[theme]['titlefont']['family'],
                                    'size': graph_styles[theme]['titlefont']['size'],
                                    'color': graph_styles[theme]['titlefont']['color'],
                            },
                            'text': 'TEAM PERFORMANCE RADAR',
                    },
                    {
                            'x': 1,
                            'y': 1,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                    # 'family': graph_styles[theme]['titlefont']['family'],
                                    # 'size': graph_styles[theme]['titlefont']['size'],
                                    'color': graph_styles[theme]['titlefont']['color'],
                            },
                            'text': '<b>POSSESSION</b>',
                    },                    {
                            'x': 0,
                            'y': 1,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                    # 'family': graph_styles[theme]['titlefont']['family'],
                                    # 'size': graph_styles[theme]['titlefont']['size'],
                                    'color': graph_styles[theme]['titlefont']['color'],
                            },
                            'text': '<b>ATTACK</b>',
                    },                    {
                            'x': 0,
                            'y': 0,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                    # 'family': graph_styles[theme]['titlefont']['family'],
                                    # 'size': graph_styles[theme]['titlefont']['size'],
                                    'color': graph_styles[theme]['titlefont']['color'],
                            },
                            'text': '<b>DEFENSE</b>',
                    },                    {
                            'x': 1,
                            'y': 0,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {
                                    # 'family': graph_styles[theme]['titlefont']['family'],
                                    # 'size': graph_styles[theme]['titlefont']['size'],
                                    'color': graph_styles[theme]['titlefont']['color'],
                            },
                            'text': '<b>AGGRESSION</b>',
                    },

                    ]
    #                 title = '{}'.format(team_stats.columns[1].upper())
    )
    
    
    return({'data': data, 'layout': layout})

# plot(create_spider_chart(), 'test_plot.html', auto_open=False)

# Performance Radars

def create_performance_radars():
    """Create performance radars for home and away team."""
    passing_stats = (passing_df[passing_df.outcome.isnull()]
                     .groupby('team')
                     .agg({
                         'id': 'count',
                         'length': 'mean',
                         'angle': lambda x: np.sum(np.where((x<90) & (x>-90), 1, 0))
                     })
                     .rename(columns = {'id': 'passes',
                                        'length': 'pass_length',
                                        'angle': 'progressive_passes'}))

    crossing_stats = (passing_df
                     .groupby('team')
                     .is_cross.sum())

    req_cols = ['Pressure','Dribble','Block','Foul Committed','Clearance','Foul Won','Interception','Dispossessed']

    overall_stats = (events
                    .assign(team_name = lambda x: x['team'].apply(lambda y: y['name']),
                            event_type = lambda x: x['type'].apply(lambda y: y['name']))
                    .groupby('team_name')
                    .event_type.value_counts()
                    .unstack()
                    .loc[:, req_cols]
                    .rename_axis('team'))

    shooting_stats = (shots_df
                      .groupby('team')
                      .agg({
                          'xg': 'sum',
                          'outcome': {'goals': lambda x: np.sum(np.where(x == 'Goal', 1, 0)),
                                      'sog': lambda x: np.sum(np.where(x.isin(['Goal','Post','Saved']), 1, 0))},
                          'body_part': lambda x: np.sum(np.where(x == 'Head', 1, 0))
                      }))

    shooting_stats.columns = ['xg','goals','sog','headers']

    team_stats = (overall_stats
                 .join(shooting_stats)
                 .join(passing_stats)
                 .join(crossing_stats)
                 .rename(columns=lambda x: x.replace(' ', '_').lower())
                 .transpose())

    plot_stats = team_stats.div(team_stats.sum(axis=1), axis=0)

    traces_home = []
    traces_away = []
    for idx, row in plot_stats.iterrows():
        trace_home = go.Scatterpolar(
                            r = [0, row[match_info['teams']['home']], row[match_info['teams']['home']], 0],
                            theta = angles[idx][0],
                            mode = 'lines',
                            fill = 'toself',
                            fillcolor = angles[idx][1],
                            line = {
                                'color': 'white'
                            },
                            text = '{}: {:.1f}'.format(angles[idx][2], row[match_info['teams']['home']]),
                            hoverinfo = 'text')
        traces_home.append(trace_home)

        trace_away = go.Scatterpolar(
                            r = [0, row[match_info['teams']['away']], row[match_info['teams']['away']], 0],
                            theta = angles[idx][0],
                            mode = 'lines',
                            fill = 'toself',
                            fillcolor = angles[idx][1],
                            line = {
                                'color': 'white'
                            },
                            text = '{}: {:.1f}'.format(angles[idx][2], row[match_info['teams']['away']]),
                            hoverinfo = 'text')

        traces_away.append(trace_away)

        trace_label = go.Scatterpolar(
                            r = [1.3],
                            theta = [np.mean(angles[idx][0])],
                            mode = 'text',
                            text = angles[idx][2],
                            textfont = {
#                                 'size': 20,
                                'color': graph_styles[theme]['axis_color']
                            },
                            hoverinfo = 'none')

        traces_home.append(trace_label)
        traces_away.append(trace_label)

    layout = go.Layout(
                    polar = {
                        'bgcolor': graph_styles[theme]['bg_color'],
                        'radialaxis': {
                                'visible': True,
                                'tickvals': [1],
                                'showline': False,
                                'showticklabels': False,
                                'color': graph_styles[theme]['axis_color'],
                                'gridcolor': graph_styles[theme]['grid_color'],
                        },
                        'angularaxis': {
                                'visible': True,
                                'showline': False,
                                'showticklabels': False,
                                'tickvals': np.arange(0, 360, 22.5),
                                'color': graph_styles[theme]['axis_color'],
                                'gridcolor': graph_styles[theme]['grid_color'],
                        }
                    },
                    showlegend = False,
    #                 width = 1100,
    #                 height = 1100,
                    titlefont = {
    #                         'size': 40,
    #                         'family': 'ObelixPro',
                            'color': graph_styles[theme]['titlefont']['color'],
                            },
                    plot_bgcolor = graph_styles[theme]['bg_color'],
                    paper_bgcolor = graph_styles[theme]['bg_color'],
                    margin = {
                          'l': 10,
                          'r': 10,
                          't': 10,
                          'b': 10,
                      },
    #                 title = '{}'.format(team_stats.columns[0].upper())
    )

    return(({'data': traces_home, 'layout': layout}, {'data': traces_away, 'layout': layout}))

# PASSING NETWORK MAPS

import copy

def create_full_field(theme):
    field = {
            'type': 'rect',
            'x0':0,
            'x1':80,
            'y0':0,
            'y1':120,
            'line': {
                'color': graph_styles[theme]['titlefont']['color']
                },
            'layer': 'below',
            'fillcolor': field_style[field_theme]['fill_color']
            }

    left_penalty = {
                    'type': 'rect',
                    'y0':0,
                    'y1':18,
                    'x0':18,
                    'x1':62,
                    'line': {
                        'color': graph_styles[theme]['titlefont']['color']
                        },
                    'layer': 'below'
                    }

    right_penalty = {
                    'type': 'rect',
                    'y0':102,
                    'y1':120,
                    'x0':18,
                    'x1':62,
                    'line': {
                        'color': graph_styles[theme]['titlefont']['color']
                        },
                    'layer': 'below'
                    }
    left_goal = {
                'type': 'rect',
                'y0':0,
                'y1':6,
                'x0':30,
                'x1':50,
                'line': {
                    'color': graph_styles[theme]['titlefont']['color']
                    },
                'layer': 'below'
                }

    right_goal = {
                'type': 'rect',
                'y0':114,
                'y1':120,
                'x0':30,
                'x1':50,
                'line': {
                    'color': graph_styles[theme]['titlefont']['color']
                    },
                'layer': 'below'
                }

    left_post = {
                'type': 'rect',
                'y0':-2,
                'y1':0,
                'x0':36,
                'x1':44,
                'line': {
                    'color': graph_styles[theme]['titlefont']['color']
                    },
                'layer': 'below'
                }

    right_post = {
                'type': 'rect',
                'y0':120,
                'y1':122,
                'x0':36,
                'x1':44,
                'line': {
                    'color': graph_styles[theme]['titlefont']['color']
                    },
                'layer': 'below'
                }

    centre_line = {
                    'type': 'line',
                    'y0':60,
                    'y1':60,
                    'x0':0,
                    'x1':80,
                    'line': {
                        'color': graph_styles[theme]['titlefont']['color']
                        },
                    'layer': 'below'
                }

    full_field_shapes = [field, left_penalty, right_penalty, left_goal, 
                         right_goal, centre_line, left_post, right_post]

    duplicate_shapes = []
    for shape in full_field_shapes:
        new_shape = copy.deepcopy(shape)
        new_shape['xref'] = 'x2'
        new_shape['yref'] = 'y2'
        duplicate_shapes.append(new_shape)

    full_field = full_field_shapes + duplicate_shapes
    return full_field

def create_map_traces(team, positions, pass_combinations, starting, match_info):
    """Create passing network map traces for team."""
    position_team = positions[positions.id.isin(starting[team])]

    formation_team = go.Scatter(
                                x = position_team.y_pos,
                                y = position_team.x_pos,
                                name = match_info['teams'][team],
                                mode = 'markers+text',
                                marker = {
                                        'size': 40 * position_team.pass_frac,
                                        'color': team_colors[team],
                                        'opacity': 1
                                    },
                                textfont = {
                                    'color': 'white',
#                                     'family': 'LOVES', 
#                                     'size': 30
                                },
                                textposition = 'bottom center' if team=='home' else 'top center',
                                text = (position_team.name
                                        .replace({
                                            'Cristiano Ronaldo dos Santos Aveiro': 'Cristiano Ronaldo',
                                            'Lionel Andrés Messi Cuccittini': 'Lionel Messi'
                                            })
                                        .apply(lambda x: x.split()[-1].upper())),
                                customdata = position_team.name,
                                hoverinfo = 'text',
                                xaxis = 'x2' if team == 'away' else 'x',
                                yaxis = 'y2' if team == 'away' else 'y',)

    comb_team = (pass_combinations[(pass_combinations.player_1.isin(starting[team])) &
                     (pass_combinations.player_2.isin(starting[team]))]
                 .merge(position_team[['id','name','x_pos','y_pos']], left_on='player_1', right_on='id', how='left')
                 .drop('id', 1)
                 .rename(columns={'name': 'player_1_name','x_pos': 'player_1_x_pos', 'y_pos': 'player_1_y_pos'})
                 .merge(position_team[['id','name','x_pos','y_pos']], left_on='player_2', right_on='id', how='left')
                 .rename(columns={'name': 'player_2_name','x_pos': 'player_2_x_pos', 'y_pos': 'player_2_y_pos'})
                 .drop('id', 1))

    line_team = []
    for idx, row in comb_team.iterrows():
        trace = go.Scatter(
                        x = [row['player_1_y_pos'], row['player_2_y_pos']],
                        y = [row['player_1_x_pos'], row['player_2_x_pos']],
                        mode = 'lines',
                        line = {
                                'width': 20 * row['pass_frac'],
                                'color': 'black'
                            },
                        showlegend = False,
                        opacity = row['pass_frac'] * 0.9,
                        text = 'Number of Passes: {}'.format(row['passes']),
                        hoverinfo = 'text',
                        xaxis = 'x2' if team == 'away' else 'x',
                        yaxis = 'y2' if team == 'away' else 'y',
                        )
        line_team.append(trace)
    
    return(line_team + [formation_team])

def create_passing_network_map(passing_df, location_df, starting, match_info, theme):
    """Create passing network map for both home and away teams."""
    
    passing_factor = (passing_df[passing_df.receiver_name.notnull()] 
                     .groupby(['id'], as_index=False)
                     .name.count()
                     .rename(columns={'name':'pass'})
                     .assign(pass_frac = lambda x: x['pass']/x['pass'].max()))

    positions = (location_df
                 .groupby(['id','name','team'], as_index=False)
                 .agg({
                     'x_pos': 'mean',
                     'y_pos': 'mean'})
                 .merge(passing_factor, how='left', on='id'))

    positions.loc[:, 'hover_text'] = positions.name + '<br>Passes: ' + positions['pass'].map('{:.0f}'.format)

    pass_combinations = (passing_df[passing_df.receiver_name.notnull()]
                         .assign(player_1 = lambda x: x.apply(lambda y: list({y['id'], y['receiver_id']})[0], axis=1),
                                 player_2 = lambda x: x.apply(lambda y: list({y['id'], y['receiver_id']})[1], axis=1))
                         .groupby(['player_1','player_2'], as_index=False)
                         .location.count()
                         .rename(columns = {'location':'passes'})
                         .assign(pass_frac = lambda x: x['passes']/x['passes'].max()))

    home_traces = create_map_traces('home', positions, pass_combinations, starting, match_info)
    away_traces = create_map_traces('away', positions, pass_combinations, starting, match_info)

    data = home_traces + away_traces

    full_field = create_full_field(theme)

    layout = {
        'shapes': full_field,
        'hovermode': 'closest',
        'xaxis': {'range': [-5, 85], 'visible': False, 'domain':[0, 0.5]},
        'yaxis': {'range': [-5, 125], 'visible': False},
        'xaxis2': {'range': [85, -5], 'visible': False,'domain':[0.5, 1]},
        'yaxis2': {'range': [125, -5], 'visible': False},
        'plot_bgcolor': graph_styles[theme]['bg_color'],
        'paper_bgcolor': graph_styles[theme]['bg_color'],
        'showlegend': False,
        'margin': {
            'l': 0,
            'r': 0,
            't': 40,
            'b': 0,
        },
        'annotations': [
                {
                        'x': 0.5,
                        'y': 1.08,
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                                'family': graph_styles[theme]['titlefont']['family'],
                                'size': graph_styles[theme]['titlefont']['size'],
                                'color': graph_styles[theme]['titlefont']['color'],
                        },
                        'text': 'PASSING NETWORK MAPS',
                },
        ],
    #     'legend': {
    #             'orientation': 'h',
    #             'y': 1.05, 'x': 0.5, 
    #             'xanchor': 'center',
    #             'font': {
    #                     'size': 20,
    #                 }
    #               },
#         'width': 1595,
#         'height': 1595,
        'titlefont': {
#                     'size': 20,
#                     'family': 'ObelixPro',
                    'color': graph_styles[theme]['legendfont']['color']
                    },
    #     'title': '{}'.format(events.loc[0,'team']['name'])
    }
    
    
    return({'data': data, 'layout': layout})

# Player Profile

pass_color_dic = {
    1: 'rgb(152, 252, 36)',
    2: 'rgb(207, 250, 30)',
    3: 'rgb(248, 208, 22)',
    4: 'rgb(247, 144, 17)',
    5: 'rgb(245, 88, 12)',
}

pass_description = {
    1: 'Very Short',
    2: 'Short',
    3: 'Medium',
    4: 'Long',
    5: 'Very Long',
}

angle_dic = {i: [i*22.5, i*22.5, (i*22.5) + 22.5, (i*22.5) + 22.5] for i in range(16)}

def create_player_profile(pass_angles, player_name, match_info, theme):
    """Create player profile visual."""
    

    player_passes = pass_angles[pass_angles.name.str.contains(player_name)]
    
    sector_traces = []
    for index, row in player_passes.iterrows():
        trace = go.Scatterpolar(
                                r = [0, row['count'], row['count'], 0],
                                theta = angle_dic[row['pass_sector']],
    #                             mode = 'lines',
                                fill = 'toself',
                                line = {
                                    'color': row['pass_color']
                                },
                                hoverinfo = 'text',
                                text = 'Pass length profile: {}<br>Number of passes: {}'.format(row['hover_text'], row['count']),
                                )
        sector_traces.append(trace)

    layout = go.Layout(
                      polar = {
                          'bgcolor': graph_styles[theme]['bg_color'],
                          'angularaxis': {
                              'rotation': (90 + 11.25) if player_passes.team.max() == match_info['teams']['home'] else (270 + 11.25),
                              'direction': 'clockwise',
                              'showline': False,
                              'showticklabels': False,
                              'tickvals': np.linspace(11.25, 348.75, 16) - 11.25,
                              'color': graph_styles[theme]['axis_color'],
                              'gridcolor': graph_styles[theme]['grid_color'],
                          },
                          'radialaxis': {
    #                           'range': [0, 25],
    #                           'tickvals': [0, 0.2, 0.4, 0.6, 0.8, 1],
                              'showticklabels': False,
                              'showline': True,
                              'color': graph_styles[theme]['axis_color'],
                              'gridcolor': graph_styles[theme]['grid_color'],
                          },
                          'domain':{
                              'x': [0.5, 1],
                              'y': [0, 1]
                          }
                      },
                      showlegend = False,
                      plot_bgcolor = graph_styles[theme]['bg_color'],
                      paper_bgcolor = graph_styles[theme]['bg_color'],
                      margin = {
                          'l': 0,
                          'r': 0,
                          't': 50,
                          'b': 0,
                      },
                     annotations=[
                             {
                                'text': '{}'.format(player_name),
                                'x': 0.5,
                                'y': 1.15,
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font':{
                                    'color': 'black' if theme=='light' else 'white',
                                    'size': 14,
                                }
                             },
                     ],
                     images = [{
                         'source': 'data:image/png;base64,{}'.format(get_as_base64(player_name)),
                         'layer': 'above',
                         'xref': 'paper',
                         'yref': 'paper',
                         'yanchor': 'bottom',
                         'xanchor': 'left',
                         'x': 0.05,
                         'y': 0.05,
                         'sizex': 0.4,
                         'sizey': 0.9,
                         'sizing': 'stretch'
                     }])
    
    
    return({'data': sector_traces, 'layout': layout})

# plot(create_player_profile(player_name), 'test_plot.html', auto_open=True)


# Dash app begins

what_is_xg = (
    "xG refers to Expected Goals. It is a metric which assesses every chance,"
    " essentially answering the question of whether a player should have "
    "scored from a certain opportunity. Put simply, it is a way of assigning"
    " a 'quality' value (xG) to every attempt based on what we know about it."
    " The higher the xG - with 1 being the maximum - the more likelihood of "
    "the opportunity being taken. ")

how_is_it_worked_out = (
    "Football data experts Opta have analysed over 300,000 shots to calculate"
    " the likelihood of an attempt being scored from a specific position on "
    "the pitch during a particular phase of play. The factors taken into "
    "account when assessing the quality of a chance include:")

app = dash.Dash(__name__)

app.css.append_css({"external_url": "https://codepen.io/hkhare42/pen/eQzWNy.css"})

app.layout = html.Div(id='bodydiv', children = [
                    html.Header(
                        html.Details(id='details_header', 
                            children=[
                            html.Summary('INFORMATION BAR'),

                            html.Div(id='infopanel', children = [
                                                            html.H2(id='app_title',children='FIFA WORLD CUP 2018 MATCH EXPLORER'),
                            dcc.Dropdown(id='match_dropdown', options=
                            [{'label':row['description'], 'value':row['match_id']} 
                                for idx, row in matches.sort_values('match_date').iterrows()], value=7584,
                                clearable=False),
                            html.H1(id = 'match_header'),
                                    html.P(className='paraheader', id='match_date'),
                                    html.P(className='paraheader', id='match_stadium'),
                                    html.P(className='paraheader', id='match_ref'),
                                    html.Br(),
                                    html.P(className='paraheader', children='What is XG?'),
                                    html.Br(),
                                    html.P(className='para', children=what_is_xg),
                                    html.Br(),
                                    html.P(className='paraheader', children='How is it worked out?'),
                                    html.Br(),
                                    html.P(className='para', children=how_is_it_worked_out),
                                    html.Br(),
                                    html.P(className='para', children='Distance from goal'),
                                    html.P(className='para', children='Angle of the shot'),
                                    html.P(className='para', children="Did the chance fall at the player's feet or was it a header?"),
                                    html.P(className='para', children='Was it a one on one?'),
                                    html.P(className='para', children='What was the assist like? (eg long ball, cross, through ball, pull-back)'),
                                    html.P(className='para', children='In what passage of play did it happen? (eg open play, direct free-kick, corner kick)'),
                                    html.P(className='para', children='Has the player just beaten an opponent?'),
                                    html.P(className='para', children='Is it a rebound?'),
                                    html.Br(),
                                    html.Button(id='theme_switcher'),
                                    html.Br()
                                    ])
                            ])
                                ),
                    html.Div(id='container', children=[
                                        dcc.Graph(className='graph', id='xg_plot', relayoutData={}, config={'modeBarButtons': [['zoom2d','resetViews']], 'displaylogo':False}),
                                        dcc.Graph(className='graph', id='player_profile', config={'displayModeBar': False}),
                                        dcc.Graph(className='graph', id='player_profile2', config={'displayModeBar': False}),
                                        dcc.Graph(className='graph', id='pass_map', config={'modeBarButtons': [['zoom2d','pan2d','resetViews']], 'displaylogo':False}),
                                        dcc.Graph(className='graph', id='shot_plot', config={'modeBarButtons': [['zoom2d','resetViews']], 'displaylogo':False}),
                                        dcc.Graph(className='graph', id='spider', config={'displayModeBar': False})
                                        ]),
                    html.Footer(
                            html.Details(id='details_footer', 
                            children=[
                                html.Summary('REFERENCES'),
                                html.Ul(id='ref_list', children= [
                                html.Li([
                                        'Data used for this analytical piece was made available by Statsbomb: ',
                                        html.A(href='https://statsbomb.com/data/', children='Link')
                                        ], id='referlinks'),
                                html.Li('Visuals inspired by multiple works in the community: Tegen 11, StatsBomb, Colin Trainor, Ben Mayhew.'),
                                html.Li("All analysis was carried out using Python data stack. Visualization realized with the help of Plotly's Dash framework."),
                                        ])
                                ])),
                    html.Div(id='events_div', style={'display': 'none'}),
                    html.Div(id='match_info_div', style={'display': 'none'}),
                    html.Div(id='shots_div', style={'display': 'none'}),
                    html.Div(id='passing_div', style={'display': 'none'}),
                    html.Div(id='location_div', style={'display': 'none'}),
                    html.Div(id='starting_div', style={'display': 'none'}),
                    html.Div(id='top_xg_div', style={'display': 'none'}),
                    html.Div(id='passing_angles_div', style={'display': 'none'}),
                    html.Div(id='theme_div', style={'display': 'none'})])

@app.callback(
            Output('theme_switcher', 'children'),
            [Input('theme_switcher', 'n_clicks')])
def switch_theme(n_clicks):
    if (not n_clicks) or (n_clicks%2 == 0):
        button_text = 'SWITCH TO DARK THEME'
    else:
        button_text = 'SWITCH TO LIGHT THEME'
    return button_text

@app.callback(
            Output('theme_div', 'children'),
            [Input('theme_switcher', 'n_clicks')])
def update_theme(n_clicks):
    if (not n_clicks) or (n_clicks%2 == 0):
        theme = 'light'
    else:
        theme = 'dark'
    return theme

@app.callback(
            Output('details_header', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    if theme == 'light':
        color = 'rgb(203, 203, 203)'
    else:
        color = graph_styles[theme]['bg_color']
    return {'color':color, 'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('details_footer', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    if theme == 'light':
        color = 'rgb(203, 203, 203)'
    else:
        color = graph_styles[theme]['bg_color']
    return {'color':color, 'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('app_title', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('match_header', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('infopanel', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('ref_list', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'backgroundColor':graph_styles[theme]['color']}

@app.callback(
            Output('container', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'backgroundColor':graph_styles[theme]['bg_color']}

@app.callback(
            Output('theme_switcher', 'style'),
            [Input('theme_div', 'children')])
def update_theme(theme):
    return {'color':graph_styles[theme]['bg_color'], 
            'borderColor':graph_styles[theme]['bg_color']}

@app.callback(
            Output('match_info_div', 'children'),
            [Input('match_dropdown', 'value')])
def update_match_info(match_id):
    
    match_cols = ['home','away', 'home_score','away_score',
              'match_date','display_date','match_id','referee_name',
              'stadium_name','stage','description']

    match_info = matches[matches.match_id == match_id].iloc[0][match_cols].to_dict()

    match_info['teams'] = {'home': match_info['home'], 'away': match_info['away']}
    match_info['invert_teams'] = {match_info['home']: 'home', match_info['away']: 'away'}
    
    
    return pd.Series(match_info).to_json()

@app.callback(
            Output('match_header', 'children'),
            [Input('match_info_div', 'children')])
def update_match_header(match_info):
    match_info = json.loads(match_info)
    new_header = '{} {}-{} {}'.format(match_info['home'].upper(),
                                     match_info['home_score'],
                                     match_info['away_score'],
                                     match_info['away'].upper())
    return new_header

@app.callback(
            Output('match_date', 'children'),
            [Input('match_info_div', 'children')])
def update_match_date(match_info):
    match_info = json.loads(match_info)
    return 'Date: {}'.format(match_info['display_date'])

@app.callback(
            Output('match_stadium', 'children'),
            [Input('match_info_div', 'children')])
def update_match_date(match_info):
    match_info = json.loads(match_info)
    return 'Stadium: {}'.format(match_info['stadium_name'])

@app.callback(
            Output('match_ref', 'children'),
            [Input('match_info_div', 'children')])
def update_match_date(match_info):
    match_info = json.loads(match_info)
    return 'Referee: {}'.format(match_info['referee_name'])

@app.callback(
            Output('events_div', 'children'),
            [Input('match_dropdown', 'value')])
def update_events_data(match_id):
    
    events = (pd.read_json('./data/events/{}.json'.format(match_id), encoding='utf-8')
            .query('minute < 120'))
    
    
    return events.to_json()

@app.callback(
            Output('shots_div', 'children'),
            [Input('events_div', 'children'),
             Input('match_info_div', 'children')])
def update_shots_data(events, match_info):
    
    match_info = json.loads(match_info)
    events = pd.read_json(events)
    shots = events[events.type.apply(lambda x: x['name']) == 'Shot']

    shots_df = pd.DataFrame(
        list(zip(
            shots.player.apply(lambda x: x['name']),
            shots.team.apply(lambda x: x['name']),
            shots.period,
            shots.minute,
            shots.second,
            shots.location,
            shots.shot.apply(lambda x: x['statsbomb_xg']),
            shots.shot.apply(lambda x: x['end_location']),
            shots.shot.apply(lambda x: x['outcome']['name']),
            shots.shot.apply(lambda x: x['body_part']['name']),
            shots.shot.apply(lambda x: x['technique']['name']),
        )), columns=['name','team','period','minute','seconds','location','xg',
                     'end_location','outcome','body_part','technique'])
    
    og = events[events.type.apply(lambda x: x['name']) == 'Own Goal Against']

    og_df = pd.DataFrame(
        list(zip(
            og.player.apply(lambda x: x['name']),
            og.team.apply(lambda x: list(set(match_info['teams'].values()) - {x['name']})[0]),
            og.period,
            og.minute,
            og.second,
            og.location.apply(lambda x: [120 - x[0], 80 - x[1]]),
            [0] * og.shape[0],
            [[120, 40]] * og.shape[0],
            ['Goal'] * og.shape[0],
            ['Unknown'] * og.shape[0],
            ['Unknown'] * og.shape[0],
        )), columns=['name','team','period','minute','seconds','location','xg',
                     'end_location','outcome','body_part','technique'])

    shots_df = pd.concat([shots_df, og_df], ignore_index=True, sort=False)

    shots_df.loc[:, 'dec_time'] = shots_df.minute + shots_df.seconds/60
    shots_df = shots_df.sort_values(['period','dec_time'])
    shots_df.loc[:, 'cum_xg'] = shots_df.groupby('team')['xg'].cumsum()

    shots_df.loc[:, 'hover_text'] = (shots_df.name 
                                    + ' ('
                                    + shots_df.team
                                    + ')<br>Time: '
                                    + shots_df.minute.astype(str)
                                    + ':'
                                    + shots_df.seconds.astype(str)
                                    +'<br>xG: '
                                    + shots_df.xg.map('{:.3f}'.format)
                                    + '<br>Cum. xG: '
                                    + shots_df.cum_xg.map('{:.3f}'.format)
                                    + '<br>Outcome: '
                                    + shots_df.outcome
                                    + '<br>Body Part: '
                                    + shots_df.body_part)

    shots_df.loc[:, 'shot_color'] = np.where(shots_df.outcome == 'Goal', 'black', shots_df.team.map(match_info['invert_teams']).map(team_colors))
    
    
    return shots_df.to_json()

@app.callback(
            Output('passing_div', 'children'),
            [Input('events_div', 'children')])
def update_passing_data(events):
    
    events = pd.read_json(events)
    passing = events[(events.type.apply(lambda x: x['name']) == 'Pass')]

    pass_dic = {'id': None,
               'name': None}

    passing_df = pd.DataFrame(
                    list(zip(
                        passing.player.apply(lambda x: x['name']),
                        passing.player.apply(lambda x: x['id']),
                        passing.period,
                        passing.minute,
                        passing.second,
                        passing.location,
                        passing.location.apply(lambda x: x[0]),
                        passing.location.apply(lambda x: x[1]),
                        passing.team.apply(lambda x: x['name']),
                        passing['pass'].apply(lambda x: x.get('recipient', pass_dic)['id']),
                        passing['pass'].apply(lambda x: x.get('recipient', pass_dic)['name']),
                        passing['pass'].apply(lambda x: x['height']['name']),
                        passing['pass'].apply(lambda x: x['length']),
                        passing['pass'].apply(lambda x: (x['angle'] * 180) / 3.14),
                        passing['pass'].apply(lambda x: x.get('cross', 0)),
                        passing['pass'].apply(lambda x: x.get('outcome', pass_dic)['name'])
                        )), columns=['name','id','period','minute','seconds',
                                     'location','x_pos','y_pos','team',
                                     'receiver_id','receiver_name',
                                     'height','length','angle','is_cross','outcome'])
    
    
    return passing_df.to_json()

@app.callback(
            Output('location_div', 'children'),
            [Input('events_div', 'children')])
def update_location_data(events):
    
    events = pd.read_json(events)
    mask = (~events.play_pattern.apply(lambda x: x['name'])
            .isin(['From Free Kick', 'From Corner']))

    location = events[mask & (pd.notnull(events.player)) & (pd.notnull(events.location))]

    location_df = pd.DataFrame(
                        list(zip(
                            location.player.apply(lambda x: x['name']),
                            location.player.apply(lambda x: x['id']),
                            location.period,
                            location.minute,
                            location.second,
                            location.location,
                            location.location.apply(lambda x: x[0]),
                            location.location.apply(lambda x: x[1]),
                            location.team.apply(lambda x: x['name']),
                            location.type.apply(lambda x: x['name'])
                            )), columns=['name','id','period','minute','seconds',
                                         'location','x_pos','y_pos','team','event'])
    
    
    return location_df.to_json()

@app.callback(
            Output('starting_div', 'children'),
            [Input('events_div', 'children'),
             Input('match_info_div', 'children')])
def update_starting_data(events, match_info):
    
    match_info = json.loads(match_info)
    events = pd.read_json(events)
    lineups = (events[events.type.apply(lambda x: x['name']) == 'Starting XI']
               .assign(team_type = lambda x: (x.team
                                              .apply(lambda y: y['name'])
                                              .map(match_info['invert_teams']))))

    starting = {
            'home': [player['player']['id'] for player in lineups[lineups.team_type == 'home'].tactics.iloc[0]['lineup']],
            'away': [player['player']['id'] for player in lineups[lineups.team_type == 'away'].tactics.iloc[0]['lineup']]
    }
    
    
    return json.dumps(starting)

@app.callback(
            Output('top_xg_div', 'children'),
            [Input('shots_div', 'children')])
def update_xg_data(shots_df):
    
    shots_df = pd.read_json(shots_df)

    top_xg = (shots_df
              .assign(is_goal = np.where(shots_df.outcome == 'Goal', 1, 0))
              .groupby(['name', 'team'])
              .agg({'xg': ['sum', 'count', 'max'], 'is_goal':['sum']})
              .T.reset_index(drop=True).T
              .rename(columns = {
                                  0: 'total_xg',
                                  1: 'shots',
                                  2: 'max_xg',
                                  3: 'goals'
                                })
              .reset_index()
              .sort_values('total_xg', ascending=False)
              .head(3))

    top_xg.loc[:, 'hover_text'] = (top_xg.name 
                                    + '<br>Total xG: '
                                    + top_xg.total_xg.map('{:.3f}'.format)
                                    + '<br>Shots: '
                                    + top_xg.shots.map('{:.0f}'.format)
                                    + '<br>Goals: '
                                    + top_xg.goals.map('{:.0f}'.format)
                                    + '<br>Max xG: '
                                    + top_xg.max_xg.map('{:.3f}'.format))

    
    

    return top_xg.to_json()

@app.callback(
            Output('passing_angles_div', 'children'),
            [Input('passing_div', 'children')])
def update_player_profile_data(passing_df):
    passing_df = pd.read_json(passing_df)
    pass_angles = (passing_df
                  .assign(mod_angle = np.where(passing_df.angle < 0, 360 + passing_df.angle, passing_df.angle))
                  .assign(pass_sector = lambda x: pd.cut(x.mod_angle, 
                                                        bins = np.linspace(11.25, 348.75, 16),
                                                        labels = list(range(1, 16))))
                  .assign(pass_sector = lambda x: x.pass_sector.astype('float'))
                  .fillna({'pass_sector': 0})  
                  .groupby(['name','team', 'pass_sector'])
                  .agg({'length': ['count', 'mean']})
                  .length
                  .reset_index()
                  .assign(pass_style = lambda x: pd.cut(x['mean'],
                                                       bins = [0, 10, 20, 40, 60, 130],
                                                       labels = [1, 2, 3, 4, 5]),
                          pass_color = lambda x: x['pass_style'].map(pass_color_dic),
                          hover_text = lambda x: x['pass_style'].map(pass_description)))
    return pass_angles.to_json()

@app.callback(
            Output('xg_plot', 'figure'),
            [Input('shots_div', 'children'),
             Input('events_div', 'children'),
             Input('top_xg_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_xg_plot(shots_df, events, top_xg, match_info, theme):
    
    match_info = json.loads(match_info)
    shots_df = pd.read_json(shots_df)
    events = pd.read_json(events)
    top_xg = pd.read_json(top_xg)
    
    
    return create_xg_plot(shots_df, events, top_xg, match_info, theme)

@app.callback(
            Output('pass_map', 'clickData'),
            [Input('match_dropdown', 'value')])
def update_clickdata(value):
    return None

@app.callback(
            Output('pass_map', 'hoverData'),
            [Input('match_dropdown', 'value')])
def update_hoverdata(value):
    return None

@app.callback(
            Output('xg_plot', 'relayoutData'),
            [Input('match_dropdown', 'value')])
def update_relayoutdata(value):
    return {'newmatch': ''}

@app.callback(
            Output('player_profile', 'figure'),
            [Input('passing_angles_div', 'children'),
             Input('pass_map', 'clickData'),
             Input('top_xg_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_player_profile(pass_angles, clickData, top_xg, match_info, theme):
    match_info = json.loads(match_info)
    pass_angles = pd.read_json(pass_angles)
    top_xg = pd.read_json(top_xg).sort_values('total_xg', ascending=False)
    selected_name = clickData['points'][0]['customdata'] if clickData else top_xg.name.iloc[0]
    return create_player_profile(pass_angles, selected_name, match_info, theme)

@app.callback(
            Output('player_profile2', 'figure'),
            [Input('passing_angles_div', 'children'),
             Input('pass_map', 'hoverData'),
             Input('top_xg_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_player_profile_2(pass_angles, hoverData, top_xg, match_info, theme):
    match_info = json.loads(match_info)
    pass_angles = pd.read_json(pass_angles)
    top_xg = pd.read_json(top_xg).sort_values('total_xg', ascending=False)
    selected_name = hoverData['points'][0]['customdata'] if hoverData else top_xg.name.iloc[1]
    return create_player_profile(pass_angles, selected_name, match_info, theme)

@app.callback(
            Output('pass_map', 'figure'),
            [Input('passing_div', 'children'),
             Input('location_div', 'children'),
             Input('starting_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_pass_map(passing_df, location_df, starting, match_info, theme):
    
    starting = json.loads(starting)
    match_info = json.loads(match_info)
    passing_df = pd.read_json(passing_df)
    location_df = pd.read_json(location_df)
    
    
    return create_passing_network_map(passing_df, location_df, starting, match_info, theme)

@app.callback(
            Output('shot_plot', 'figure'),
            [Input('xg_plot', 'relayoutData'),
             Input('shots_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_shot_plot(relayoutData, shots_df, match_info, theme):
    
    match_info = json.loads(match_info)
    shots_df = pd.read_json(shots_df)
    if "xaxis.range[0]" in list(relayoutData.keys()):
        new_shots_df = shots_df[(shots_df.dec_time > relayoutData['xaxis.range[0]']) 
                                & (shots_df.dec_time < relayoutData['xaxis.range[1]'])]
    else:
        new_shots_df = shots_df
    
    
    return create_shot_plot(new_shots_df, match_info, theme)

# @app.callback(
#             Output('spider', 'figure'),
#             [Input('xg_plot', 'relayoutData'),
#              Input('events_div', 'children'),
#              Input('shots_div', 'children'),
#              Input('passing_div', 'children'),
#              Input('match_info_div', 'children'),
#              Input('theme_div', 'children')])
# def update_spider(relayoutData, events, shots_df, passing_df, match_info, theme):
#     
#     match_info = json.loads(match_info)
#     events = pd.read_json(events)
#     shots_df = pd.read_json(shots_df)
#     passing_df = pd.read_json(passing_df)
#     if "xaxis.range[0]" in list(relayoutData.keys()):
#         new_shots_df = shots_df[(shots_df.dec_time > relayoutData['xaxis.range[0]']) 
#                                 & (shots_df.dec_time < relayoutData['xaxis.range[1]'])]
#         new_events = events[(events.minute >= relayoutData['xaxis.range[0]']) 
#                                 & (events.minute <= relayoutData['xaxis.range[1]'])]
#         new_passing_df = passing_df[(passing_df.minute > relayoutData['xaxis.range[0]']) 
#                                 & (passing_df.minute < relayoutData['xaxis.range[1]'])]
#     else:
#         new_shots_df = shots_df
#         new_events = events
#         new_passing_df = passing_df
#     end=time.time()
#     
#     return create_spider_chart(new_events, new_shots_df, new_passing_df, match_info, theme)

@app.callback(
            Output('spider', 'figure'),
            [Input('events_div', 'children'),
             Input('shots_div', 'children'),
             Input('passing_div', 'children'),
             Input('match_info_div', 'children'),
             Input('theme_div', 'children')])
def update_spider(events, shots_df, passing_df, match_info, theme):
    
    match_info = json.loads(match_info)
    events = pd.read_json(events)
    shots_df = pd.read_json(shots_df)
    passing_df = pd.read_json(passing_df)
    return create_spider_chart(events, shots_df, passing_df, match_info, theme)

if __name__ == '__main__':
    app.run_server(
            debug=True, 
            host='0.0.0.0'
        )