from pydantic import BaseModel
import random
import simpy

from Models.Functional import FunctionContainer, FSM_State

from JsonSchemas.FlowSchema import Discrete, Continuous


class InputASchema(BaseModel):
    field1: int
    field2: int

class OutputASchema(BaseModel):
    field1: int
    field2: int


def square(field1, field2):
    return {"field1": field1**2, "field2": field2**2}

# Initialize the function container, specifying 'env' to be ignored in schema validation
A = FunctionContainer(
    func=square,
    input_schema=InputASchema,
    output_schema=OutputASchema,
)
# Create FSM_States from A
A_State = FSM_State("A", A)


# Define simpy Process

def time_process(env):
    # Choose a random delay between 1 and 10 seconds
    delay = random.randint(1, 10)

    # Wait for the time delay
    yield env.timeout(delay)
    print(f'Process triggered after {delay} seconds.')

    # Return the current simulation time
    return env.now

# Initialize a SimPy Environment and trigger events
env = simpy.Environment()
init_process1 = env.process(time_process(env))
init_process2 = env.process(time_process(env))

# Assign relevant events to the FSM_State
A_State.set_trigger_events([init_process1, init_process2])
A_State.set_environment(env)

# Initialize the FSM_State
env.process(A_State.process())

# run simpy environment
env.run()


