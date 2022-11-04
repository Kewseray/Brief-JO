from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import copy

import pandas as pd
import numpy as np

df = pd.read_csv('pays_results.csv')

app = Dash(__name__)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h")
)

app.layout = html.Div([
    html.H1(children='Dashboard des JO'),

    html.Div(children='''
        Dashboard pour le brief Dessine moi les JO.
    '''),

    html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filtrer les résultats par date:",
                            className="control_label",
                        ),
                            dcc.RangeSlider(
                            min=df['date'].min(),
                            max=df['date'].max(),
                            value=[df['date'].min(), df['date'].max()],
                            marks={str(year): str(year) for year in np.arange(1896, 2024, 16)},
                            id='year-slider'
                        ),
                        html.P("Sexe à afficher :", className="control_label"),
                        dcc.RadioItems(
                            id="data_selector",
                            options=[
                                {"label": "Total ", "value": "All"},
                                {"label": "Homme ", "value": "Man"},
                                {"label": "Femme ", "value": "Woman"},
                            ],
                            value="All",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="pays_menu",
                            options=["Greece","Australia","Russia"],
                            multi=True,
                            value=list(["Greece","Australia","Russia"]),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="medal_text"), html.P("Nombre de médailles")],
                                    id="medals",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [dcc.Graph(id="individual_graph")],
                                    className="pretty_container five columns",
                                ),
                                html.Div(
                                    [dcc.Graph(id="athlete_graph")],
                                    className="pretty_container four columns",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="graph-with-slider")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

    #dcc.Graph(id='graph-with-slider'),
])


# Helper functions
def filter_dataframe(df, pays, sexe, year_slider):
    if sexe == "All":
        dff = df[
            df["country_name"].isin(pays)
        ]

    else:
        dff = df[
            df["country_name"].isin(pays)
            & df["sexe"].isin([sexe])
        ]
    return dff


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'),
    Input('pays_menu', 'value'),
    Input('data_selector', 'value'))
def update_figure(selected_year, pays, sexe):
    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, pays, sexe, selected_year)

    medal_count = dff.groupby(by="date").count().medal_type
    athlete_count = dff.groupby(by="date").count().athlete_url

    colors = []
    colors2 = []
    for i in medal_count.index:
        if i >= int(selected_year[0]) and i <= int(selected_year[1]):
            colors.append("rgb(123, 199, 255)")
            colors2.append("rgb(199, 255, 123)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")
            colors2.append("rgba(199, 255, 123, 0.2)")

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=medal_count.index,
            y=medal_count.values,
            name="Medals",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=medal_count.index,
            y=medal_count.values,
            name="Medals",
            marker=dict(color=colors),
        ),
        dict(
            type="scatter",
            mode="markers",
            x=athlete_count.index,
            y=athlete_count.values,
            name="Athletes",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=athlete_count.index,
            y=athlete_count.values,
            name="Athletes",
            marker=dict(color=colors2),
        ),
    ]

    layout_count["title"] = "Nombre d'athlètes et de médailles"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = True
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)

    return figure



# Selectors -> medal text
@app.callback(
    Output("medal_text", "children"),
    Input("year-slider", "value"),
    Input('pays_menu', 'value'),
    Input('data_selector', 'value')
)
def update_medal_text(year_slider, pays, sexe):

    dff = filter_dataframe(df, pays, sexe, year_slider)

    dff_final = dff.groupby(by="date").count().medal_type
    return dff_final.loc[year_slider[0]:year_slider[1]+4].sum()


# Selectors -> 10 bests figure
@app.callback(
    Output("individual_graph", "figure"),
    Input("year-slider", "value"),
    Input('pays_menu', 'value'),
    Input('data_selector', 'value')
)
def update_10_bests(year_slider, pays, sexe):

    dff = filter_dataframe(df, pays, sexe, year_slider)

    dff_final = dff.groupby(by="athlete_url").count().sort_values(by="medal_type", ascending=False)[:10]
    names = []
    for row in dff_final.iterrows():
        names.append(row[0].split("/")[-1].split("-")[-1])

    fig = px.bar(dff_final, x=np.array(names), y="medal_type")

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)