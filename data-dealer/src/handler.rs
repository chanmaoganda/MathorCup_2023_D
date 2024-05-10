use crate::object::Object;

pub struct Handler {
    expected_excavator_nums: Vec<f32>,
}

impl Handler {
    pub fn new(expected_excavator_nums: Vec<f32>) -> Self {
        Handler{expected_excavator_nums}
    }

    pub fn compare_to_expected(&self, object: &Object) -> bool {
        let excavator_nums: Vec<&f32> = object.excavator_values.values().collect();
        for (&reality, expected) in excavator_nums.iter().zip(self.expected_excavator_nums.iter()) {
            if reality != expected {
                return false;
            }
        }
        true
    }
}