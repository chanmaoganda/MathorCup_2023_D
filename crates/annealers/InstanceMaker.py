class InstanceMaker:
    def __init__(self) -> None:
        self.data = 
    
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