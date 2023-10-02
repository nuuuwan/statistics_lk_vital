from dataclasses import dataclass
from functools import cached_property

import openpyxl
from openpyxl import Workbook
from utils import Log

from statistics_lk_vital.core.AgeRange import AgeRange
from statistics_lk_vital.core.Description import SIMPLE_TO_COLOR, Description
from statistics_lk_vital.core.Gender import Gender

log = Log('MortalityStatistic')


@dataclass
class MortalityStatistic:
    description_raw: str
    year: int
    gender_raw: str
    age_raw: str
    deaths: int

    @cached_property
    def gender(self) -> str:
        return Gender.parse(self.gender_raw)

    @cached_property
    def age_range(self) -> str:
        return AgeRange.parse(self.age_raw)

    @cached_property
    def description(self) -> str:
        return Description(self.description_raw).simple

    @staticmethod
    def get_idx(statistics: list['MortalityStatistic']) -> dict:
        idx_gda = {}
        idx_gad = {}
        for statistic in statistics:
            gender = statistic.gender
            if gender is None:
                continue
            gender = str(gender)

            description = statistic.description

            age_range = statistic.age_range
            if age_range is None:
                continue
            age_range = str(age_range)

            # idx_gda
            if gender not in idx_gda:
                idx_gda[gender] = {}
            if description not in idx_gda[gender]:
                idx_gda[gender][description] = {}
            if age_range not in idx_gda[gender][description]:
                idx_gda[gender][description][age_range] = 0
            idx_gda[gender][description][age_range] += statistic.deaths

            # idx_gad
            if gender not in idx_gad:
                idx_gad[gender] = {}
            if age_range not in idx_gad[gender]:
                idx_gad[gender][age_range] = {}
            if description not in idx_gad[gender][age_range]:
                idx_gad[gender][age_range][description] = 0
            idx_gad[gender][age_range][description] += statistic.deaths

        return idx_gda, idx_gad

    @staticmethod
    def write_list(statistics: list['MortalityStatistic'], file_path: str):
        assert file_path.endswith('.xlsx')

        idx_gda, idx_gad = MortalityStatistic.get_idx(statistics)
        wb = Workbook()
        most_common_description_set = set()
        for gender in idx_gda:
            ws = wb.create_sheet(gender)

            for i_row, description in enumerate(idx_gda[gender].keys()):
                ws.cell(i_row + 2, 1).value = description

                for i_col, age_range in enumerate(
                    idx_gda[gender][description].keys()
                ):
                    if i_row == 0:
                        ws.cell(1, i_col + 2).value = age_range

                    deaths = idx_gda[gender][description][age_range]
                    ws.cell(i_row + 2, i_col + 2).value = deaths

            i_row_most_common = len(idx_gda[gender].keys()) + 3
            N_MOST_COMMON = 10
            for i in range(N_MOST_COMMON):
                position = {
                    0: 'Top',
                    1: '2nd',
                    2: '3rd',
                }.get(i, f'{i + 1}th')
                ws.cell(i_row_most_common + i + 1, 1).value = position

            for i_col, age_range in enumerate(idx_gad[gender].keys()):
                ws.cell(i_row_most_common, i_col + 2).value = age_range

                sorted_description_and_deaths = sorted(
                    idx_gad[gender][age_range].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
                total_deaths = sum(
                    deaths for _, deaths in sorted_description_and_deaths
                )
                for i in range(N_MOST_COMMON):
                    description, deaths = sorted_description_and_deaths[i + 1]
                    most_common_description_set.add(description)
                    p_deaths = deaths / total_deaths
                    cell = ws.cell(i_row_most_common + i + 1, i_col + 2)
                    cell.value = f'{p_deaths:.0%} {description}'

                    my_red = openpyxl.styles.colors.Color(
                        rgb=SIMPLE_TO_COLOR.get(description, '00FFFFFF')
                    )
                    my_fill = openpyxl.styles.fills.PatternFill(
                        patternType='solid', fgColor=my_red
                    )
                    cell.fill = my_fill
        wb.save(file_path)
        log.info(f'Wrote {len(statistics)} statistics to {file_path}')
