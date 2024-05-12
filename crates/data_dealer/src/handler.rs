use std::collections::BTreeMap;

use crate::object::Object;

pub struct Handler {
    expected_excavator_nums: Vec<f32>,
    expected_truck_nums: Vec<f32>,
}

impl Handler {
    pub fn new(expected_excavator_nums: Vec<f32>, expected_truck_nums: Vec<f32>) -> Self {
        Handler{expected_excavator_nums, expected_truck_nums}
    }

    fn compare_to_expected(&self, object: &Object) -> bool {
        for (reality, expected) in object.excavator_values.values().zip(self.expected_excavator_nums.iter()) {
            if reality != expected {
                return false;
            }
        }
        for (reality, expected) in object.truck_values.values().zip(self.expected_truck_nums.iter()) {
            if reality != expected {
                return false;
            }
        }
        for (reality, expected) in object.half_used_values.values().zip(vec![0.0, 0.0, 0.0].iter()) {
            if reality != expected {
                return false;
            }
        }
        true
    }

    pub fn parse_iteration(&self, iteration: i32) -> (bool, Vec<i32>) {
        let mut matched_nums = Vec::new();
        let mut result = true;
        let data_dir = "./build/all-data/data";

        for index in 0..100 {
            let object = Object::new(format!("{}/iteration-{iteration}/{}-solution.json", data_dir, index).as_str());
            if self.compare_to_expected(&object) {
                matched_nums.push(index);
            } else {
                result &= false;
            }
        }
        (result, matched_nums)
    }
    
    pub fn parse_all_iterations(&self) {
        let mut matched_iteration_lens = Vec::new();
        let mut matched_iteration_indexes = Vec::new();
        let total_iterations = 1000;
        for index in 1..=total_iterations {
            let (_, matched_indexes) = self.parse_iteration(index);
            if matched_indexes.len() == 0 {
                continue;
            }
            println!("matched iteration {} with matched numbers {:?} ", index, matched_indexes);
            matched_iteration_indexes.push(index);
            matched_iteration_lens.push(matched_indexes.len());
        }
        println!("matched numbers: {:?}", matched_iteration_indexes.iter().zip(matched_iteration_lens.iter()).collect::<BTreeMap<_, _>>());
        println!("total number is {}, averaged matched numbers: {:3}", 
            matched_iteration_lens.len(), 
            matched_iteration_lens.iter().sum::<usize>() as f32 / total_iterations as f32);
    }

}