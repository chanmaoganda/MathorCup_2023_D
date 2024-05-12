use std::{collections::BTreeMap, fs};

use serde::{Serialize, Deserialize};

#[derive(Debug,Serialize, Deserialize)]
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
    pub fn new(file_path: &str) -> Self {
        let str = fs::read_to_string(file_path).expect("Couldn't find or load that file.");
        let object : Self = serde_json::from_str(&str).unwrap();
        object
    }
}