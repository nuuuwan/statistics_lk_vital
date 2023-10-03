import math

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from utils import Log, xmlx

from statistics_lk_vital.core.AgeRange import AgeRange
from statistics_lk_vital.core.Description import (ROW_CODE_TO_COLOR,
                                                  ROW_CODE_TO_SIMPLE,
                                                  Description)
from statistics_lk_vital.core.Gender import Gender
from statistics_lk_vital.core.MortalityStatistic import MortalityStatistic

_ = xmlx._


log = Log('RenderStatistics')
WIDTH, HEIGHT = 1600, 900
PADDING = 25
BASE_FONT_SIZE = 12
BASE_FONT_FAMILY = 'GIL_____'
N_DISPLAY = 10


class RenderStatistics:
    @staticmethod
    def transform(px: float, py: float):
        return (
            px * (WIDTH - PADDING * 2) + PADDING,
            (1 - py) * (HEIGHT - PADDING * 2) + PADDING,
        )

    @staticmethod
    def font_size(p: float):
        return BASE_FONT_SIZE * p

    def __init__(self, statistics: list[MortalityStatistic]):
        self.statistics = statistics

    @property
    def year(self):
        return self.statistics[0].year

    def get_idx_ad_sorted(self):
        idx_ad = {}
        for statistic in self.statistics:
            gender = Gender.parse(statistic.gender_raw)
            if gender is None:
                continue
            gender = str(gender)
            if gender not in ['male', 'female']:
                continue
            age = AgeRange.parse(statistic.age_raw)
            if not age:
                continue
            age = str(age)

            description = Description(statistic.description_raw)
            if not description.is_top_level:
                continue

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
        for statistic in self.statistics:
            gender = Gender.parse(statistic.gender_raw)
            if gender is None:
                continue
            gender = str(gender)
            if gender not in ['male', 'female']:
                continue
            age = AgeRange.parse(statistic.age_raw)
            if not age:
                continue
            age = str(age)

            description = Description(statistic.description_raw)
            if not description.is_top_level:
                continue

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

    @staticmethod
    def get_position(i_rank):
        if i_rank == 0:
            return 'Top'
        if i_rank == 1:
            return '2nd'
        if i_rank == 2:
            return '3rd'
        return f'{i_rank + 1}th'

    def render_age_group(
        self,
        i_age_group: int,
        n_age_group: int,
        age_group: str,
        idx_d: dict,
        row_code_to_display_age_group: dict,
    ):
        p_age_group = (i_age_group + 2) / (n_age_group + 2)

        x, y = RenderStatistics.transform(p_age_group, 0.83)
        x0, y0 = RenderStatistics.transform(
            p_age_group - (1 / (n_age_group + 2)), 0.83
        )
        dy = RenderStatistics.font_size(4.5)
        inner = [
            _(
                'text',
                age_group,
                dict(
                    x=x,
                    y=y,
                    text_anchor='middle',
                    dominant_baseline='middle',
                    font_size=RenderStatistics.font_size(1.5),
                    font_family=BASE_FONT_FAMILY,
                    fill='#444',
                ),
            )
        ]
        displayed_deaths = 0
        for i_rank in range(N_DISPLAY):
            if i_age_group == 0:
                inner.append(
                    _(
                        'text',
                        self.get_position(i_rank),
                        dict(
                            x=x0,
                            y=y + dy * (1 + i_rank),
                            text_anchor='middle',
                            dominant_baseline='middle',
                            font_size=RenderStatistics.font_size(1.5),
                            font_family=BASE_FONT_FAMILY,
                            fill='#444',
                        ),
                    ),
                )

            row_code, deaths = list(idx_d.items())[i_rank]
            displayed_deaths += deaths
            r = math.sqrt(deaths) * 0.5
            color = ROW_CODE_TO_COLOR.get(row_code, '#cccccc')

            inner.append(
                _(
                    'circle',
                    None,
                    dict(
                        cx=x,
                        cy=y + dy * (1 + i_rank),
                        r=r,
                        stroke=color,
                        fill=color,
                        fill_opacity=0.7,
                    ),
                ),
            )

            if row_code_to_display_age_group[row_code] == age_group:
                short = ROW_CODE_TO_SIMPLE.get(row_code, row_code)
                inner.append(
                    _(
                        'text',
                        short,
                        dict(
                            x=x,
                            y=y + dy * (1 + i_rank),
                            text_anchor='middle',
                            dominant_baseline='middle',
                            font_size=RenderStatistics.font_size(1.5),
                            font_family=BASE_FONT_FAMILY,
                            fill='black',
                        ),
                    ),
                )
        remaining_deaths = sum(idx_d.values()) - displayed_deaths
        r = math.sqrt(remaining_deaths) * 0.7
        inner.append(
            _(
                'circle',
                None,
                dict(
                    cx=x,
                    cy=y + dy * (1 + N_DISPLAY),
                    r=r,
                    stroke='#888',
                    fill='#fff',
                ),
            ),
        )

        if i_age_group == 0:
            inner.append(
                _(
                    'text',
                    'All Others',
                    dict(
                        x=x0,
                        y=y + dy * (1 + N_DISPLAY),
                        text_anchor='middle',
                        dominant_baseline='middle',
                        font_size=RenderStatistics.font_size(1),
                        font_family=BASE_FONT_FAMILY,
                        fill='#888',
                    ),
                ),
            )

        return _('g', inner)

    def render_body(self):
        idx_ads = self.get_idx_ad_sorted()
        row_code_to_display_age_group = (
            self.get_row_code_to_display_age_group()
        )
        n_age_groups = len(idx_ads.keys())
        inner = []
        for i_age_group, age_group in enumerate(idx_ads.keys()):
            inner.append(
                self.render_age_group(
                    i_age_group,
                    n_age_groups,
                    age_group,
                    idx_ads[age_group],
                    row_code_to_display_age_group,
                )
            )

        return _(
            'g',
            inner,
        )

    def render_header(self):
        x, y = self.transform(0.5, 0.9)
        x0, y0 = self.transform(0.97, 0.9)
        return _(
            'g',
            [
                _(
                    'text',
                    f'Top {N_DISPLAY} Causes of Death by Age-Group (Sri Lanka)',
                    dict(
                        x=x,
                        y=y,
                        text_anchor='middle',
                        dominant_baseline='middle',
                        font_size=self.font_size(4),
                        font_family=BASE_FONT_FAMILY,
                        fill='black',
                    ),
                ),
                _(
                    'text',
                    f'{self.year}',
                    dict(
                        x=x0,
                        y=y + self.font_size(1),
                        text_anchor='end',
                        dominant_baseline='middle',
                        font_size=self.font_size(7),
                        font_family=BASE_FONT_FAMILY,
                        fill='#888',
                    ),
                ),
            ],
        )

    def render_footer(self):
        x, y = self.transform(0.5, 0.05)
        return _(
            'g',
            [
                _(
                    'text',
                    f'Data by The Department of Census and Statistics, Sri Lanka | Visualization by @nuuuwan',
                    dict(
                        x=x,
                        y=y,
                        text_anchor='middle',
                        dominant_baseline='middle',
                        font_size=self.font_size(1),
                        font_family=BASE_FONT_FAMILY,
                        fill='#888',
                    ),
                ),
            ],
        )

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
