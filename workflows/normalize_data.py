import os

from statistics_lk_vital.core.MortalityStatistic import MortalityStatistic
from statistics_lk_vital.parsers.Parser2019 import Parser2019
from statistics_lk_vital.renderers.RenderStatistics import RenderStatistics

dir_data = os.path.abspath('data')
dir_images = os.path.abspath('images')


def main():
    for year in range(1998, 2023):
        if year != 2019:
            continue
        file_path = os.path.join(dir_data, f'cause-of-death-{year}.xlsx')
        if not os.path.exists(file_path):
            continue
        parser = Parser2019(year, file_path)
        statistics = parser.parse()
        MortalityStatistic.write(
            statistics,
            os.path.join(dir_data, f'norm.cause-of-death-{year}.xlsx'),
        )
        for gender in ['female', 'male']:
            RenderStatistics(statistics, gender).write(
                os.path.join(
                    dir_images, f'cause-of-death-{year}-{gender}.svg'
                ),
            )


if __name__ == '__main__':
    main()
