from dataclasses import dataclass


@dataclass
class MortalityStatistic:
    death_description: str
    death_code_min: str
    death_code_max: str
    year: int
    gender: str
    age_min: int
    age_max: int
    deaths: int
