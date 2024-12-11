import pandas as pd
import plotly.express as px

def plot_emissions_over_time(output_df: pd.DataFrame):
    output_df["ACCEPT TIME"] = pd.to_datetime(output_df["ACCEPT TIME"])
    output_df["accept_time_gmt"] = output_df["ACCEPT TIME"].dt.tz_localize("UTC")
    output_df["time_to_target_mins"] = pd.to_timedelta(output_df["TIME TO TARGET (MINS)"], unit='min')
    output_df["target_time"] = output_df["accept_time_gmt"] + output_df["time_to_target_mins"]
    emissions_per_sp = output_df.groupby("target_time", as_index=False)["carbon_emissions_tonnes"].sum()
    fig = px.line(emissions_per_sp, x="target_time", y="carbon_emissions_tonnes")
    fig.update_layout(title="Emissions over time")
    return fig