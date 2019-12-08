import os

import pandas as pd

from .settings import DATA_PATH, RESULTS_PATH


def get_data():
    return pd.read_csv(os.path.join(DATA_PATH, 'family_data.csv'), index_col="family_id")


def save_submission(assignments: pd.DataFrame, name: str):
    file_path = os.path.join(RESULTS_PATH, '{}.csv'.format(name))
    assignments.to_csv(file_path, index=False)
