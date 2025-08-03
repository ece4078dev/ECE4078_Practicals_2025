from ece4078.plotly_viz import labeled_slider
import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objects as go
from IPython.display import IFrame
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.transforms as transforms

class bot2D():
    def __init__(self):
        # Configuration of 2D robot in world frame, x,y = coordinates in world frame, theta=orientation
        self.x = 0
        self.y = 0
        self.theta = 0
        self.states = []
        
    def reset(self):
        first_state = self.states[0]
        self.x, self.y, self.theta = first_state
        del self.states[:]
        self.states = [first_state]
        
    def get_state(self):
        """Return the current bicycle state. The state is in (x,y,theta) format"""
        return (self.x, self.y, self.theta)
    
    def set_state(self,x=0,y=0,theta=0):
        """Sets the model new state"""
        self.x = x
        self.y = y
        self.theta = theta
        self.states.append([x, y, theta])

    def get_axis(self):
        R = np.array(
            [[np.cos(self.theta), -np.sin(self.theta)], [np.sin(self.theta), np.cos(self.theta)]]
        )
        x_axis = R @ np.array([1.0, 0.0])
        y_axis = R @ np.array([0.0, 1.0])

        o_ = np.array([self.x, self.y])

        return o_ + x_axis, o_ + y_axis

def generate_initial_robot_fig(init_o, init_x, init_y, xlim = [-10, 10], ylim = [-10, 10]):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[init_o[0]], y=[init_o[1]], mode="lines", line=dict(width=2, color="blue"))
    )
    # Robot axes (trace 1 & 2)
    fig.add_trace(
        go.Scatter(x=[init_o[0], init_x[0]], y=[init_o[1], init_x[1]], mode="lines", line=dict(width=4, color="red"), showlegend=False)
    )
    fig.add_trace(
        go.Scatter(x=[init_o[0], init_y[0]], y=[init_o[1], init_y[1]], mode="lines", line=dict(width=4, color="green"), showlegend=False)
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(range=xlim, scaleanchor="y", scaleratio=1, title="x"),
        yaxis=dict(range=ylim, title="y"),
        showlegend=False,
    )

    return fig

def get_workshop_layout(fig, interval, first_label, first_max, first_step, second_label, second_max, second_step):
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100vh"},
        children=[
            dcc.Graph(id="bicycle-graph", figure=fig, style={"flex": "1 1 auto"}),
            dcc.Interval(id="timer", interval=interval, n_intervals=0, disabled=True),
            html.Div(
                style={"display": "flex", "gap": "2rem", "flexWrap": "wrap", "padding": "1rem 10"},
                children=[
                    html.Div(
                        labeled_slider("first_arg", first_label, -first_max, first_max, first_step, 0.0,
                                       marks={-first_max: f"{-first_max:.2f}", 0: 0, first_max: f"{-first_max:.2f}"}),
                        style={"flex": "1 1 50px", "minWidth": "50px"},
                    ),
                    html.Div(
                        labeled_slider("second_arg", second_label, -second_max, second_max, second_step, 0.0,
                            marks={-second_max: f"{-second_max:.2f}", 0: 0, second_max: f"{second_max:.2f}"}),
                        style={"flex": "1 1 50px", "minWidth": "50px"},
                    ),
                    html.Div(id="frame-label", style={"alignSelf": "center", "fontFamily": "monospace"}),
                    html.Button("Play/Pause", id="play-toggle-btn", n_clicks=0),
                    html.Button("Reset", id="reset-btn", n_clicks=0),
                ],
            ),
        ],
    )

