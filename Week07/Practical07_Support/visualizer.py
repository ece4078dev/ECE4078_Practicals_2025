import plotly.graph_objects as go
from spatialmath import SE3
import numpy as np
import roboticstoolbox as rp

from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from ece4078.plotly_viz import labeled_slider

class RobotPlotlyPlot():

    def __init__(self, robot, triad_length = 1.0, triad_width = 5, link_color = "#E16F6D",
                link_width = 8, joint_size = 3, shadow_color = "darkgrey",
                xlim = [-2, 2], ylim = [-2, 2], zlim = [-3, 3], ground_color = "grey",
                ground_opacity = 0.15):
        self.robot = robot
        self.triad_length = triad_length
        self.triad_width = triad_width
        self.link_color = link_color
        self.link_width = link_width
        self.joint_size = joint_size
        self.shadow_color = shadow_color
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim
        y_plane = np.linspace(*xlim, 2)
        z_plane = np.linspace(*ylim, 2)
        Y, Z = np.meshgrid(y_plane, z_plane)
        X = np.zeros_like(Y) 
        self.ground_plane = go.Surface(
            x=Y, y=Z, z=X,
            showscale=False,
            opacity=ground_opacity,
            colorscale=[[0, ground_color], [1, ground_color]],
            hoverinfo="skip",
            name="ground plane"
        )

        self.triad_x_color = "#EE9494"
        self.triad_y_color = "#93E7B0"
        self.triad_z_color = "#54AEFF"
        self.joint_axis_color = "#8FC1E2"
    
    def axes_calcs(self):
        # Joint and ee poses
        T = self.robot.fkine_all()
        Te = self.robot.fkine(self.robot.q)
        Tb = self.robot.base

        # Joint and ee position matrix
        loc = np.zeros([3, self.robot.n + 2])
        loc[:, 0] = Tb.t
        loc[:, self.robot.n + 1] = Te.t

        # Joint axes position matrix
        joints = np.zeros((3, self.robot.n))

        # Axes arrow transforms
        Tjx = SE3.Tx(self.triad_length)
        Tjy = SE3.Ty(self.triad_length)
        Tjz = SE3.Tz(self.triad_length)

        # ee axes arrows
        Tex = Te * Tjx
        Tey = Te * Tjy
        Tez = Te * Tjz

        # Joint axes arrow calcs
        for i in range(self.robot.n):
            loc[:, i + 1] = T[i].t

            if isinstance(self.robot, rp.DHRobot) \
                    or self.robot.ets[self.robot.q_idx[i]].axis == 'Rz' \
                    or self.robot.ets[self.robot.q_idx[i]].axis == 'tz':
                Tji = T[i] * Tjz

            elif self.robot.ets[self.robot.q_idx[i]].axis == 'Ry' \
                    or self.robot.ets[self.robot.q_idx[i]].axis == 'ty':
                Tji = T[i] * Tjy

            elif self.robot.ets[self.robot.q_idx[i]].axis == 'Rx' \
                    or self.robot.ets[self.robot.q_idx[i]].axis == 'tx':
                Tji = T[i] * Tjx

            joints[:, i] = Tji.t

        return loc, joints, [Tex, Tey, Tez]

    def plot_arrow(self, p0, p1, color, name):
        return go.Scatter3d(
            x=[p0[0], p1[0]], y=[p0[1], p1[1]], z=[p0[2], p1[2]],
            mode="lines",
            line=dict(width=self.triad_width, color=color),
            showlegend=False,
            name=name
        )

    def plot_link(self, loc):
        return go.Scatter3d(
            x=loc[0].tolist(), y=loc[1].tolist(), z=loc[2].tolist(),
            mode="lines+markers",
            line=dict(width=self.link_width, color=self.link_color),
            marker=dict(size=self.joint_size, color=self.link_color),
            name="links"
        )

    def plot_shadow(self, loc):
        return go.Scatter3d(
            x=loc[0].tolist(), y=loc[1].tolist(), z=np.zeros_like(loc[2]).tolist(),
            mode="lines",
            line=dict(width=self.link_width, color=self.shadow_color),
            hoverinfo="skip",
            showlegend=True,
            name="shadow"
        )

    def plot_single_frame(self):
        loc, joints, ee = self.axes_calcs()
    
        traces = [
            self.ground_plane,
            self.plot_shadow(loc),
            self.plot_link(loc)
        ]

        # Plot the axes' axis
        for j in range(self.robot.n):
            traces.append(
                self.plot_arrow(loc[:, j+1], joints[:, j], self.joint_axis_color, "joint-z")
            )

        # Plot the EE triad
        traces += [
            self.plot_arrow(loc[:, -1], ee[0].t, self.triad_x_color, "ee-x"),
            self.plot_arrow(loc[:, -1], ee[1].t, self.triad_y_color, "ee-y"),
            self.plot_arrow(loc[:, -1], ee[2].t, self.triad_z_color, "ee-z"),
        ]
        return traces

    def update_single_frame(self, theta1, theta2, theta3):
        self.robot.q = [np.deg2rad(theta1), np.deg2rad(theta2), np.deg2rad(theta3)]
        loc, joints, ee = self.axes_calcs()

        robot_dof = self.robot.n
        xs = []; ys = []; zs = []
        for j in range(robot_dof):
            xs.append([loc[:, j+1][0], joints[:, j][0]])
            ys.append([loc[:, j+1][1], joints[:, j][1]])
            zs.append([loc[:, j+1][2], joints[:, j][2]])
        EE_axes = 3
        for j in range(EE_axes):
            xs.append([loc[:, -1][0], ee[j].t[0]])
            ys.append([loc[:, -1][1], ee[j].t[1]])
            zs.append([loc[:, -1][2], ee[j].t[2]])

        
        patch = {"x": [loc[0].tolist(), loc[0].tolist()] + xs, 
                 "y": [loc[1].tolist(), loc[1].tolist()] + ys, 
                 "z": [np.zeros_like(loc[2]), loc[2]] + zs
                }
        
        EE_axes = 3
        point_limit = [4, 4] + [2]*(robot_dof + EE_axes)
        return (patch, [1, 2] + [2 + 1 + j for j in range(robot_dof + EE_axes)], 
                {"x": point_limit, "y": point_limit, "z": point_limit})

    def str_4by4(self, T, decimals = 2):
        rows = [np.round(r, decimals) for r in T]
        return "<br>".join(" ".join(f"{v:5.2f}" for v in row) for row in rows)

    def get_layout(self, width = 800, height = 600):
        return go.Layout(
                paper_bgcolor="white",
                scene=dict(
                    uirevision="robot-view",
                    bgcolor="white",
                    aspectmode="cube",
        
                    xaxis=dict(range=self.xlim, title="x",
                               showbackground=True, backgroundcolor="white",
                               showgrid=True, gridcolor="black", gridwidth=1,
                               zerolinecolor="black"),
                    yaxis=dict(range=self.ylim, title="y",
                               showbackground=True, backgroundcolor="white",
                               showgrid=True, gridcolor="black", gridwidth=1,
                               zerolinecolor="black"),
                    zaxis=dict(range=self.zlim, title="z",
                               showbackground=True, backgroundcolor="white",
                               showgrid=True, gridcolor="black", gridwidth=1,
                               zerolinecolor="black")
                ),
                width=width,
                height=height,
                showlegend=False)

    def generate_animation(self, path, max_iter = 100, play_mode = "button"):
        frames = []
        max_iter = min(max_iter, path.shape[0])
        idx = np.linspace(0, path.shape[0]-1, max_iter, dtype=int)
        path = path[idx]
        for (i, self.robot.q) in enumerate(path):
            
            annotation = dict(
                text=f"<b>End-effector Pose</b><br>{self.str_4by4(self.robot.fkine(self.robot.q).A)}",
                x = 0.02, y = 0.98, xref = "paper", yref = "paper",
                showarrow = False, align = "left",
                font = dict(family = "Courier New, monospace", size = 12)
            )
            frames.append(go.Frame(
                data=self.plot_single_frame(), 
                name = str(i),
                layout = go.Layout(annotations = [annotation])))
        slider_steps = []
        for i in range(len(frames)):
            slider_steps.append(dict(
                method="animate",
                args=[[str(i)], {
                    "frame": {"duration": 0, "redraw": True},
                    "mode": "immediate"
                }],
                label=""
            ))
        self.robot.q = path[0]

        updatemenus = []
        sliders = []
        if play_mode == "button":
            updatemenus = [dict(
                    type="buttons",
                    showactive=False,
                    y=1.05, x=0,
                    xanchor="left", yanchor="bottom",
                    buttons=[
                        dict(label="Play",
                             method="animate",
                             args=[None, dict(frame=dict(duration=50, redraw=True),
                                              transition=dict(duration=0),
                                              fromcurrent=True,
                                              mode="immediate")]),
                        dict(label="Pause",
                             method="animate",
                             args=[[None], dict(frame=dict(duration=0, redraw=False),
                                                mode="immediate")])
                    ]
                )]
        elif play_mode == "slider":
            sliders = [dict(steps=slider_steps, tickwidth=0, pad={"t": 50})]
        else:
            raise RuntimeEerror(f"Don't know what to do with play_mode: {self.play_mode}")

        base_layout = self.get_layout()
        return go.Figure(
            data=self.plot_single_frame(),
            layout=base_layout.update(
                updatemenus= updatemenus,
                sliders=sliders
            ),
            frames=frames
        )

