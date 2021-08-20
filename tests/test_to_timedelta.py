import pandas as pd
import numpy as np

if __name__ == '__main__':
    arr = ['59.343']
    print(pd.to_timedelta(arr, unit='s'))