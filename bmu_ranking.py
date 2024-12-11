import pandas as pd
from ranking_methods import RankingMethod


class BmuRanking:
    def __init__(self, all_boas_df: pd.DataFrame, ranking_method: RankingMethod, carbon_cost_pounds_per_mwh: float):
        self.selected_ranking_method = ranking_method
        self.carbon_cost_pounds_per_mwh = carbon_cost_pounds_per_mwh
        self.all_boas_df = self._get_timestamp_from_date_and_sp(all_boas_df)
        self.ranked_bmu_df = self.rank_bmus_per_sp()
    
    def _get_timestamp_from_date_and_sp(self, boa_df: pd.DataFrame):
        cleaned_boa_df= boa_df.copy()
        cleaned_boa_df["settlement_date"] = pd.to_datetime(cleaned_boa_df["Settlement Date"])
        cleaned_boa_df["sp_start_minutes"] = pd.to_timedelta(cleaned_boa_df["Settlement Period"] * 30, unit='min')
        cleaned_boa_df["sp_datetime"] = cleaned_boa_df["settlement_date"] + cleaned_boa_df["sp_start_minutes"] 
        return cleaned_boa_df


    def calculate_carbon_cost_per_boa(self):
        objective_df = self.all_boas_df.copy()
        objective_df["total_cost_pounds"] = objective_df["NET VOL (MWh)"] * objective_df["AVG PRICE (GBP/MWh)"]
        objective_df["carbon_cost_pounds"] = objective_df["carbon_emissions_tonnes"] * self.carbon_cost_pounds_per_mwh
        objective_df["carbon_cost_pounds_per_mwh"] = objective_df["carbon_cost_pounds"] / objective_df["NET VOL (MWh)"]
        objective_df["carbon_adjusted_cost_pounds_per_mwh"] = objective_df["AVG PRICE (GBP/MWh)"] + objective_df["carbon_cost_pounds_per_mwh"]
        return objective_df

    def rank_bmus_per_sp(self):
        if self.selected_ranking_method == RankingMethod.EMISSIONS_ONLY:
            ranked_df = self.order_df_by_column(self.all_boas_df, "carbon_emissions_tonnes")
        else:
            boas_with_carbon_adjusted_cost = self.calculate_carbon_cost_per_boa()
            ranked_df = self.order_df_by_column(boas_with_carbon_adjusted_cost, "carbon_adjusted_cost_pounds_per_mwh")
        
        ranked_df["cumulative_demand"] = ranked_df.groupby("sp_datetime", as_index=False)["NET VOL (MWh)"].cumsum()
        ranked_df["required_bmu"] = ranked_df["cumulative_demand"] <= ranked_df["required_demand"]
        return ranked_df.loc[ranked_df["required_bmu"] is True]

    def order_df_by_column(self, df:pd.DataFrame, column_name: str, ascending:bool=True) -> pd.DataFrame:
        return df.groupby("sp_datetime", as_index=False).sort_values(by=column_name, ascending=ascending)
