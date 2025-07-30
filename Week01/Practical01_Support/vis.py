import os
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from IPython.display import HTML
import numpy as np

class InteractiveApp:

    def __init__(self, host="0.0.0.0", port=8080, display_host="127.0.0.1"):
        self.host, self.port = host, port
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div()
        self._demo_builders = {}
        self._current_demo = None
        self._server_thread = None
        self.register_demo("NotebookChecker",  NotebookChecker)

        if "DEEPNOTE_PROJECT_ID" in os.environ:
            deepnote_id = os.environ["DEEPNOTE_PROJECT_ID"]
            self.url = f"https://{deepnote_id}.deepnoteproject.com"
            self.is_deepnote = True
        else:
            self.url = f"http://{display_host}:{self.port}"
            self.is_deepnote = False


    def register_demo(self, name: str, builder):
        self._demo_builders[name] = builder

    def use_demo(self, name: str, *args, **kwargs):
        if name not in self._demo_builders:
            raise KeyError(f"No demo named '{name}' registered")
        if self._current_demo is not None:
            self.app._callback_list = []
        builder = self._demo_builders[name]
        builder({"app": self.app}, *args, **kwargs)
        self._current_demo = name

    def run(self):
        self.app.run(jupyter_mode="external", host=self.host, port=self.port, debug=False, use_reloader=False)

    def embed(self, height=500):
        if self.is_deepnote:
            height = "100%"
        else:
            height = f"{height}px"
        return HTML(
            f'<iframe src="{self.url}" '
            f'style="width:100%; height:{height}; border:none;"></iframe>'
        )


def NotebookChecker(ctx, compute_fn = None):

    app = ctx["app"]
    x = np.linspace(0, 2 * np.pi, 400)

    # Initial figure (ω = 1)
    base_fig = go.Figure(go.Scatter(x=x, y=np.sin(x), mode="lines"))
    base_fig.update_layout(
        margin=dict(t=20),
        xaxis_title="x",
        yaxis_title="sin(x)",
        height=500,
    )

    app.layout = html.Div([
        dcc.Slider(
            id="freq",
            min=1, max=10, step=1, value=1,
            marks={i: str(i) for i in range(1, 11)},
        ),
        dcc.Graph(id="sine-graph", figure=base_fig),
    ])

    @app.callback(
        Output("sine-graph", "figure"),
        Input("freq", "value"),
        prevent_initial_call=True,
    )
    
    def update(freq):
        if freq == 10:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=20),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(
                    text="Isaac Asimov",
                    x=0.5, y=0.5, xref="paper", yref="paper",
                    showarrow=False, font=dict(size=28)
                )],
                height=500,
            )
            return fig

        y = np.sin(freq * x)
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines"))
        fig.update_layout(
            margin=dict(t=20),
            xaxis_title="x",
            yaxis_title=f"sin({freq}x)",
            height=500,
        )
        return fig

def get_tf_point(tf):
    o = tf @ np.array([[0, 0, 0, 1]]).T
    x = tf @ np.array([[1, 0, 0, 1]]).T
    y = tf @ np.array([[0, 1, 0, 1]]).T
    z = tf @ np.array([[0, 0, 1, 1]]).T

    return o[:3, 0], x[:3, 0], y[:3, 0], z[:3, 0]

def labeled_slider(id, label, min, max, step, value, marks):
    return html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0px'},
        children=[
            html.Label(label, style={'width': '12%', 'marginRight': '5%'}),
            html.Div(
                dcc.Slider(
                    id=id,
                    min=min,
                    max=max,
                    step=step,
                    value=value,
                    marks=marks,
                    updatemode="drag",
                    tooltip={"placement": "bottom"},
                ),
                style={'flex': '1'}
            )
        ]
    )

