import pandas as pd
from add_demand import add_demand
from ranking_methods import RankingMethod


class BmuRanking:
    def __init__(self, all_boas_df: pd.DataFrame, ranking_method: RankingMethod, carbon_cost_pounds_per_mwh: float):
        self.selected_ranking_method = ranking_method
        self.carbon_cost_pounds_per_mwh = carbon_cost_pounds_per_mwh
        self.all_boas_df = self._get_all_boas_df(all_boas_df)
        self.ranked_bmu_df = self.rank_bmus_per_sp()
    
    def _get_all_boas_df(self, boa_df: pd.DataFrame):
        cleaned_boa_df= boa_df.copy()
        cleaned_boa_df["start_time"] = pd.to_datetime(cleaned_boa_df["start_time"])
        cleaned_boa_df = add_demand(cleaned_boa_df)
        return cleaned_boa_df


    def calculate_carbon_cost_per_boa(self):
        objective_df = self.all_boas_df.copy()
        objective_df["total_cost_pounds"] = objective_df["net_vol"] * objective_df["avg_price"]
        objective_df["carbon_cost_pounds"] = objective_df["carbon_emissions_tonnes"] * self.carbon_cost_pounds_per_mwh
        objective_df["carbon_cost_pounds_per_mwh"] = objective_df["carbon_cost_pounds"] / objective_df["net_vol"]
        objective_df["carbon_adjusted_cost_pounds_per_mwh"] = objective_df["avg_price"] + objective_df["carbon_cost_pounds_per_mwh"]
        return objective_df

    def rank_bmus_per_sp(self):
        if self.selected_ranking_method == RankingMethod.EMISSIONS_ONLY:
            ranked_df = self.order_df_by_column(self.all_boas_df, "carbon_emissions_tonnes")
        else:
            boas_with_carbon_adjusted_cost = self.calculate_carbon_cost_per_boa()
            ranked_df = self.order_df_by_column(boas_with_carbon_adjusted_cost, "carbon_adjusted_cost_pounds_per_mwh")
        
        ranked_df["cumulative_demand"] = ranked_df.groupby("start_time_gmt", as_index=False)["net_vol"].cumsum()
        ranked_df["required_bmu"] = ranked_df["cumulative_demand"] <= ranked_df["demand"]
        return ranked_df.loc[ranked_df["required_bmu"] == True]

    def order_df_by_column(self, df:pd.DataFrame, column_name: str, ascending:bool=True) -> pd.DataFrame:
        return df.sort_values(["start_time_gmt", column_name], ascending=[True, ascending])


if __name__ == "__main__":
    all_boas_df = pd.read_parquet("carbon_emissions_results.parquet")
    print("This is happening")
    ranked_df = BmuRanking(all_boas_df, RankingMethod.EMISSIONS_ONLY, 0.).ranked_bmu_df
    print(ranked_df)
