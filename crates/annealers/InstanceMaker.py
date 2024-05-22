from typing import List

from DataStorage import DataStorage


class InstanceMaker:
    def __init__(self) -> None:
        self.data = DataStorage(total_budget = 2400, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                                excavator_oil_consumption = [28,30,34,38], truck_oil_consumption = [18, 22, 27],
                                excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                                excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                                excavator_precurement_cost = [100, 140, 300, 320], 
                                excavators_trucks_match_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]},
                                total_truck_numbers = [7, 7, 3])
    def make_all_instances(self) -> List[List[int]]:
        match_dict = self.data.excavators_trucks_match_dict

        matches = self.__find_matches(0, [key for key in match_dict.keys()])
        for match in matches:
            match.reverse()

        return matches

    
    def __find_matches(self, epoch: int, current_sequence: List[int]) -> List[List[int]]:
        truck_kinds = self.data.truck_kinds
        match_dict = self.data.excavators_trucks_match_dict
        
        if epoch == truck_kinds - 1:
            return [[excavator_index] for excavator_index in current_sequence if match_dict[excavator_index][epoch] != 0]
        result = []
        for index in range(len(current_sequence)):
            excavator = current_sequence.pop(0)
            if match_dict[excavator][epoch] == 0:
                current_sequence.append(excavator)
                continue
            matches = self.__find_matches(epoch + 1, current_sequence)

            for match in matches:
                match.append(excavator)
            current_sequence.append(excavator)
            result.extend(matches)
        return result