import numpy as np
import plotly.graph_objects as go

def animate_path_bug(initial_robot_pos, goal_pos, path, obstacles, robot_size, wall_thickness, goal_line = True):
    
    fig = go.Figure()

    for obs in obstacles:
        verts = obs.compute_inner_vertices(wall_thickness/2 + robot_size)
        path_str = "M " + " L ".join(f"{x},{y}" for x,y in verts) + " Z"
        fig.add_shape(
            type="path", path=path_str,
            line=dict(color="Red", width=3),
            fillcolor="rgba(255,0,0,0.3)"
        )
    #0
    fig.add_trace(go.Scatter(
        x=path[:,0], y=path[:,1],
        mode="lines", line=dict(color="blue", width=2),
        name="Planned Path"
    ))
    #1
    fig.add_trace(go.Scatter(
        x=[goal_pos[0]], y=[goal_pos[1]],
        mode="markers",
        marker=dict(size=12, color="blue"),
        name="Goal"
    ))
    #2
    fig.add_trace(go.Scatter(
        x=[initial_robot_pos[0]], y=[initial_robot_pos[1]],
        mode="markers",
        marker=dict(size=12, color="green"),
        name="Robot"
    ))

    if goal_line:
        fig.add_trace(go.Scatter(
            x=[initial_robot_pos[0], goal_pos[0]],
            y=[initial_robot_pos[1], goal_pos[1]],
            mode="lines", line=dict(color="Black", width=2, dash = "dash"),
            name="Start-Goal"
        ))

    frames = []
    for i, (x, y) in enumerate(path):
        frames.append(go.Frame(
            data=[go.Scatter(x=[x], y=[y], mode="markers", marker=dict(size=12, color="green"))],
            name=str(i),
            traces=[2]
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
        title=f"Total of steps: {len(path)}",
        sliders=[dict(steps=slider_steps, tickwidth=0)],
        width=1000, height=500,
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )

    return fig


def plot_rrt_based(rrt_based):
    path = rrt_based.planning()

    fig = go.Figure()

    # The obstacles
    for i, obs in enumerate(rrt_based.obstacle_list):
        cx, cy = obs.center
        r = obs.radius
        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=cx - r, y0=cy - r,
            x1=cx + r, y1=cy + r,
            line=dict(width=0),
            fillcolor="rgba(255,0,0,0.5)",
            name=f"obs_{i}"
        )

    # 0. Start
    fig.add_trace(go.Scatter(
        x=[rrt_based.start.x], y=[rrt_based.start.y],
        mode="markers",
        marker=dict(size=12, color="red"),
        name="start"
    ))
    
    #1. End
    fig.add_trace(go.Scatter(
        x=[rrt_based.end.x], y=[rrt_based.end.y],
        mode="markers",
        marker=dict(size=12, color="green"),
        name="end"
    ))
    return path, fig

def animate_path_rrt(rrt, path_thickness = 3):
    path, fig = plot_rrt_based(rrt)

    #2. edge and vertices
    k = 0
    for i, node in enumerate(rrt.node_list):
        if node.parent is None:
            continue
        xs = node.path_x
        ys = node.path_y
        k = k + 1
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers+lines",
            marker=dict(size=4, color="green"),
            line=dict(width=1, color="black"),
            name=f"node_{i}",
            showlegend=False
        ))

    fig = animate_path_progression(fig, path, path_thickness, k+2)
    
    return fig

def animate_path_rrtc(rrtc, path_thickness = 3):
    path, fig = plot_rrt_based(rrtc)
    k = 0
    for i, node in enumerate(rrtc.start_node_list):
        if node.parent is None:
            continue
        xs, ys = node.path_x, node.path_y
        k = k + 1
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers+lines",
            marker=dict(size=4, color="green"),
            line=dict(width=1, color="green"),
            showlegend=False
        ))
    for i, node in enumerate(rrtc.end_node_list):
        if node.parent is None:
            continue
        xs, ys = node.path_x, node.path_y
        k = k + 1
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers+lines",
            marker=dict(size=4, color="blue"),
            line=dict(width=1, color="blue"),
            showlegend=False
        ))

    fig = animate_path_progression(fig, path, path_thickness, k+2)
    
    return fig

def animate_path_prm(rmap, start, goal, path, path_thickness = 3, edge_thickness = 0.1, vertices_thickness = 2):
    fig = go.Figure()
    
    # 0. obstacle (wall)
    points = rmap.obstacles.data
    fig.add_trace(go.Scatter(
        x=rmap.obstacles.data[:, 0],
        y=rmap.obstacles.data[:, 1],
        mode='markers',
        marker=dict(size=6, color='black'),
        showlegend = False
    ))

    verts = rmap.vertices
    edges = rmap.edges
    edge_x, edge_y = [], []
    for i, nbrs in enumerate(edges):
        x0, y0 = verts[i]
        for j in nbrs:
            x1, y1 = verts[j]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

    # 1. edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=edge_thickness, color='blue'),
        name='edges',
        hoverinfo='none'
    ))

    # 2. vertices
    fig.add_trace(go.Scatter(
        x=verts[:,0], y=verts[:,1],
        mode='markers',
        marker=dict(size=vertices_thickness, color='red'),
        name='vertices'
    ))

    # 3. start
    fig.add_trace(go.Scatter(
        x=[start[0]], y=[start[1]],
        mode="markers",
        marker=dict(size=6, color="red"),
        name="start"
    ))

    # 4. goal
    fig.add_trace(go.Scatter(
        x=[goal[0]], y=[goal[1]],
        mode="markers",
        marker=dict(size=6, color="green"),
        name="goal"
    ))

    trace_index = 5 # after 4
    fig = animate_path_progression(fig, path, path_thickness, trace_index)

def animate_path_progression(fig, path, path_width, trace_index):
    if path is not None:
        solved_path = np.flipud(path)
        fig.add_trace(go.Scatter(
            x=solved_path[:, 0], y=solved_path[:, 1],
            mode="lines",
            name="solved_path",
            line=dict(width=path_width)
        ))
        
    
        frames = []
        for i in range(len(path)):
            frames.append(go.Frame(
                data=[go.Scatter(x=solved_path[:(i+1), 0], y=solved_path[:(i+1), 1], mode="lines", line=dict(width=path_width))],
                name=str(i),
                traces=[trace_index]
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
            sliders=[dict(steps=slider_steps, tickwidth=0)],
            width=600, height=600,
            xaxis=dict(constrain="domain"),  # keep square aspect
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )
    
    else:
        fig.update_layout(
            width=600, height=600,
            xaxis=dict(constrain="domain"),  # keep square aspect
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )
    
    fig.show()
