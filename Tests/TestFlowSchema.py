from pydantic import ValidationError
from JsonSchemas.FlowSchema import Discrete, Continuous

#Turn this into a pytest

# Usage
try:
    continuous = Continuous(val=7.65, ranges=[
        Discrete(upper=1, name='lowest'),
        Discrete(lower=1, upper=5, name='low'),
        Discrete(lower=5, upper=7.5, name='nominal'),
        Discrete(lower=7.5, name='high')
    ])

except ValidationError as e:
    print(e)

    # Try Access Private Variable
try:
    continuous.val= 8.55
    continuous.ranges = [
        Discrete(upper=2., name='new_lowest'),
        Discrete(lower=2.0, upper=6, name='new_low'),
        # ... other ranges
    ]
except ValidationError as e:
    print(e)

for range in continuous.ranges:
    print(range.name, range.lower, range.upper)