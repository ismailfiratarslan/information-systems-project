import pandas as pd
import datetime, time
import numpy as np


def convert(path_input_day, path_output, household, start_date, end_date):
    df_day = pd.read_csv(path_input_day)
    df_day = df_day[df_day["LCLid"] == household]
    df_day_mask = df_day[df_day.day.between(start_date, end_date)]
    df_day_mask.to_csv(path_output, index=False, header=True, float_format='%.4f')
