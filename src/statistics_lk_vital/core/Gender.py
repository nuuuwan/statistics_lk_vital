class Gender:
    def __init__(self, gender):
        self.gender = gender

    def __str__(self):
        return {'t': 'total', 'm': 'male', 'f': 'female'}.get(
            self.gender, 'unknown'
        )

    @staticmethod
    def parse(x):
        candidate_gender = x.lower()[0]
        if candidate_gender not in ['t', 'm', 'f']:
            return None
        return Gender(candidate_gender)
