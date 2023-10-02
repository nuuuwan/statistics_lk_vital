from dataclasses import dataclass
from functools import cached_property

from openpyxl import Workbook
from utils import Log

from statistics_lk_vital.core.AgeRange import AgeRange
from statistics_lk_vital.core.Description import Description
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
        return Description(self.description_raw).description_raw

    @staticmethod
    def get_idx_gda(statistics: list['MortalityStatistic']) -> dict:
        idx_gda = {}
        for statistic in statistics:
            gender = statistic.gender
            if gender is None:
                continue
            gender = str(gender)

            age_range = statistic.age_range
            if age_range is None:
                continue
            age_range = str(age_range)

            description = statistic.description

            # idx_gda
            idx_gda[gender] = idx_gda.get(gender, {})
            idx_gda[gender][description] = idx_gda[gender].get(
                description, {}
            )
            idx_gda[gender][description][age_range] = idx_gda[gender][
                description
            ].get(age_range, 0)
            idx_gda[gender][description][age_range] += statistic.deaths
        return idx_gda

    @staticmethod
    def get_idx_gad(statistics: list['MortalityStatistic']) -> dict:
        idx_gad = {}
        for statistic in statistics:
            gender = statistic.gender
            if gender is None:
                continue
            gender = str(gender)

            age_range = statistic.age_range
            if age_range is None:
                continue
            age_range = str(age_range)

            description = statistic.description

            # idx_gad
            idx_gad[gender] = idx_gad.get(gender, {})
            idx_gad[gender][age_range] = idx_gad[gender].get(age_range, {})
            idx_gad[gender][age_range][description] = idx_gad[gender][
                age_range
            ].get(description, 0)
            idx_gad[gender][age_range][description] += statistic.deaths

        return idx_gad

    @staticmethod
    def write(statistics: list['MortalityStatistic'], file_path: str):
        assert file_path.endswith('.xlsx')

        idx_gda = MortalityStatistic.get_idx_gda(statistics)

        wb = Workbook()
        for gender in idx_gda:
            ws = wb.create_sheet(gender)
            n_descriptions = len(idx_gda[gender].keys())

            for i_row, description in enumerate(idx_gda[gender].keys()):
                ws.cell(i_row + 2, 1).value = description

                for i_col, age_range in enumerate(
                    idx_gda[gender][description].keys()
                ):
                    if i_row == 0:
                        ws.cell(1, i_col + 2).value = age_range

                    deaths = idx_gda[gender][description][age_range]
                    ws.cell(i_row + 2, i_col + 2).value = deaths

            log.debug(f'Wrote {n_descriptions} descriptions for {gender}')

        wb.remove(wb['Sheet'])

        wb.save(file_path)
        log.info(f'Wrote {len(statistics)} statistics to {file_path}')
