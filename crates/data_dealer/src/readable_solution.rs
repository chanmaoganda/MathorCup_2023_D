use std::collections::BTreeMap;
use tabled::Tabled;
use crate::{FormattedString, Solution};

use color_print::cformat;

#[derive(Tabled)]
pub struct ReadableSolution {
    #[tabled(rename = "Total Revenue Value", order = 0)]
    pub total_revenue_val: f32,
    #[tabled(rename = "Total Cost", order = 1)]
    pub total_cost: f32,
    #[tabled(display_with("Self::format_excavator_values", self))]
    pub excavator_values: BTreeMap<String, f32>,
    #[tabled(display_with("Self::format_truck_values", self))]
    pub truck_values: BTreeMap<String, f32>,
    #[tabled(display_with("Self::format_half_used_excavators", self))]
    pub half_used_excavators: BTreeMap<String, f32>,

    #[tabled(skip)]
    parse_rule: Vec<String>,
}

impl ReadableSolution {
    pub fn from_solution(solution : Solution) -> Self {
        Self{ 
            total_cost: solution.total_cost,
            total_revenue_val: solution.total_revenue_val,
            excavator_values: solution.excavator_values,
            truck_values: solution.truck_values,
            half_used_excavators: solution.half_used_values,
            parse_rule: Vec::new()
        }
    }

    pub fn print_rule(&mut self, rule: &Vec<String>) {
        self.parse_rule = rule.clone();
    }

    fn format_btree_map(&self, map: &BTreeMap<String, f32>) -> String {
        let mut string = String::new();
        self.parse_rule.iter().for_each(|key| {
            let parsed_key = map.keys().find(|k| {k.contains(key)}).unwrap();
            string.push_str(&format!("{}: {:.1}, ", key, map.get(parsed_key).unwrap_or(&-1.0))
            );
        });
        string
    }

    fn format_excavator_values(&self) -> String {
        self.format_btree_map(&self.excavator_values)
    }

    fn format_truck_values(&self) -> String {
        self.truck_values.format()
    }

    fn format_half_used_excavators(&self) -> String {
        self.format_btree_map(&self.half_used_excavators)
    }
}

impl FormattedString for ReadableSolution {
    fn format(&self) -> String {
        let mut string = String::new();
        string.push_str(&format!("total_cost is <y>{}\n", self.total_cost));
        string.push_str(&format!("excavator_values is {}\n", self.excavator_values.format()));
        string.push_str(&format!("truck_value is {}\n", self.truck_values.format()));
        string.push_str(&format!("half_used_values is {}\n", self.half_used_excavators.format()));
        string.push_str(&format!("total_revenue_val is {}\n", self.total_revenue_val));
        string
    }

    fn format_with_color(&self) -> String {
        let mut string = String::new();
        string.push_str(&cformat!("<c>total_cost is </><y>{}</>\n", self.total_cost));
        string.push_str(&cformat!("<c>excavator_values is </>{}\n", self.excavator_values.format()));
        string.push_str(&cformat!("<c>truck_value is </>{}\n", self.truck_values.format()));
        string.push_str(&cformat!("<c>half_used_values is </>{}\n", self.half_used_excavators.format()));
        string.push_str(&cformat!("<c>total_revenue_val is </><y, bold>{}</>\n", self.total_revenue_val));
        string
    }
}