def rotate2D_viz(ctx, compute_fn=None):
    app = ctx["app"]
    
    colors = ["red", "green"]
    fig = go.Figure()

    for (x, y), col in zip([(1, 0), (0, 1)], colors):
        fig.add_trace(
            go.Scatter(
                x=[0, x], y=[0, y],
                mode="lines+markers",
                marker=dict(size=6, color=col),
                line=dict(width=5, color=col),
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[0, 1, 0, 0],
            y=[0, 0, 0, 1],
            mode="lines",
            line=dict(width=1, dash="dash", color="black"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=20),
        height=500,
        xaxis=dict(title = 'x', range=[-1.5, 1.5], scaleanchor="y", scaleratio=1, zeroline=False),
        yaxis=dict(title = 'y', range=[-1.5, 1.5], zeroline=False),
    )

    app.layout = html.Div(
        style={"display": "flex", "width": "100%", "height": "80vh"},
        children=[
            html.Div(
                style={"flex": "1 0 60%", "display": "flex", "flexDirection": "column"},
                children=[
                    dcc.Graph(id="axes-graph", figure=fig, style={"flex": "1 1 auto"}),
                    html.Div(id="status", style={"textAlign": "center",
                                                 "padding": "6px 0",
                                                 "fontFamily": "monospace",
                                                 "whiteSpace": "pre"}),
                ],
            ),
            html.Div(
                style={"flex": "0 0 40%",
                       "display": "flex",
                       "flexDirection": "column",
                       "justifyContent": "space-evenly",
                       "padding": "0 1rem"},
                children=[
                    labeled_slider(
                        "theta", "theta", -180, 180, 3, 0,
                        marks={-180: "-180°", 0: "0°", 180: "180°"},
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("axes-graph", "extendData"),
        Output("status", "children"),
        Input("theta", "value"),
        prevent_initial_call=True,
    )
    def update(theta):
        R = compute_fn(theta)
        o = np.array([0.0, 0.0])
        x_ = R @ np.array([1.0, 0.0])
        y_ = R @ np.array([0.0, 1.0])

        patch = {
            "x": [[o[0], x_[0]], [o[0], y_[0]]],
            "y": [[o[1], x_[1]], [o[1], y_[1]]],
        }
        extension = (patch, [0, 1], 2)
        msg = f"{np.round(R, 2)}"
        return extension, msg

def rotate3D_viz(ctx, compute_fn = None):
    app = ctx["app"]

    colors = ["red", "green", "blue"]
    fig = go.Figure()
    for p, axis_colour in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], colors):
        fig.add_trace(
            go.Scatter3d(
                x=[0, p[0]],
                y=[0, p[1]],
                z=[0, p[2]],
                mode="lines+markers",
                marker=dict(size=4, color=axis_colour),
                line=dict(width=5, color=axis_colour),
                showlegend=False
            )
        )

    fig.add_trace(
        go.Scatter3d(
        x=[0,1,0,0,0,0], y=[0,0,0,1,0,0], z=[0,0,0,0,0,1],
        marker=dict(opacity=0.1, size=0.0001),
        line=dict(width=10, color='black',dash='dash'),
        name="origin"
        )
    )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=20),
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5], zeroline=False),
            yaxis=dict(range=[-1.5, 1.5], zeroline=False),
            zaxis=dict(range=[-1.5, 1.5], zeroline=False),
            aspectmode="cube",
        ),
        height=500
    )
        

    app.layout = html.Div(
        style={"display": "flex", "width": "100%", "height": "80vh"},
        children=[
            html.Div(
                style={"flex": "1 0 60%",
                       "display": "flex",
                       "flexDirection": "column"},
                children=[
                    dcc.Graph(
                        id="axes-graph",
                        figure=fig,
                        style={"flex": "1 1 auto"}
                    ),

                    html.Div(
                        id="status",
                        style={"textAlign": "center",
                               "padding": "6px 0",
                               "fontFamily": "monospace",
                               "whiteSpace": "pre"}
                    ),
                ],
            ),

            html.Div(
                style={
                    "flex": "0 0 40%",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "space-evenly",
                    "padding": "0 1rem",
                },
                children=[
                    html.Div(
                        style={'marginBottom': '16px'},
                        children=[
                            html.Label("Transform:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                            dcc.RadioItems(
                                id='mode-btn',
                                options=[
                                    {'label': 'x-z-y', 'value': 'x-z-y'},
                                    {'label': 'z-x-y', 'value': 'z-x-y'},
                                    {'label': 'y-z-x', 'value': 'y-z-x'},
                                ],
                                value='x-z-y',
                                labelStyle={'display': 'inline-block', 'marginRight': '8px'},
                                inputStyle={"marginRight": "4px"}
                            ),
                        ]
                    ),
                    labeled_slider(
                        'rx', 'theta_x', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
                    labeled_slider(
                        'ry', 'theta_y', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
                    labeled_slider(
                        'rz', 'theta_z', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("axes-graph", "extendData"),
        Output("status", "children"),
        Input("rx", "value"), Input("ry", "value"), Input("rz", "value"),
        Input("mode-btn", "value"),
        prevent_initial_call=True,
    )
    def update(rx, ry, rz, mode):
        rot = compute_fn(mode, rx, ry, rz)
        tf = np.identity(4)
        tf[:3, :3] = rot
        o_, x_, y_, z_ = get_tf_point(tf)
        patch = {"x": [[o_[0], x_[0]], [o_[0], y_[0]], [o_[0], z_[0]]], 
                 "y": [[o_[1], x_[1]], [o_[1], y_[1]], [o_[1], z_[1]]], 
                 "z": [[o_[2], x_[2]], [o_[2], y_[2]], [o_[2], z_[2]]]}
        extension = (patch, [0,1,2], 2)
        msg = (
            f"{np.round(tf,2)[:3, :3]}"
        )
        return extension, msg

def transform3D_viz(ctx, compute_fn = None):
    app = ctx["app"]

    colors = ["red", "green", "blue"]
    fig = go.Figure()
    for p, axis_colour in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], colors):
        fig.add_trace(
            go.Scatter3d(
                x=[0, p[0]],
                y=[0, p[1]],
                z=[0, p[2]],
                mode="lines+markers",
                marker=dict(size=4, color=axis_colour),
                line=dict(width=5, color=axis_colour),
                showlegend=False
            )
        )

    fig.add_trace(
        go.Scatter3d(
        x=[0,1,0,0,0,0], y=[0,0,0,1,0,0], z=[0,0,0,0,0,1],
        marker=dict(opacity=0.1, size=0.0001),
        line=dict(width=10, color='black',dash='dash'),
        name="origin"
        )
    )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=20),
        scene=dict(
            xaxis=dict(range=[-2.5, 2.5], zeroline=False),
            yaxis=dict(range=[-2.5, 2.5], zeroline=False),
            zaxis=dict(range=[-2.5, 2.5], zeroline=False),
            aspectmode="cube",
        ),
        height=500
    )
        

    app.layout = html.Div(
        style={"display": "flex", "width": "100%", "height": "80vh"},
        children=[
            html.Div(
                style={"flex": "1 0 60%",
                       "display": "flex",
                       "flexDirection": "column"},
                children=[
                    dcc.Graph(
                        id="axes-graph",
                        figure=fig,
                        style={"flex": "1 1 auto"}
                    ),

                    html.Div(
                        id="status",
                        style={"textAlign": "center",
                               "padding": "6px 0",
                               "fontFamily": "monospace",
                               "whiteSpace": "pre"}
                    ),
                ],
            ),

            html.Div(
                style={
                    "flex": "0 0 40%",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "space-evenly",
                    "padding": "0 1rem",
                },
                children=[
                    html.Div(
                        style={'marginBottom': '16px'},
                        children=[
                            html.Label("Transform:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                            dcc.RadioItems(
                                id='mode-btn',
                                options=[
                                    {'label': 'X transform', 'value': 'x'},
                                    {'label': 'Y transform', 'value': 'y'},
                                    {'label': 'Z transform', 'value': 'z'},
                                ],
                                value='x',
                                labelStyle={'display': 'inline-block', 'marginRight': '8px'},
                                inputStyle={"marginRight": "4px"}
                            ),
                        ]
                    ),
                    labeled_slider(
                        'rx', 'theta_x', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
                    labeled_slider(
                        'ry', 'theta_y', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
                    labeled_slider(
                        'rz', 'theta_z', -180, 180, 5, 0,
                        marks={-180: '-180°', 0: '0°', 180: '180°'}
                    ),
    
                    labeled_slider(
                        'tx', 'd_x', -2, 2, 0.1, 0,
                        marks={-2: '-2', 0: '0', 2: '2'}
                    ),
                    labeled_slider(
                        'ty', 'd_y', -2, 2, 0.1, 0,
                        marks={-2: '-2', 0: '0', 2: '2'}
                    ),
                    labeled_slider(
                        'tz', 'd_z', -2, 2, 0.1, 0,
                        marks={-2: '-2', 0: '0', 2: '2'}
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("axes-graph", "extendData"),
        Output("status", "children"),
        Input("rx", "value"), Input("ry", "value"), Input("rz", "value"),
        Input("tx", "value"), Input("ty", "value"), Input("tz", "value"),
        Input("mode-btn", "value"),
        prevent_initial_call=True,
    )
    def update(rx, ry, rz, tx, ty, tz, mode):
        tf = compute_fn(mode, rx, tx, ry, ty, rz, tz)
        o_, x_, y_, z_ = get_tf_point(tf)
        patch = {"x": [[o_[0], x_[0]], [o_[0], y_[0]], [o_[0], z_[0]]], 
                 "y": [[o_[1], x_[1]], [o_[1], y_[1]], [o_[1], z_[1]]], 
                 "z": [[o_[2], x_[2]], [o_[2], y_[2]], [o_[2], z_[2]]]}
        extension = (patch, [0,1,2], 2)
        msg = (
            f"{np.round(tf,2)}"
        )
        return extension, msg