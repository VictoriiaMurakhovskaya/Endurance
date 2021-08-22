import openpyxl as op
import pandas as pd
import numpy as np


def make_results(df):
    lap_list = pd.Series(df.values.T.reshape(1, -1).ravel()).astype('str')
    lap_list = lap_list.loc[lap_list != '0.0'].str.replace(r'[^\d^\:^\.]', '').astype('str').copy()
    lap_list = lap_list.apply(lambda x: x if x.find(':') > -1 else '0:' + x).str.replace('.', ':').copy()
    laps_df = lap_list.str.split(':', expand=True)

    for col in laps_df:
        laps_df[col] = laps_df[col].str.replace('nan', '0')
        laps_df = laps_df.loc[~laps_df[2].isna()].copy()

        laps_df[col] = laps_df[col].astype('int64')

    lap_list = pd.to_timedelta(laps_df[0], unit='min') +\
               pd.to_timedelta(laps_df[1], unit='s') +\
               pd.to_timedelta(laps_df[2], unit='ms')

    border_time = pd.to_timedelta(2, unit='m')
    pits_list = lap_list.loc[lap_list > border_time].index.tolist()
    pits_list = [0, *pits_list]

    n_laps, mean_times, intervals, cumulative, cumulates, run_time_lst, cum_run_time, run_time =\
        [], [], [], 0, [], [], [], pd.to_timedelta(0, unit='m')
    for i, pit in enumerate(pits_list):
        if i == 0:
            interval = (0, pits_list[i + 1] - 1)
        elif i == len(pits_list) - 1:
            interval = (pit + 1, len(lap_list) - 1)
        else:
            interval = (pit + 1, pits_list[i + 1] - 1)

        sub_series = lap_list.loc[(lap_list.index >= interval[0]) & (lap_list.index <= interval[1])]

        if i == 0:
            cumulative = sub_series.sum()
        else:
            cumulative += sub_series.sum() + lap_list[pit]

        run_time += sub_series.sum()

        cumulates.append(cumulative)
        cum_run_time.append(run_time)
        run_time_lst.append(sub_series.sum())
        n_laps.append(len(sub_series))
        mean_times.append(sub_series.mean())
        intervals.append(interval)

    df_result = pd.DataFrame({'N laps': n_laps,
                              'Interval': intervals,
                              'Avg time': mean_times,
                              'Interval run time': run_time_lst,
                              'Cumulative time': cumulates,
                              'Cumulative run time': cum_run_time})
    df_result['Avg time'] = df_result['Avg time'].apply(lambda x: x.total_seconds())

    for item in ['Interval run time', 'Cumulative time', 'Cumulative run time']:
        df_result[item] = df_result[item].apply(lambda x: x.total_seconds() / 60)

    check_cumulative = lap_list.sum()
    run_time = lap_list.loc[~lap_list.index.isin(pits_list)].sum()
    pit_time = lap_list.loc[lap_list.index.isin(pits_list)].sum()

    return df_result


if __name__ == '__main__':
    wb = op.load_workbook(filename='../data_1.xlsx')
    ws_names = wb.sheetnames

    with pd.ExcelWriter('../results.xlsx', engine='xlsxwriter') as writer:
        for sheet in ws_names:
            df = pd.read_excel("data_1.xlsx", sheet_name=sheet, index_col=0)
            make_results(df).to_excel(excel_writer=writer, sheet_name=sheet)