def bot3D_viz(ctx, viz = None):
    app = ctx["app"]
    fig = go.Figure(
        data = viz.plot_single_frame(),
        layout=viz.get_layout(width = 500, height = 500))

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
                        "theta1", "θ₁ (deg)", -90, 90, 1, 0,
                        marks={-90: "-90°", 0: "0°", 90: "90°"},
                    ),
                    labeled_slider(
                        "theta2", "θ₂ (deg)", -90, 90, 1, 0,
                        marks={-90: "-90°", 0: "0°", 90: "90°"},
                    ),
                    labeled_slider(
                        "theta3", "θ₃ (deg)", -90, 90, 1, 0,
                        marks={-90: "-90°", 0: "0°", 90: "90°"},
                    )
                ],
            ),
        ],
    )

    @app.callback(
        Output("axes-graph", "extendData"),
        Output("status", "children"),
        Input("theta1", "value"),
        Input("theta2", "value"),
        Input("theta3", "value"),
        prevent_initial_call=True,
    )
    def update(theta1, theta2, theta3):
        extension = viz.update_single_frame(theta1, theta2, theta3)
        msg = f"End effector\n{np.round(viz.robot.fkine(viz.robot.q).A, 2)}"
        return extension, msg

def bot2D_viz(ctx, my_plot = None):
    loc, joints, ee = my_plot.axes_calcs()
    app = ctx["app"]
    fig = go.Figure()

    def get_arrow(p1, p2):
        return [p1[0], p2[0]], [p1[1], p2[1]]

    xx, yx = get_arrow(loc[:-1, -1], ee[0].t[:-1])
    fig.add_trace(
        go.Scatter(
            x=xx, y=yx,
            mode="lines",
            line=dict(width=my_plot.triad_width, color = my_plot.triad_x_color),
            hoverinfo="skip",
            showlegend=False,         
        )
    )

    xy, yy = get_arrow(loc[:-1, -1], ee[1].t[:-1])
    fig.add_trace(
        go.Scatter(
            x=xy, y=yy,
            mode="lines",
            line=dict(width=my_plot.triad_width, color = my_plot.triad_y_color),
            hoverinfo="skip",
            showlegend=False,         
        )
    )

    fig.add_trace(
        go.Scatter(
            x=loc[0].tolist(), y=loc[1].tolist(),
            mode="lines+markers",
            line=dict(width=my_plot.link_width, color=my_plot.link_color),
            marker=dict(size=my_plot.joint_size, color=my_plot.link_color),
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
                        "theta1", "θ₁ (deg)", -90, 90, 1, 0,
                        marks={-90: "-90°", 0: "0°", 90: "90°"},
                    ),
                    labeled_slider(
                        "theta2", "θ₂ (deg)", -90, 90, 1, 0,
                        marks={-90: "-90°", 0: "0°", 90: "90°"},
                    )
                ],
            ),
        ],
    )

    @app.callback(
        Output("axes-graph", "extendData"),
        Output("status", "children"),
        Input("theta1", "value"),
        Input("theta2", "value"),
        prevent_initial_call=True,
    )
    def update(theta1, theta2):
        my_plot.robot.q = [np.deg2rad(theta1), np.deg2rad(theta2)]
        loc, joints, ee = my_plot.axes_calcs()
        xx, yx = get_arrow(loc[:-1, -1], ee[0].t[:-1])
        xy, yy = get_arrow(loc[:-1, -1], ee[1].t[:-1])
        patch = {"x": [xx, xy, loc[0].tolist()], "y": [yx, yy, loc[1].tolist()]}
        extension = (patch, [0,1,2], {"x": [2, 2, 4], "y": [2, 2, 4]})
        # msg = f"{np.round(R, 2)}"
        msg = f"End effector\n{np.round(my_plot.robot.fkine(my_plot.robot.q).A, 2)}"
        return extension, msg