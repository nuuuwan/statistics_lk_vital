from functools import cached_property

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from utils import Log, xmlx

from statistics_lk_vital.core.AgeRange import AgeRange
from statistics_lk_vital.core.Description import Description
from statistics_lk_vital.core.Gender import Gender
from statistics_lk_vital.core.MortalityStatistic import MortalityStatistic
from statistics_lk_vital.renderers.RenderStatisticsRenderers import \
    RenderStatisticsRenderers

_ = xmlx._


log = Log('RenderStatistics')
WIDTH, HEIGHT = 1600, 900
PADDING = 25
BASE_FONT_SIZE = 12
BASE_FONT_FAMILY = 'TCM_____'
N_DISPLAY = 10


class RenderStatistics(RenderStatisticsRenderers):
    def __init__(self, statistics: list[MortalityStatistic], gender: str):
        self.statistics = statistics
        self.gender = gender
        self.prev_location = {}

    @property
    def year(self):
        return self.statistics[0].year

    @cached_property
    def filtered_statistics(self):
        filtered_statistics = []
        for statistic in self.statistics:
            gender = Gender.parse(statistic.gender_raw)
            if str(gender) not in [self.gender]:
                continue
            age = AgeRange.parse(statistic.age_raw)
            if not age:
                continue
            description = Description(statistic.description_raw)
            if not description.is_top_level:
                continue
            filtered_statistics.append(statistic)
        log.debug(f'Filtered statistics: {len(filtered_statistics)}')
        return filtered_statistics

    def get_idx_ad_sorted(self):
        idx_ad = {}
        for statistic in self.filtered_statistics:
            age = str(AgeRange.parse(statistic.age_raw))
            description = Description(statistic.description_raw)
            row_code = description.row_code
            if age not in idx_ad:
                idx_ad[age] = {}
            if row_code not in idx_ad[age]:
                idx_ad[age][row_code] = 0
            idx_ad[age][row_code] += statistic.deaths

        idx_ad_sorted = {}
        for age, idx_d in idx_ad.items():
            idx_ad_sorted[age] = dict(
                sorted(idx_d.items(), key=lambda x: x[1], reverse=True)
            )
        return idx_ad_sorted

    def get_idx_da_sorted(self):
        idx_da = {}
        for statistic in self.filtered_statistics:
            age = str(AgeRange.parse(statistic.age_raw))
            description = Description(statistic.description_raw)
            row_code = description.row_code
            if row_code not in idx_da:
                idx_da[row_code] = {}
            if age not in idx_da[row_code]:
                idx_da[row_code][age] = 0

            idx_da[row_code][age] += statistic.deaths

        idx_da_sorted = {}
        for row_code, idx_a in idx_da.items():
            idx_da_sorted[row_code] = dict(
                sorted(idx_a.items(), key=lambda x: x[1], reverse=True)
            )
        return idx_da_sorted

    def get_row_code_to_display_age_group(self):
        idx_da_sorted = self.get_idx_da_sorted()
        row_code_to_display_age_group = {}
        for row_code, idx_a in idx_da_sorted.items():
            row_code_to_display_age_group[row_code] = list(idx_a.keys())[0]
        return row_code_to_display_age_group

    def write(self, svg_path: str):
        svg = _(
            'svg',
            [self.render_header(), self.render_body(), self.render_footer()],
            dict(width=WIDTH, height=HEIGHT),
        )
        svg.store(svg_path)
        log.info(f'Wrote {svg_path}')

        drawing = svg2rlg(svg_path)
        png_path = svg_path[:-3] + 'png'
        renderPM.drawToFile(drawing, png_path, fmt="PNG")
        log.info(f'Saved {png_path}')
