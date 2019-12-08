import os


SETTINGS_PATH = os.path.abspath(__file__)
ROOT_PATH = os.path.dirname(os.path.dirname(SETTINGS_PATH))     # two levels above
DATA_PATH = os.path.join(ROOT_PATH, 'data')
RESULTS_PATH = os.path.join(ROOT_PATH, 'results')
