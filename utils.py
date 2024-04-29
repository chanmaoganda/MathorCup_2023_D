from math import ceil, log2
from typing import Callable, Generator, List

def get_generator(source_array) -> Generator:
    return primary_generator_factory(source_array, lambda x: x, lambda x: True)

def get_condition_generator(source_array: List, condition: Callable) -> Generator:
    return primary_generator_factory(source_array, lambda x: x, condition)

def get_mapped_generator(source_array: List, map_method: Callable) -> Generator:
    return primary_generator_factory(source_array, map_method, lambda x: True)

def primary_generator_factory(source_array: List, map_method: Callable, condition: Callable) -> Generator:
    mapped_array = list(map(map_method, source_array))
    return (mapped_array[index] for index in range(len(mapped_array)) if condition(index))

def int2binary(number: int):
    return ceil(log2(number + 1))