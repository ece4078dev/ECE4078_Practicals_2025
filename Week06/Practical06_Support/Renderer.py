from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

def render_plotly(x_state,
                     first_value, first_name, first_title,
                     second_value, second_name, second_title,
                     sim_time, goal_x, robot_axis_len = 2, is_1D = False,
                     height = 600, width = 1500):
    if is_1D:
        if len(x_state.shape) > 1:
            raise RuntimeError(f"x state is not 1D vector but specified is_1D")
        x_state = np.hstack([x_state.reshape(-1, 1), np.zeros((x_state.shape[0], 2))])
    else:
        if x_state.shape[1] != 3:
            raise RuntimeError(f"Only know how to handle (N, 3) got *(N, {x_state.shape[2]})")
    if len(goal_x) == 2:
        goal_x = np.append(goal_x, 0)
    
    N = x_state.shape[0]

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"rowspan": 2}, {"type": "scatter"}],
               [None,           {"type": "scatter"}]],
        column_widths=[0.55, 0.45],
        row_heights=[0.6, 0.4],
        subplot_titles=("Overhead view", first_title, second_title)
    )
    # 0. path
    fig.add_trace(go.Scatter(
        x=[x_state[0, 0]], y=[x_state[0, 1]],
        mode="lines",
        marker=dict(size=10, color="blue"),
        line=dict(width=2, color="blue"),
        name="robot path"),
        row=1, col=1)
    
    # 1. first value
    fig.add_trace(go.Scatter(
        x=[sim_time[0]], y=[first_value[0]],
        mode="lines",
        line=dict(width=2, color="green")),
        row=1, col=2)
    # 2. second_value
    fig.add_trace(go.Scatter(
        x=[sim_time[0]], y=[second_value[0]],
        mode="lines",
        line=dict(width=2, color="firebrick")),
        row=2, col=2)
    # 3. goal_x
    fig.add_trace(go.Scatter(
        x=[goal_x[0], goal_x[0] + robot_axis_len],
        y=[goal_x[1], goal_x[1]],
        mode="lines",
        line=dict(width=4, color="rgba(255, 0, 0, 0.3)"),
        showlegend=False),
        row=1, col=1)
    # 4. goal_y
    fig.add_trace(go.Scatter(
        x=[goal_x[0], goal_x[0]],
        y=[goal_x[1], goal_x[1] + robot_axis_len],
        mode="lines",
        line=dict(width=4, color="rgba(0, 255, 0, 0.3)"),
        showlegend=False),
        row=1, col=1)
    # 5. current_x
    fig.add_trace(go.Scatter(
        x=[x_state[0, 0], x_state[0, 0] + robot_axis_len * np.cos(x_state[0, 2])],
        y=[x_state[0, 1], x_state[0, 1] + robot_axis_len * np.sin(x_state[0, 2])],
        mode="lines",
        line=dict(width=4, color="red"),
        showlegend=False),
        row=1, col=1)
    # 6. current_y
    fig.add_trace(go.Scatter(
        x=[x_state[0, 0], x_state[0, 0] - robot_axis_len * np.sin(x_state[0, 2])],
        y=[x_state[0, 1], x_state[0, 1] + robot_axis_len * np.cos(x_state[0, 2])],
        mode="lines",
        line=dict(width=4, color="green"),
        showlegend=False),
        row=1, col=1)


    # # ---------- animation frames ----------
    frames = []
    for k in range(N):
        c = np.cos(x_state[k, 2])
        s = np.sin(x_state[k, 2])
        frames.append(go.Frame(
            name=str(k),
            data=[
                go.Scatter(x=x_state[:k + 1, 0], y=x_state[:k + 1, 1]),
                go.Scatter(x=sim_time[:k + 1], y=first_value[:k + 1]),
                go.Scatter(x=sim_time[:k + 1], y=second_value[:k + 1]),
                go.Scatter(x=[x_state[k, 0], x_state[k, 0] + robot_axis_len * c],
                           y=[x_state[k, 1], x_state[k, 1] + robot_axis_len * s]),
                go.Scatter(x=[x_state[k, 0], x_state[k, 0] - robot_axis_len * s],
                           y=[x_state[k, 1], x_state[k, 1] + robot_axis_len * c])
            ],
            traces = [0,1,2,5,6]
        ))

    fig.frames = frames

    slider_steps = []
    for i in range(len(frames)):
        slider_steps.append(dict(
            method="animate",
            args=[[str(i)], {
                "frame": {"duration": 0, "redraw": False},
                "mode": "immediate"
            }],
            label=""
        ))
        
    fig.update_layout(
        sliders=[dict(steps=slider_steps, tickwidth=0, pad={"t": 50})],
        width=600, height=600,
        xaxis=dict(constrain="domain"),  # keep square aspect
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )

    fig.update_xaxes(title_text="<b>X (m)</b>",
                     range=[x_state[:, 0].min() - 2 * robot_axis_len, x_state[:, 0].max() + 2 * robot_axis_len],
                     row=1, col=1)
    fig.update_yaxes(title_text="<b>Y (m)</b>", visible=True, row=1, col=1, scaleanchor="x", scaleratio = 1,
                    range=[x_state[:, 1].min() - 2 * robot_axis_len, x_state[:, 1].max() + 2 * robot_axis_len])

    fig.update_xaxes(title_text="Time", row=1, col=2, range= [0, sim_time[-1]])
    fig.update_xaxes(title_text="Time", row=2, col=2, range= [0, sim_time[-1]])
    fig.update_yaxes(title_text=first_name, row=1, col=2, range = [np.min(first_value), np.max(first_value)])
    fig.update_yaxes(title_text=second_name, row=2, col=2, range = [np.min(second_value), np.max(second_value)])

    fig.update_layout(
        height=height, width=width,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.show()
