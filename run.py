import streamlit as st
import pandas as pd
from app.components.graph_plotting_functions import (
    plot_emissions_over_time,
    plot_cost_over_time,
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
    bmu_ranking_class = BmuRanking(all_boas_df, RankingMethod(ranking_mode), co_cost)

    cost_ranked_df = bmu_ranking_class.ranked_bmu_df

    cost_over_time_plot = plot_cost_over_time(cost_ranked_df)
    st.plotly_chart(cost_over_time_plot)

    if ranking_mode == "Emissions-Adjusted Cost":
        co_cost = st.slider(
            "Carbon cost (£/tCO2)", min_value=0.0, max_value=1.0, value=0.5, step=0.01
        )

    # TODO: Replace with function calls

    line_plot = plot_emissions_over_time(cost_ranked_df)
    st.plotly_chart(line_plot)


if __name__ == "__main__":
    run_app()
