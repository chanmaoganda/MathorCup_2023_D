use scan_dir::ScanDir;
use crate::{solution::Solution, ReadableSolution};
use tabled::tables::ExtendedTable;

pub struct Handler {
    data_dir: String,
}

impl Handler {
    pub fn new() -> Self {
        let data_dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../data");
        Handler{data_dir: data_dir.to_string()}
    }

    pub fn parse_one_iteration(&self, iteration_path: &str) -> Solution {
        let mut solutions : Vec<Solution> = Vec::new();
        let _ = ScanDir::files().read(iteration_path, |iterable|{
            for (entry, _) in iterable {
                let file = entry.path().display().to_string();
                solutions.push(Solution::from_file(&file));
            }
        });
        solutions.into_iter().max_by(|lhs, rhs| {
            rhs.obj_val.total_cmp(&lhs.obj_val)
        }).unwrap()
    }

    fn parse_one_instance(&self, instance_path: &str) -> Solution {
        let mut solutions : Vec<Solution> = Vec::new();
        let _ = ScanDir::dirs().read(instance_path, |iterable| {
            for (entry, _) in iterable {
                let iteration_path = entry.path().display().to_string();
                let solution = self.parse_one_iteration(&iteration_path);
                solutions.push(solution);
            }
        });
        solutions.into_iter().max_by(|lhs, rhs| {
            rhs.obj_val.total_cmp(&lhs.obj_val)
        }).unwrap()
    }
    
    pub fn parse_all_instances(&self) {
        let mut solutions_of_instances = Vec::new();
        let _ = ScanDir::dirs().read(&self.data_dir, |iterable|{
            for (entry, path) in iterable {
                let instance_path = entry.path().display().to_string();
                let instance_best_solution = self.parse_one_instance(&instance_path);
                let rule = self.parse_rule(&path);
                let mut solution_with_rule = ReadableSolution::from_solution(instance_best_solution);
                solution_with_rule.print_rule(&rule);
                solutions_of_instances.push(solution_with_rule);
            }
            
            let table = ExtendedTable::new(solutions_of_instances).to_string();
            println!("{}", table);
        });
    }

    fn parse_rule(&self, name: &str) -> Vec<String> {
        return name.split('-').map(|str| {
            let mut base = String::from("excavator");
            base.push_str(str);
            base
        }).collect::<Vec<String>>();
    }

}