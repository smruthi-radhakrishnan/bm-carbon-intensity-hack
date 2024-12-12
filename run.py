import streamlit as st
import pandas as pd
from app.components.graph_plotting_functions import (
    plot_emissions_over_time,
    plot_cost_over_time,
    summary_table,
)
from bmu_ranking import BmuRanking
from ranking_methods import RankingMethod


def run_app():

    st.title("Group 7 Demo: Green Dispatch")

    ranking_mode = st.radio(
        "BOA Ranking Method", ["Emissions only", "Emissions-Adjusted Cost"]
    )
    co_cost = 0.0

    all_boas_df = pd.read_parquet("data/carbon_emissions_results.parquet")
    bmu_ranking_class_original = BmuRanking(
        all_boas_df, RankingMethod(ranking_mode), 0.0
    )
    bmu_ranking_class_adjusted = BmuRanking(
        all_boas_df, RankingMethod(ranking_mode), co_cost
    )

    adjusted_costs_df = bmu_ranking_class_adjusted.ranked_bmu_df
    original_costs_df = bmu_ranking_class_original.ranked_bmu_df

    col5, col6 = st.columns(2)

    table_list = summary_table(
        original_df=original_costs_df, adjusted_df=adjusted_costs_df
    )
    col5.dataframe(
        table_list[0],
        hide_index=True,
    )

    col6.metric(label="Cost of CO₂ savings", value=str(table_list[1]) + " £/tCO₂")

    if ranking_mode == "Emissions-Adjusted Cost":
        co_cost = st.slider(
            "Carbon cost (£/tCO2)", min_value=0.0, max_value=50.0, value=25.0, step=1.0
        )

    # Cost graphs

    cost_max = (
        max(
            adjusted_costs_df["total_cost_pounds"].max(),
            original_costs_df["total_cost_pounds"].max(),
        )
        + 100000
    )
    cost_min = (
        min(
            adjusted_costs_df["total_cost_pounds"].min(),
            original_costs_df["total_cost_pounds"].min(),
        )
        - 100000
    )

    cost_over_time_plot = plot_cost_over_time(
        original_costs_df,
        axis_min=cost_min,
        axis_max=cost_max,
    )
    col1, col2 = st.columns(2)

    cost_over_time_plot_adjusted = plot_cost_over_time(
        adjusted_costs_df,
        title="Emissions-adjusted cost over time (£)",
        line_colour="#000080",
        axis_min=cost_min,
        axis_max=cost_max,
    )
    col1.plotly_chart(cost_over_time_plot)
    col2.plotly_chart(cost_over_time_plot_adjusted)

    # Carbon graphs

    # TODO: Replace with function calls

    carbon_max = (
        max(
            adjusted_costs_df["carbon_emissions_tonnes"].max(),
            original_costs_df["carbon_emissions_tonnes"].max(),
        )
        + 100000
    )
    carbon_min = (
        min(
            adjusted_costs_df["carbon_emissions_tonnes"].min(),
            original_costs_df["carbon_emissions_tonnes"].min(),
        )
        - 100000
    )

    carbon_over_time_plot = plot_emissions_over_time(
        original_costs_df,
        axis_min=carbon_min,
        axis_max=carbon_max,
    )
    col3, col4 = st.columns(2)

    carbon_over_time_plot_adjusted = plot_emissions_over_time(
        adjusted_costs_df,
        title="Emissions-adjusted CO₂ over time (£)",
        line_colour="#450003",
        axis_min=carbon_min,
        axis_max=carbon_max,
    )
    col3.plotly_chart(carbon_over_time_plot)
    col4.plotly_chart(carbon_over_time_plot_adjusted)


if __name__ == "__main__":
    run_app()
