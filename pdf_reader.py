import camelot
import pandas as pd
import numpy as np
import ctypes
from ctypes.util import find_library
import sys
import re
import logging


FILE = 'data_endurance.pdf'
LOG_FILENAME = 'log.log'

if __name__ == '__main__':

    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

    if not find_library("".join(("gsdll", str(ctypes.sizeof(ctypes.c_void_p) * 8), ".dll"))):
        sys.exit(-1)

    tables = camelot.read_pdf(FILE, pages='1-end')

    def extract_times(table):

        data_lst = []
        for col in table.df:
            data_lst.extend(table.df.at[0, col].split('\n'))

        return data_lst

    res_list = []
    for i, table in enumerate(tables):
        try:
            res_list.extend(extract_times(table))
        except:
            logging.exception(f'Exception with page {i}')

    headers_indexes = []

    for i, item in enumerate(res_list):
        if isinstance(item, str):
            if res := re.findall(r'[\d\s]{1,3}:[\-\s\dA-Za-z]{3,}', item):
                headers_indexes.append(i)

    df_dict = {}
    for i, header_n in enumerate(headers_indexes):
        if len(headers_indexes) > i + 1:
            next_header = headers_indexes[i + 1] - 1
        else:
            next_header = len(res_list)
        df_dict.update({res_list[header_n - 1] + res_list[header_n]: res_list[header_n + 1: next_header]})

    with pd.ExcelWriter("data_1.xlsx", engine='xlsxwriter') as writer:
        for k, v in df_dict.items():
            n_rows = len(v) // 15 + 1
            arr = np.concatenate((np.array(v), np.zeros(n_rows * 15 - len(v))))
            pd.DataFrame(arr.reshape(15, n_rows)).T.to_excel(writer, sheet_name=re.sub(r"[\[\]:\*\?/]", '', k))