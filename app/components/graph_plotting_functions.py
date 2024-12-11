import pandas as pd
import plotly.express as px


# SP = Settling Period
def plot_emissions_over_time(output_df: pd.DataFrame):
    emissions_per_sp = output_df.groupby("start_time_gmt", as_index=False)[
        "carbon_emissions_tonnes"
    ].sum()
    fig = px.line(emissions_per_sp, x="start_time_gmt", y="carbon_emissions_tonnes")
    fig.update_layout(title="Emissions over time, tonnes")
    return fig


def plot_cost_over_time(output_df: pd.DataFrame):
    cost_per_sp = output_df.groupby("start_time_gmt", as_index=False)[
        "total_cost_pounds"
    ].sum()
    fig = px.line(cost_per_sp, x="start_time_gmt", y="total_cost_pounds")
    fig.update_layout(title="Cost over time, £")
    fig.update_traces(line=dict(color="#FF0000"), mode="lines")

    return fig
