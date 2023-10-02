import os

from statistics_lk_vital.core.MortalityStatistic import MortalityStatistic
from statistics_lk_vital.parsers.Parser2019 import Parser2019

dir_data = os.path.abspath('data')
print(dir_data)


def main():
    for year in range(1998, 2023):
        file_path = os.path.join(dir_data, f'cause-of-death-{year}.xlsx')
        if not os.path.exists(file_path):
            continue
        parser = Parser2019(year, file_path)
        statistics = parser.parse()
        MortalityStatistic.write(
            statistics,
            os.path.join(dir_data, f'norm.cause-of-death-{year}.xlsx'),
        )


if __name__ == '__main__':
    main()
