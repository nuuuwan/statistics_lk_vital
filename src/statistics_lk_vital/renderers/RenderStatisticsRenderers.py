import math

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from utils import Log, xmlx

from statistics_lk_vital.core.Description import (ROW_CODE_TO_COLOR,
                                                  ROW_CODE_TO_SIMPLE)
from statistics_lk_vital.renderers.svg_utils import (
    BASE_FONT_FAMILY, BASE_FONT_FAMILY_MONOSPACE, DX, DY, HEIGHT, N_DISPLAY,
    PADDING, WIDTH, font_size, get_position, pad, tx)

_ = xmlx._


log = Log('RenderStatistics')


class RenderStatisticsRenderers:
    def render_col_header(self, x, y, age_group):
        return _(
            'text',
            age_group,
            dict(
                x=x,
                y=y,
                text_anchor='middle',
                dominant_baseline='middle',
                font_size=font_size(1.5),
                font_family=BASE_FONT_FAMILY,
                fill='#444',
            ),
        )

    def render_row_header(self, x, y, i_rank):
        return _(
            'text',
            get_position(i_rank),
            dict(
                x=x,
                y=y,
                text_anchor='middle',
                dominant_baseline='middle',
                font_size=font_size(1.5),
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
            ),
        )

    def render_deaths_circle(self, x, y, deaths, color):
        r = math.sqrt(deaths) * 0.5
        return _(
            'circle',
            None,
            dict(
                cx=x,
                cy=y,
                r=r,
                stroke=color,
                stroke_width=5,
                fill=color,
                fill_opacity=1,
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
                font_size=font_size(1.5),
                font_family=BASE_FONT_FAMILY,
                fill='black',
            ),
        )

    def render_age_group_description(
        # parent
        self,
        i_age_group: int,
        n_age_group: int,
        age_group: str,
        idx_d: dict,
        row_code_to_display_age_group: dict,
        # child
        x_col: int,
        y_row: int,
        i_rank: int,
    ):
        inner = []

        if i_age_group == 0 or i_age_group == n_age_group - 1:
            x_col_header = x_col - DX if i_age_group == 0 else x_col + DX
            inner.append(self.render_row_header(x_col_header, y_row, i_rank))

        row_code, deaths = list(idx_d.items())[i_rank]
        color = ROW_CODE_TO_COLOR.get(row_code, '#cccccc')

        prev_location = self.prev_location.get(row_code, None)
        location = (x_col, y_row)
        self.prev_location[row_code] = location

        if prev_location is not None:
            inner.append(
                self.render_connection(prev_location, location, color)
            )

        inner.append(self.render_deaths_circle(x_col, y_row, deaths, color))

        if row_code_to_display_age_group[row_code] == age_group:
            short = ROW_CODE_TO_SIMPLE.get(row_code, row_code)
            inner.append(self.render_description_label(x_col, y_row, short))

        return _('g', inner)

    def render_all_other(self, x_col, y_row, i_age_group, remaining_deaths):
        inner = []
        y_row_all_other = y_row + DY
        if i_age_group == 0:
            x_row_header = x_col - DX
            inner.append(
                self.render_row_header(
                    x_row_header,
                    y_row_all_other,
                    N_DISPLAY,
                )
            )
        inner.append(
            self.render_deaths_circle(
                x_col,
                y_row_all_other,
                remaining_deaths,
                '#ccc',
            )
        )
        return _('g', inner)

    def render_age_group(
        self,
        i_age_group: int,
        n_age_group: int,
        age_group: str,
        idx_d: dict,
        row_code_to_display_age_group: dict,
    ):
        x_col, y_col_header = pad(DX * (i_age_group + 2)), pad(DY * 3)

        inner = [self.render_col_header(x_col, y_col_header, age_group)]
        displayed_deaths = 0
        for i_rank in range(N_DISPLAY):
            y_row = y_col_header + DY * (1 + i_rank)
            __, deaths = list(idx_d.items())[i_rank]
            displayed_deaths += deaths
            inner.append(
                self.render_age_group_description(
                    i_age_group,
                    n_age_group,
                    age_group,
                    idx_d,
                    row_code_to_display_age_group,
                    x_col,
                    y_row,
                    i_rank,
                )
            )

        # remaining deaths
        remaining_deaths = sum(idx_d.values()) - displayed_deaths
        inner.append(
            self.render_all_other(x_col, y_row, i_age_group, remaining_deaths)
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
        x_header = pad(tx(0.5))
        x_header_year = pad(tx(0.95))
        y_header = DY * 2
        return _(
            'g',
            [
                _(
                    'text',
                    f'Top {N_DISPLAY} Causes of Death in {self.gender.title()}s'
                    + ' by Age-Group (Sri Lanka)',
                    dict(
                        x=x_header,
                        y=y_header,
                        text_anchor='middle',
                        font_size=font_size(3),
                        font_family=BASE_FONT_FAMILY,
                        fill='black',
                    ),
                ),
                _(
                    'text',
                    f'{self.year}',
                    dict(
                        x=x_header_year,
                        y=y_header + font_size(1),
                        text_anchor='end',
                        font_size=font_size(7),
                        font_family=BASE_FONT_FAMILY_MONOSPACE,
                        fill='#f00',
                    ),
                ),
            ],
        )

    def render_footer(self):
        x_footer = pad(tx(0.5))
        y_footer = HEIGHT - PADDING - DY
        return _(
            'g',
            [
                _(
                    'text',
                    ' · '.join(
                        [
                            'Data by The Department of'
                            + ' Census and Statistics, Sri Lanka',
                            'Visualization by @nuuuwan',
                        ]
                    ),
                    dict(
                        x=x_footer,
                        y=y_footer,
                        text_anchor='middle',
                        dominant_baseline='middle',
                        font_size=font_size(2),
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