def bot2D_viz(ctx, mybot, mode, interval = 50, dt = 0.05, frames_max = 300, frame_step = 1):
    if frames_max % frame_step != 0:
        raise ValueError("frames_max must be a multiple of frame_step")

    app = ctx["app"]

    init_x, init_y = mybot.get_axis()
    init_o = np.array([mybot.x, mybot.y])

    base_fig = generate_initial_robot_fig(init_o, init_x, init_y)
    if mode == "bicycle":
        app.layout = get_workshop_layout(base_fig, interval, "v (m/s)", mybot.vel_max, 0.1, "δ (rad)", mybot.delta_max, 0.1)
    elif mode == "penguinpi":
        app.layout = get_workshop_layout(base_fig, interval, "v (m/s)", mybot.max_linear_velocity, 0.1, "ω (rad/s)", mybot.max_angular_velocity, 0.1)
    else:
        raise RuntimeError(f"Don't know what to do with {mode}")
        

    @app.callback(
        Output("timer", "disabled"),
        Input("play-toggle-btn", "n_clicks"),
        State("timer", "disabled"),
        prevent_initial_call=True,
    )
    def toggle_timer(_, disabled):
        return not disabled

    @app.callback(
        Output("first_arg", "value"),
        Output("second_arg", "value"),
        Output("timer", "disabled", allow_duplicate=True),
        Output("timer",  "n_intervals"),
        Output("bicycle-graph", "figure", allow_duplicate=True),
        Output("frame-label", "children", allow_duplicate=True),
        Input("reset-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_state(_):
        mybot.reset()
        fresh_fig = ctx["app"].layout.children[0].figure
        fresh_fig.data[0].x, fresh_fig.data[0].y = [mybot.x], [mybot.y]
        fresh_fig.data[1].x, fresh_fig.data[1].y = [mybot.x, mybot.x + 1], [mybot.y, mybot.y]
        fresh_fig.data[2].x, fresh_fig.data[2].y = [mybot.x, mybot.x], [mybot.y, mybot.y + 1]
        return 0.0, 0.0, True, 0, fresh_fig, f"Frame: 0/{frames_max}"
        

    @app.callback(
        Output("bicycle-graph", "extendData"),
        Output("timer", "disabled", allow_duplicate=True),
        Input("timer", "n_intervals"),
        State("bicycle-graph", "figure"),
        State("first_arg", "value"),
        State("second_arg", "value"),
        prevent_initial_call=True,
    )
    
    def step(frame_idx, fig, v, delta):
        if (frame_idx * frame_step) >= frames_max:
            return no_update, True

        mybot.update_control(v, delta)
        x_traj = []
        y_traj = []    
        for _ in range(frame_step):
            mybot.drive(dt=dt)
            x_traj.append(mybot.x)
            y_traj.append(mybot.y)

        xaxis, yaxis = mybot.get_axis()

        patch = {
            "x": [
                x_traj,
                [mybot.x, xaxis[0]],
                [mybot.x, yaxis[0]],
            ],
            "y": [
                y_traj,
                [mybot.y, xaxis[1]],
                [mybot.y, yaxis[1]],
            ],
        }
        return (patch, [0, 1, 2], {"x": [frames_max, 2, 2], "y": [frames_max, 2, 2]}), no_update

    @app.callback(Output("frame-label", "children"), Input("timer", "n_intervals"))
    def update_label(n):
        return f"Frame: {min(n * frame_step, frames_max)}/{frames_max}"

def display_bicycle_wheels(rear_wheel, front_wheel, theta):               
    # Initialize figure
    fig = plt.figure(figsize=(5, 5))
    ax = plt.gca()
    ax.set_xlim([0,4])
    ax.set_ylim([0,4])
    ax.tick_params(axis='both', which='major', labelsize=7)
    plt.title('Overhead View')
    plt.xlabel('X (m)',weight='bold')
    plt.ylabel('Y (m)',weight='bold')

    ax.plot(0,0)
  
    rear_wheel_x = FancyArrowPatch((0,0), (0.4,0),
                                        mutation_scale=8,color='red')
    rear_wheel_y = FancyArrowPatch((0,0), (0,0.4),
                                        mutation_scale=8,color='red')

    front_wheel_x = FancyArrowPatch((0,0), (0.4,0),
                                        mutation_scale=8,color='blue') 
    front_wheel_y = FancyArrowPatch((0,0), (0,0.4),
                                        mutation_scale=8,color='blue')

    custom_lines = [Line2D([0], [0], color='red', lw=4),
                    Line2D([0], [0], color='blue', lw=4)]
    
    # Apply translation and rotation as specified by current robot state
    cos_theta, sin_theta = np.cos(theta), np.sin(theta)
    Tw_rear = np.eye(3)
    Tw_rear[0:2,2] = rear_wheel
    Tw_rear[0:2,0:2] = [[cos_theta,-sin_theta],[sin_theta,cos_theta]]
    Tw_rear_obj = transforms.Affine2D(Tw_rear)

    Tw_front = np.eye(3)
    Tw_front[0:2,2] = front_wheel
    Tw_front[0:2,0:2] = [[cos_theta,-sin_theta],[sin_theta,cos_theta]]
    Tw_front_obj = transforms.Affine2D(Tw_front)

    ax_trans = ax.transData
    
    rear_wheel_x.set_transform(Tw_rear_obj+ax_trans)
    rear_wheel_y.set_transform(rear_wheel_x.get_transform())
    ax.add_patch(rear_wheel_x)
    ax.add_patch(rear_wheel_y)

    front_wheel_x.set_transform(Tw_front_obj+ax_trans)
    front_wheel_y.set_transform(front_wheel_x.get_transform())
    ax.add_patch(front_wheel_x)
    ax.add_patch(front_wheel_y)

    ax.legend(custom_lines, ['Rear Wheel', 'Front Wheel']) 

def traj_viz(ctx, traj, pad = 1.0):
    n_frames = len(traj)

    pad = 1.0
    xlim = [traj[:, 0].min() - pad, traj[:, 0].max() + pad]
    ylim = [traj[:, 1].min() - pad, traj[:, 1].max() + pad]

    init_x, init_y, init_th = traj[0]
    init_o = np.array([init_x, init_y])
    R = np.array([[np.cos(init_th), -np.sin(init_th)], [np.sin(init_th), np.cos(init_th)]])
    x_axis = R @ np.array([1.0, 0.0])
    y_axis = R @ np.array([0.0, 1.0])

    fig = generate_initial_robot_fig(init_o, init_o + x_axis, init_o + y_axis, xlim = xlim, ylim = ylim)
    
    app = ctx["app"]

    app.layout = html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100vh"},
        children=[
            dcc.Store(id="trajectory", data=dict(x=traj[:, 0].tolist(),
                                                  y=traj[:, 1].tolist(),
                                                  theta=traj[:, 2].tolist())),
    
            dcc.Graph(id="bicycle-graph", figure=fig, style={"flex": "1 1 auto"}),
            html.Div(style={"display": "flex", "gap": "1rem", "alignItems": "center", "padding": "0 12px"}, children=[
                html.Button("Play/Pause", id="play-toggle-btn", n_clicks=0),
                html.Button("Reset", id="reset-btn", n_clicks=0),
                html.Div(
                    dcc.Slider(id="frame-slider", min=0, max=n_frames-1, step=1, value=0,
                               tooltip={"placement": "bottom", "always_visible": True}, marks = None),
                    style={"flex": "1 1 50px", "minWidth": "50px"}
                ),
                html.Div(id="frame-label", style={"fontFamily": "monospace", "minWidth": "120px"}),
            ]),
            dcc.Interval(id="timer", interval=10, n_intervals=0, disabled=True),
        ],
    )
    
    app.clientside_callback(
        """
        function(_, disabled){
            return !disabled;
        }
        """,
        Output("timer", "disabled", allow_duplicate=True),
        Input("play-toggle-btn", "n_clicks"),
        State("timer", "disabled"),
        prevent_initial_call=True,
    )
    
    app.clientside_callback(
        """
        function(tick, idx, data){
            if (tick === undefined) {
                return [dash_clientside.no_update, dash_clientside.no_update];
            }
            const maxF = data.x.length - 1;
            const next = Math.min((idx ?? -1) + 1, maxF);
            return [next, (next === maxF)]; // second output disables timer if at end
        }
        """,
        Output("frame-slider", "value", allow_duplicate=True),
        Output("timer", "disabled", allow_duplicate=True),
        Input("timer", "n_intervals"),
        State("frame-slider", "value"),
        State("trajectory", "data"),
        prevent_initial_call=True,
    )
    
    app.clientside_callback(
        """
        function(clicks, data){
            if (!clicks){
                return [dash_clientside.no_update, dash_clientside.no_update, dash_clientside.no_update];
            }
            return [0, true, `Frame: 0/${data.x.length-1}`];
        }
        """,
        Output("frame-slider", "value", allow_duplicate=True),
        Output("timer", "disabled", allow_duplicate=True),
        Output("frame-label", "children", allow_duplicate=True),
        Input("reset-btn", "n_clicks"),
        State("trajectory", "data"),
        prevent_initial_call=True,
    )
    
    app.clientside_callback(
        """
        function(idx, data, fig){
            if(idx === undefined){return dash_clientside.no_update;}
            const x = data.x, y = data.y, th = data.theta;
            const c = Math.cos(th[idx]);
            const s = Math.sin(th[idx]);
            const newFig = {...fig};
            newFig.data = [...fig.data];
            newFig.data[0] = {...fig.data[0], x: x.slice(0, idx+1), y: y.slice(0, idx+1)};
            newFig.data[1] = {...fig.data[1], x: [x[idx], x[idx]+c], y: [y[idx], y[idx]+s]};
            newFig.data[2] = {...fig.data[2], x: [x[idx], x[idx]-s], y: [y[idx], y[idx]+c]};
            return [newFig, `Frame: ${idx}/${x.length-1}`];
        }
        """,
        Output("bicycle-graph", "figure"),
        Output("frame-label", "children", allow_duplicate=True),
        Input("frame-slider", "value"),
        State("trajectory", "data"),
        State("bicycle-graph", "figure"),
        prevent_initial_call=True,
    )
