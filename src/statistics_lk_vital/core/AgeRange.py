class AgeRange:
    def __init__(self, age_min: int, age_max: int):
        self.age_min = age_min
        self.age_max = age_max

    def __str__(self):
        return f'{self.age_min}-{self.age_max}'

    @staticmethod
    def parse(x: str):
        x = x.lower().replace(' ', '')

        for phrase, age_range in [
            ('85+', AgeRange(85, 120)),
            ('total1-4years', AgeRange(1, 4)),
            ('total0-29days', AgeRange(0, 1)),
            ('total1-11months', AgeRange(0, 1)),
        ]:
            if phrase in x:
                return age_range

        if '-' not in x or 'total' in x:
            return None

        age_min, age_max = x.split('-')
        age_min = int(age_min)
        age_max = int(age_max)

        if age_min % 5 != 0 or age_max - age_min != 4:
            return None
        return AgeRange(age_min, age_max)
