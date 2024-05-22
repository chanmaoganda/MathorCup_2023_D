use std::{collections::BTreeMap, fs};

use serde::{Serialize, Deserialize};

#[derive(Debug,Serialize, Deserialize, Default, Clone)]
pub struct Object {
    pub total_cost: f32,
    pub cost_con_value: f32,
    pub truck_num_constraint_val : BTreeMap<String, f32>,
    pub excavator_values: BTreeMap<String, f32>,
    pub truck_values: BTreeMap<String, f32>,
    pub half_used_values: BTreeMap<String, f32>,
    pub total_revenue_val: f32,
    pub obj_val: f32,
    pub produce_cost: f32,
    pub oil_consume_cost: f32,
    pub maintenance_cost: f32,
    pub precurement_cost: f32,
    pub excavator_produce_dict: BTreeMap<String, f32>
}

impl Object {
    pub fn from_file(file_path: &str) -> Self{
        let str = fs::read_to_string(file_path).expect("Couldn't find or load that file.");
        let object : Self = serde_json::from_str(&str).unwrap();
        object
    }

    pub fn to_readable_string(&self) -> String {
        let mut string = String::new();
        string.push_str(&format!("total_cost is {}\n", self.total_cost));
        string.push_str(&format!("excavator_values is {:?}\n", self.excavator_values));
        string.push_str(&format!("truck_value is {:?}\n", self.truck_values));
        string.push_str(&format!("half_used_values is {:?}\n", self.half_used_values));
        string.push_str(&format!("total_revenue_val is {}\n", self.total_revenue_val));
        string
    }
}
