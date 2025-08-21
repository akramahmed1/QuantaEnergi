import pandas as pd

def etl_iot_data(df: pd.DataFrame):
    # Clean and transform
    df = df.dropna()
    return df