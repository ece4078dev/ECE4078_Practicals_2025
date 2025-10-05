import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from scipy.stats import norm


def SLAM_plotting(ctx, callback_fn, init_belief):
    
    app = ctx["app"]

    belief_position = init_belief

    def make_fig(old_dist, new_dist):

        x_old, y_old = old_dist.plotlists(0, 500)
        x_new, y_new = new_dist.plotlists(0, 500)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_old, y=y_old, mode="lines", name="Current probability",
            line=dict(shape="hv", color="blue")
        ))
        fig.add_trace(go.Scatter(
            x=x_new, y=y_new, mode="lines",
            name="Uncertainty after 5 steps",
            line=dict(shape="hv", color="green")
        ))
        fig.update_layout(
            margin=dict(t=20),
            height=500,
            width=1000,
            xaxis_title="Robot's position along the 1D line",
            yaxis_title="Probability of robot being at position x",
            legend_title=None,
            yaxis=dict(range=[0, 1.1])
        )
        return fig

    app.layout = html.Div([
        html.Div([
            html.Button("Move 5 steps", id="btn-move", n_clicks=0),
            html.Button("Reset", id="btn-reset", n_clicks=0)]),
        dcc.Graph(id="belief-graph",
                  figure=make_fig(belief_position, belief_position)),
    ])

    @app.callback(
        Output("belief-graph", "figure"),
        Input("btn-move", "n_clicks"),
        Input("btn-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_belief(n_move, n_reset):
        nonlocal belief_position

        triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        action = "reset" if triggered == "btn-reset" else "move"
        if action == "reset":
            old_belief = init_belief
        else:
            old_belief = belief_position
        belief_position = callback_fn(action, belief_position)
        return make_fig(old_belief, belief_position)


def KF_plotting(ctx, step_fn, x, mu_k, sigma_k, true_state, sigma_R):

    app = ctx["app"]

    def make_fig(y_pred, y_mes, y_est, x_true):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y_pred, mode="lines",
                                 line=dict(shape="hv", color="green"),
                                 name="Model Uncertainty", legendgroup = "pred"))
        fig.add_trace(go.Scatter(x=x, y=y_mes, mode="lines",
                                 line=dict(shape="hv", color="red"),
                                 name="Measurement Uncertainty", legendgroup = "mes"))
        fig.add_trace(go.Scatter(x=x, y=y_est, mode="lines",
                                 line=dict(shape="hv", color="orange"),
                                 name="KF Uncertainty", legendgroup = "est"))
        fig.add_trace(go.Scatter(x=[x_true], y=[0], mode="markers",
                                 marker=dict(color="blue", size=10),
                                 name="True Position", legendgroup = "true"))
        fig.update_layout(
            margin=dict(t=20), height=500,
            xaxis_title="Robot position along the 1D line",
            yaxis_title="Probability of robot position",
            legend_title=None,
            yaxis=dict(range=[-0.1, 1.1])
        )
        return fig

    store_init = dict(k=0, mu=mu_k, sigma=sigma_k)
    app.layout = html.Div([
        html.Div([
            html.Button("Next step", id="btn-next", n_clicks=0,
                        style={"marginRight": "1rem",
                               "background": "#28a745", "color": "white",
                               "border": "none", "padding": "0.5rem 1rem",
                               "borderRadius": "6px"}),
        ], style={"marginBottom": "1rem"}),

        dcc.Graph(id="kf-graph",
                  figure=make_fig(
                      norm.pdf(x, loc=mu_k, scale=sigma_k),
                      norm.pdf(x, loc=true_state[0], scale=sigma_R),
                      norm.pdf(x, loc=mu_k, scale=sigma_k),
                      true_state[0])),
        dcc.Store(id="kf-store", data=store_init),
    ])

    @app.callback(
        Output("kf-graph", "figure"),
        Output("kf-store", "data"),
        Input("btn-next", "n_clicks"),
        State("kf-graph", "figure"),   # ← current figure
        State("kf-store", "data"),
        prevent_initial_call=True,
    )
    def _step(_, fig_json, data):
        k, mu_k, sigma_k = data["k"], data["mu"], data["sigma"]
        if k >= len(true_state) - 1:
            return dash.no_update, data
    
        mu_next, sigma_next, y_pred, y_mes, y_est = step_fn(k, mu_k, sigma_k)
    
        new_traces = [
            dict(x=x, y=y_pred,  mode="lines",
                 line=dict(shape="hv", color="green"),
                 name="Model Uncertainty", showlegend=False, legendgroup = "pred"),
            dict(x=x, y=y_mes,   mode="lines",
                 line=dict(shape="hv", color="red"),
                 name="Measurement Uncertainty", showlegend=False, legendgroup = "mes"),
            dict(x=x, y=y_est,   mode="lines",
                 line=dict(shape="hv", color="orange"),
                 name="KF Uncertainty", showlegend=False, legendgroup = "est"),
            dict(x=[true_state[k + 1]], y=[0], mode="markers",
                 marker=dict(color="blue", size=10),
                 name="True Position", showlegend=False, legendgroup = "true"),
        ]
    
        fig_json["data"].extend(new_traces)
        new_store = dict(k=k + 1, mu=float(mu_next), sigma=float(sigma_next))
        return fig_json, new_store