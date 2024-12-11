import streamlit as st
import pandas as pd
from app.components.graph_plotting_functions import plot_emissions_over_time


def run_app():
    st.title("Group 7 Demo: Green Dispatch")
    emissions_per_sp_df = pd.read_csv("data/test_results.csv")
    line_plot = plot_emissions_over_time(emissions_per_sp_df)
    st.plotly_chart(line_plot)
    

if __name__ == "__main__":
    run_app()