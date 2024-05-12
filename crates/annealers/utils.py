from math import ceil, log2
from typing import Callable, Generator, List, Set

def primary_generator_factory(source_array: List, map_method: Callable, index_condition: Callable) -> Generator:
    mapped_array = list(map(map_method, source_array))
    return (mapped_array[index] for index in range(len(mapped_array)) if index_condition(index))

def make_condition_generator(source_array: List, index_condition: Callable) -> Generator:
    return primary_generator_factory(source_array, lambda value : value, index_condition)

def make_mapped_generator(source_array: List, map_method: Callable) -> Generator:
    return primary_generator_factory(source_array, map_method, lambda _ : True)

def make_generator(source_array) -> Generator:
    return primary_generator_factory(source_array, lambda value : value, lambda _ : True)

def int2binary(number: int):
    return ceil(log2(number + 1))

def dict_type_checker(dictionary: dict, key_type, value_type) -> bool:
    key_type_check = all(isinstance(key, key_type) for key in dictionary.keys())
    value_type_check = all(isinstance(value, value_type) for value in dictionary.values())
    return key_type_check and value_type_check

def dict_key_checker(dictionary: dict, key_type) -> bool:
    return all(isinstance(key, key_type) for key in dictionary.keys())