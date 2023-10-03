from functools import cached_property

ROW_CODE_TO_SIMPLE = {
    "1-001": "Infectious",
    "1-026": "Cancers",
    "1-048": "Blood",
    "1-051": "Metabolic",
    "1-055": "Mental",
    "1-058": "Nervous",
    "1-062": "Eye",
    "1-063": "Ear",
    "1-064": "Heart",
    "1-072": "Respiratory",
    "1-078": "Digestive",
    "1-082": "Skin",
    "1-083": "Bone",
    "1-084": "Genito-urinary",
    "1-087": "Pregnancy",
    "1-092": "Newborn",
    "1-093": "Birth Defects",
    "1-094": "Unspecified",
    "1-095": "Accidents / Injuries",
    "1-106": "Disappearance",
}

ROW_CODE_TO_COLOR = {
    "1-001": "#080",
    "1-026": "#08f",
    #     "1-048": "Blood / Immune",
    "1-051": "#f08",
    #     "1-055": "Mental",
    "1-058": "#f80",
    #     "1-062": "Eye",
    #     "1-063": "Ear",
    "1-064": "#f00",
    "1-072": "#888",
    "1-078": "#8f0",
    #     "1-082": "Skin",
    #     "1-083": "Bone",
    "1-084": "#fc0",
    #     "1-087": "Pregnancy / Childbirth",
    "1-092": "#008",
    "1-093": "#00f",
    "1-094": "#ccc",
    "1-095": "#000",
    #     "1-106": "Disappearance",
}


class Description:
    def __init__(self, description_raw: str):
        self.description_raw = description_raw

    @cached_property
    def row_code(self):
        return self.description_raw.strip()[:5]

    @cached_property
    def details(self):
        return self.description_raw.strip()[5:].strip()

    @cached_property
    def simple(self):
        return ROW_CODE_TO_SIMPLE.get(self.row_code, self.description_raw)

    @cached_property
    def is_top_level(self):
        return self.row_code in ROW_CODE_TO_SIMPLE.keys()

    @cached_property
    def color(self):
        return ROW_CODE_TO_COLOR.get(self.row_code, '#cccccc')
