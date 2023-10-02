from functools import cached_property

ROW_CODE_TO_SIMPLE = {
    "1-001": "Infectious",
    "1-026": "Cancers",
    "1-048": "Blood / Immune",
    "1-051": "Metabolic / Nutritional",
    "1-055": "Mental",
    "1-058": "Nervous",
    "1-062": "Eye",
    "1-063": "Ear",
    "1-064": "Heart",
    "1-072": "Respiratory",
    "1-078": "Digestive",
    "1-082": "Skin",
    "1-083": "Bone",
    "1-084": "Genitourinary",
    "1-087": "Pregnancy / Childbirth",
    "1-092": "Newborn",
    "1-093": "Birth Defects",
    "1-094": "Unspecified",
    "1-095": "Accidents / Injuries",
    "1-106": "Disappearance",
}
SIMPLE_TO_COLOR = {}


class Description:
    def __init__(self, description_raw: str):
        self.description_raw = description_raw

    @cached_property
    def tokens(self) -> list[str]:
        return self.description_raw.split(' ')

    @cached_property
    def row_code(self):
        return self.tokens[0]

    @cached_property
    def simple(self):
        return ROW_CODE_TO_SIMPLE.get(self.row_code, self.description_raw)
