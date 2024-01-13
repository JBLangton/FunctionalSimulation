from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from operator import attrgetter

class Discrete(BaseModel):
    lower: Optional[float] = float('-inf')
    upper: Optional[float] = float('inf')
    name: str

    @model_validator(mode='after')
    def check_boundaries(cls, self):
        lower, upper = self.lower, self.upper
        if lower is not None and upper is not None and lower >= upper:
            raise ValueError(f"Upper bound must be greater than lower bound, got lower={lower} and upper={upper}")
        return self

    class Config:
        validate_assignment = True

class Continuous(BaseModel):
    val: float
    ranges: List[Discrete] = []

    class Config:
        validate_assignment = True

    @field_validator('ranges')
    @classmethod
    def check_ranges(cls, v: str):

        # sort values by lower bound
        ranges = sorted(v, key=attrgetter('lower'))

        # Initialize with the opposite extremes to compare with the first range
        prev_upper = float('-inf')
        for range in ranges:

            # Check for overlaps
            if range.lower is not None and range.lower < prev_upper:
                raise ValueError(f"Overlapping range detected at {range.lower} between {prev.name} and {range.name}.")


            # Check for gaps
            if range.lower is not None and range.lower > prev_upper:
                if prev_upper != float('-inf'):  # Ignore the very first lower bound
                    raise ValueError(f"Gap detected between {prev_upper} and {range.lower} between {prev.name} and {range.name}.")

            # Prepare for next iteration
            prev = range
            prev_upper = range.upper if range.upper is not None else float('inf')

        return v