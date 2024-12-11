import pandas as pd
import plotly.express as px

def plot_emissions_over_time(output_df: pd.DataFrame):
    emissions_per_sp = output_df.groupby("start_time_gmt", as_index=False)["carbon_emissions_tonnes"].sum()
    fig = px.line(emissions_per_sp, x="start_time_gmt", y="carbon_emissions_tonnes")
    fig.update_layout(title="Emissions over time")
    return fig