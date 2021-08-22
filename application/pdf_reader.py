import pathlib

import camelot
import ctypes
import numpy as np
import pandas as pd
import re

from camelot.core import TableList, Table
from ctypes.util import find_library
from typing import Union


class PdfReader:
    """
    Класс используется для преобразования pdf определенного формата в Excel таблицы.
    PDF содержит табличную информацию, поэтому используется camelot для распознавания таких таблиц
    Последовательность работы:
    - распознавание PDF в объект camelot.core.TableList
    - формирование списка ячеек из полученных TableList
    - выделение в списке заголовков
    - разделение списка по заголовкам на датафреймы Pandas
    - сохранение полученного списка фреймов на отдельные листы Excel
    """

    def __init__(self):
        # проверка необходимой для camelot библиотеки
        if not find_library("".join(("gsdll", str(ctypes.sizeof(ctypes.c_void_p) * 8), ".dll"))):
            raise FileNotFoundError('gs*.dll not found')

    @classmethod
    def read_pdf(cls, file_in: Union[str, pathlib.Path], pages='1-end') -> TableList:
        """
        Чтение PDF - файла с использованием Camelot
        :param file_in: файл для чтения
        :param pages: страницы (номера страниц), которые должны быть распознаны
        :return: список датафреймов - объект Camelot
        """
        return camelot.read_pdf(file_in, pages=pages)

    @staticmethod
    def define_headers_indexes(res_list: list[str]) -> list[int]:
        """
        Поиск заголовков (имя участника, название команды) в ячейках распознаного списка
        Далее по ним происходит деление на отдельные таблицы
        :param res_list: список ячееку
        :return: индексы заголовков
        """
        headers_indexes = []

        for i, item in enumerate(res_list):
            if isinstance(item, str):
                if re.findall(r'[\d\s]{1,3}:[\-\s\dA-Za-z]{3,}', item):
                    headers_indexes.append(i)

        return headers_indexes

    @classmethod
    def extract_times_from_tablelist(cls, tables: TableList) -> list[str]:
        """
        Получение списка времен из результата парсинга Camelot
        :param tables: список датафреймов
        :return: список времени в формате list
        """
        res_list = []
        for i, table in enumerate(tables):
            try:
                res_list.extend(cls.extract_times(table))
            except:
                pass
        return res_list

    @classmethod
    def times_list_to_dict(cls, times_lst: list[str], headers:list[int]) -> dict:
        """
        Разбивка единого списка времен на подсписки по заголовкам
        :param times_lst: список времен
        :param headers: список положения заголовков
        :return: словарь списков (ключ - заголовок, значение - список времен)
        """
        df_dict = {}

        for i, header_n in enumerate(headers):
            if len(headers) > i + 1:
                next_header = headers[i + 1] - 1
            else:
                next_header = len(times_lst)
            df_dict.update({times_lst[header_n - 1] + times_lst[header_n]: times_lst[header_n + 1: next_header]})

        return df_dict

    @classmethod
    def write_to_excel(cls, df_dict: dict, file_out: Union[str, pathlib.Path]) -> None:
        """
        Запись полученных списков времен в Excel файл для последующего контроля
        :param df_dict: словарь со списками времен
        :param file_out: название конечного файла Excel (включая необходимый путь)
        :return:
        """
        with pd.ExcelWriter(file_out, engine='xlsxwriter') as writer:
            for k, v in df_dict.items():
                n_rows = len(v) // 15 + 1
                arr = np.concatenate((np.array(v), np.zeros(n_rows * 15 - len(v))))
                pd.DataFrame(arr.reshape(15, n_rows)).T.to_excel(writer, sheet_name=re.sub(r'[\[\]:\*\?/]', '', k))

    @classmethod
    def extract_times(cls, table: Table) -> list[str]:
        data_lst = []
        for col in table.df:
            data_lst.extend(table.df.at[0, col].split('\n'))

        return data_lst

    @staticmethod
    def pdf_to_excel(file_in: Union[str, pathlib.Path], file_out: Union[str, pathlib.Path]):
        """
        Основной статический метод для преобразования pdf и сохранения в Excel
        :param file_in: входной PDF-файл
        :param file_out: выходной XLSX - файл
        :return: True, None - операция успешна
                 False, Message - операция неуспешна, Message - код ошибки
        """
        pr = PdfReader()

        try:
            tables = pr.read_pdf(file_in)
            times_list = pr.extract_times_from_tablelist(tables)
            headers_indexes = pr.define_headers_indexes(times_list)
            df_dict = pr.times_list_to_dict(times_list, headers_indexes)
            pr.write_to_excel(df_dict, file_out)
            return True, None
        except Exception as ex:
            return False, f'{ex}'




