from pydantic import BaseModel
from typing import Callable, Type
import simpy

class FunctionContainer:
    def __init__(self, func: Callable, input_schema: Type[BaseModel], output_schema: Type[BaseModel]):
        self.func = func
        self.input_schema = input_schema
        self.output_schema = output_schema

    def call(self, input_json):
        print(input_json)

        # Check if an input_schema is provided
        if self.input_schema:
            # Validate input
            input_data = self.input_schema(**input_json)
            validated_input = input_data.model_dump()
        else:
            # If no input_schema, pass the input_json directly
            validated_input = input_json

        # Call the function with either validated input or the original input_json
        raw_output = self.func(**validated_input)

        # Validate output
        output_data = self.output_schema(**raw_output)

        return output_data



class FSM_State:
    def __init__(self, name, core_function):

        # assert name is a string, core_function is a FunctionContainer
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if not isinstance(core_function, FunctionContainer):
            raise ValueError("core_function must be an instance of FunctionContainer")


        self.name = name
        self.core_function = core_function
        self.env = None  # Environment will be set later
        self.trigger_events = []  # Initialize as empty list
        self.on_entry_events = []  # Initialize as empty list
        self.on_exit_events = []  # Initialize as empty list

    def set_environment(self, env):
        if not isinstance(env, simpy.Environment):
            raise ValueError("env must be an instance of simpy.Environment")
        self.env = env

    def set_trigger_events(self, events):
        if not all(isinstance(event, simpy.Event) for event in events):
            raise ValueError("All guard_events must be simpy.Event instances")
        self.trigger_events = events

    def set_on_entry_events(self, events):
        if not all(isinstance(event, simpy.Event) for event in events):
            raise ValueError("All on_entry_events must be simpy.Event instances")
        self.on_entry_events = events

    def set_on_exit_events(self, events):
        if not all(isinstance(event, simpy.Event) for event in events):
            raise ValueError("All on_exit_events must be simpy.Event instances")
        self.on_exit_events = events

    def process(self):
        # Wait for on guard events
        yield self.env.all_of(self.trigger_events)
        print(f'{self.name} state entered.')

        # Trigger on entry event
        for on_entry_event in self.on_entry_events:
            on_entry_event.succeed()

        # Collect values from guard events
        event_values = [event.value for event in self.trigger_events]

        # Prepare input for function call based on expected schema
        input_dict = {f'field{i + 1}': val for i, val in enumerate(event_values)}

        # Validate and call the function with dynamic inputs
        try:
            result = self.core_function.call(input_dict)
            print(f'Core function executed in {self.name} state with result: {result}')
        except Exception as e:
            print(f'Error executing core function: {e}')


        # Trigger on exit event
        for on_exit_event in self.on_exit_events:
          on_exit_event.succeed()
        print(f'{self.name} state exited.')