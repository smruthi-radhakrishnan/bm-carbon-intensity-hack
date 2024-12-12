import pandas as pd
import plotly.express as px
import streamlit as st
import html


# SP = Settling Period
def plot_emissions_over_time(
    output_df: pd.DataFrame,
    axis_min=None,
    axis_max=None,
    title="Baseline CO₂ emissions over time (tonnes)",
    y_label="CO₂ (tonnes)",
    x_label="Settlement period start time (GMT)",
    line_colour="#B53737",
):
    emissions_per_sp = output_df.groupby("start_time_gmt", as_index=False)[
        "carbon_emissions_tonnes"
    ].sum()
    fig = px.line(emissions_per_sp, x="start_time_gmt", y="carbon_emissions_tonnes")
    fig.update_layout(title=title)
    fig.update_xaxes(title=x_label)
    fig.update_yaxes(title=y_label)
    if axis_max:
        fig.update_yaxes(range=(axis_min, axis_max))
    fig.update_traces(line=dict(color=line_colour), mode="lines")
    return fig


def plot_cost_over_time(
    output_df: pd.DataFrame,
    axis_min=None,
    axis_max=None,
    title="Baseline cost over time (£)",
    y_label="Cost (£)",
    x_label="Settlement period start time (GMT)",
    line_colour="#324AB2",
):
    cost_per_sp = output_df.groupby("start_time_gmt", as_index=False)[
        "total_cost_pounds"
    ].sum()
    fig = px.line(cost_per_sp, x="start_time_gmt", y="total_cost_pounds")
    fig.update_layout(title=title)
    fig.update_xaxes(title=x_label)
    fig.update_yaxes(title=y_label)
    if axis_max:
        fig.update_yaxes(range=(axis_min, axis_max))
    fig.update_traces(line=dict(color=line_colour), mode="lines")

    return fig


def summary_table(original_df=None, adjusted_df=None):

    original_cost = (
        str((original_df["total_cost_pounds"].sum() / 1000000).round(1)) + "M"
    )
    adjusted_cost = (
        str((adjusted_df["total_cost_pounds"].sum().round(1) / 1000000).round(1)) + "M"
    )

    cost_diff = (
        str(
            (
                (
                    adjusted_df["total_cost_pounds"].sum()
                    - original_df["total_cost_pounds"].sum()
                ).round(2)
                / 1000000
            ).round(1)
        )
        + "M"
    )

    original_carbon = original_df["carbon_emissions_tonnes"].sum()
    adjusted_carbon = adjusted_df["carbon_emissions_tonnes"].sum()

    data = {
        "Type": ["Cost (£)", "CO₂ (tonnes)"],
        "Baseline": [original_cost, original_carbon],
        "Emissions-adjusted": [adjusted_cost, adjusted_carbon],
        "Abs diff": [cost_diff, original_carbon - adjusted_carbon],
    }

    carbon_cost = (
        adjusted_df["total_cost_pounds"].sum() - original_df["total_cost_pounds"].sum()
    ) / (original_carbon - adjusted_carbon)

    return [data, carbon_cost]