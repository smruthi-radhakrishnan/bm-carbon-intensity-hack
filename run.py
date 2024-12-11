import streamlit as st
import pandas as pd
from app.components.graph_plotting_functions import plot_emissions_over_time
from bmu_ranking import BmuRanking
from ranking_methods import RankingMethod


def run_app():
    st.title("Group 7 Demo: Green Dispatch")
    
    
    ranking_mode = st.radio("BOA Ranking Method", ["Emissions only", "Emissions-Adjusted Cost"])
    co_cost = 0.
    
    if ranking_mode == "Emissions-Adjusted Cost":
        co_cost = st.slider("Carbon cost (£/tCO2)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    
    # TODO: Replace with function calls
    all_boas_df = pd.read_parquet("carbon_emissions_results.parquet")
    cost_ranked_df  = BmuRanking(all_boas_df, RankingMethod(ranking_mode), co_cost).ranked_bmu_df

    line_plot = plot_emissions_over_time(cost_ranked_df)
    st.plotly_chart(line_plot)
    

if __name__ == "__main__":
    run_app()