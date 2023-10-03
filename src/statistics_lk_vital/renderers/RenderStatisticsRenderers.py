import math

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from utils import Log, xmlx

from statistics_lk_vital.core.Description import (ROW_CODE_TO_COLOR,
                                                  ROW_CODE_TO_SIMPLE)

_ = xmlx._


log = Log('RenderStatistics')
WIDTH, HEIGHT = 1600, 900
PADDING = 25
BASE_FONT_SIZE = 12
BASE_FONT_FAMILY = 'TCM_____'
N_DISPLAY = 10
N_AGE_GROUPS = 18


class RenderStatisticsRenderers:
    @staticmethod
    def tx(px: float):
        assert 0 <= px <= 1
        return px * (WIDTH - PADDING * 2)

    @staticmethod
    def ty(py: float):
        assert 0 <= py <= 1
        return py * (HEIGHT - PADDING * 2)

    @staticmethod
    def t(px: float, py: float):
        return (
            RenderStatisticsRenderers.pad(RenderStatisticsRenderers.tx(px)),
            RenderStatisticsRenderers.pad(RenderStatisticsRenderers.ty(py)),
        )

    @staticmethod
    def pad(z: float):
        return int(z + PADDING)

    @staticmethod
    def font_size(p: float):
        return BASE_FONT_SIZE * p

    @staticmethod
    def get_position(i_rank):
        if i_rank == N_DISPLAY:
            return 'All Others'
        if i_rank == 0:
            return 'Top'
        if i_rank == 1:
            return '2nd'
        if i_rank == 2:
            return '3rd'
        return f'{i_rank + 1}th'

    def render_col_header(self, x, y, age_group):
        return _(
            'text',
            age_group,
            dict(
                x=x,
                y=y,
                text_anchor='middle',
                dominant_baseline='middle',
                font_size=self.font_size(1.5),
                font_family=BASE_FONT_FAMILY,
                fill='#444',
            ),
        )

    def render_row_header(self, x, y, i_rank):
        return _(
            'text',
            self.get_position(i_rank),
            dict(
                x=x,
                y=y,
                text_anchor='middle',
                dominant_baseline='middle',
                font_size=self.font_size(1.5),
                font_family=BASE_FONT_FAMILY,
                fill='#444',
            ),
        )

    def render_connection(self, prev_location, location, color):
        x1, y1 = prev_location
        x2, y2 = location
        return _(
            'line',
            None,
            dict(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                stroke=color,
                stroke_width=3,
                stroke_opacity=0.6,
                opacity=0.6,
                fill_opacity=0.6,
            ),
        )

    def render_deaths_circle(self, x, y, r, color):
        return _(
            'circle',
            None,
            dict(
                cx=x,
                cy=y,
                r=r,
                stroke=color,
                fill=color,
                fill_opacity=0.6,
            ),
        )

    def render_description_label(self, x, y, description):
        return _(
            'text',
            description,
            dict(
                x=x,
                y=y,
                text_anchor='middle',
                dominant_baseline='middle',
                font_size=self.font_size(1.5),
                font_family=BASE_FONT_FAMILY,
                fill='black',
            ),
        )

    def render_age_group(
        self,
        i_age_group: int,
        n_age_group: int,
        age_group: str,
        idx_d: dict,
        row_code_to_display_age_group: dict,
    ):
        dx = self.tx(1.0 / (N_AGE_GROUPS + 3))
        dy = self.ty(1.0 / (N_DISPLAY + 5))

        x_col, y_col_header = self.pad(dx * (i_age_group + 2)), self.pad(
            dy * 3
        )

        inner = [self.render_col_header(x_col, y_col_header, age_group)]
        displayed_deaths = 0
        for i_rank in range(N_DISPLAY):
            y_row = y_col_header + dy * (1 + i_rank)
            if i_age_group == 0 or i_age_group == n_age_group - 1:
                x_col_header = x_col - dx if i_age_group == 0 else x_col + dx
                inner.append(
                    self.render_row_header(x_col_header, y_row, i_rank)
                )

            row_code, deaths = list(idx_d.items())[i_rank]
            displayed_deaths += deaths
            r = math.sqrt(deaths) * 0.5
            color = ROW_CODE_TO_COLOR.get(row_code, '#cccccc')

            prev_location = self.prev_location.get(row_code, None)
            location = (x_col, y_row)
            self.prev_location[row_code] = location

            if prev_location is not None:
                inner.append(
                    self.render_connection(prev_location, location, color)
                )

            inner.append(self.render_deaths_circle(x_col, y_row, r, color))

            if row_code_to_display_age_group[row_code] == age_group:
                short = ROW_CODE_TO_SIMPLE.get(row_code, row_code)
                inner.append(
                    self.render_description_label(x_col, y_row, short)
                )
        remaining_deaths = sum(idx_d.values()) - displayed_deaths
        r = math.sqrt(remaining_deaths) * 0.7
        inner.append(
            self.render_deaths_circle(
                x_col,
                y_row,
                r,
                '#ccc',
            )
        )

        if i_age_group == 0:
            inner.append(
                self.render_row_header(
                    x_col,
                    y_row,
                    N_DISPLAY,
                )
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
        x, y = self.t(0.5, 0.1)
        x0, y0 = self.t(0.97, 0.1)
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
        x, y = self.t(0.5, 0.95)
        return _(
            'g',
            [
                _(
                    'text',
                    '|'.join(
                        [
                            'Data by The Department of'
                            + ' Census and Statistics, Sri Lanka ',
                            'Visualization by @nuuuwan',
                        ]
                    ),
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
