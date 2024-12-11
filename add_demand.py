#import numpy as np
import pandas as pd
#import re

#boas_data = pd.read_csv("data/test_results.csv")
#boas_data.columns = [re.sub("\_\_", "_", re.sub(r"[^A-Za-z0-9]", "_", re.sub(r'\)$', '', column.lower()))) for column in boas_data.columns]

# Add on some dummy accepted info
# boas_data["accepted"] = np.random.randint(2, size=boas_data.shape[0])

def add_demand(boas_data):
    # Extract day from accepted time
    boas_data["date"] = pd.to_datetime(boas_data['start_time']).dt.date

    # Add on demand by summing volume across each settlement period within each day
    boas_data["demand"] = boas_data[boas_data["accepted"]==1].groupby(["main_sp", "date"] )["net_vol_mwh"].transform("sum")

    return(boas_data)