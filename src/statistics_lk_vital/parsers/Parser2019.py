from openpyxl import load_workbook
from utils import Log

from statistics_lk_vital.core.MortalityStatistic import MortalityStatistic

log = Log('Parser2019')


def parse_int(x):
    try:
        return int(x)
    except Exception:
        return 0


def parse_col_to_age(cells):
    col_to_age = []
    non_none_cell = None
    for cell in cells:
        if cell is not None:
            cell = str(cell).lower()
            non_none_cell = cell.lower()
        col_to_age.append(non_none_cell)
    return col_to_age


def parse_col_to_gender(cells):
    col_to_gender = []
    non_none_cell = None
    for cell in cells:
        if cell is not None:
            non_none_cell = str(cell).lower()
        col_to_gender.append(non_none_cell)
    return col_to_gender


class Parser2019:
    def __init__(self, year: str, file_path: str):
        self.year = year
        self.file_path = file_path

    def parse(self) -> list[MortalityStatistic]:  # noqa
        workbook = load_workbook(filename=self.file_path)
        sheet = workbook.active
        statistics = []
        i_row = 0
        col_to_age = None
        col_to_gender = None

        i_data_row_start = None
        for i_row, row in enumerate(sheet.iter_rows(values_only=True)):
            cells0 = list(row)[0]
            if cells0 is not None and cells0.strip().startswith('1-'):
                i_data_row_start = i_row
                break

        for i_row, row in enumerate(sheet.iter_rows(values_only=True)):
            cells = list(row)

            if i_row < i_data_row_start - 2:
                continue

            if i_row == i_data_row_start - 2:  # Age:
                col_to_age = parse_col_to_age(cells)
                continue

            if i_row == i_data_row_start - 1:  # Gender
                col_to_gender = parse_col_to_gender(cells)
                continue

            if cells[0] is None:
                continue

            death_description = cells[0].strip()
            if (
                death_description is None
                or death_description == 'Grand Total'
            ):
                continue

            for i_cell, cell in enumerate(cells):
                if i_cell == 0:
                    continue

                deaths = parse_int(cell)
                statistic = MortalityStatistic(
                    description_raw=death_description,
                    year=self.year,
                    gender_raw=col_to_gender[i_cell],
                    age_raw=col_to_age[i_cell],
                    deaths=deaths,
                )

                statistics.append(statistic)
        return statistics
