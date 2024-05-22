use std::fs;
use scan_dir::ScanDir;

use crate::object::Object;

pub struct Handler {
    data_dir: String,
}

impl Handler {
    pub fn new() -> Self {
        let data_dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../data");
        Handler{data_dir: data_dir.to_string()}
    }

    pub fn parse_one_iteration(&self, iteration_path: &str) -> Object {
        let mut best_object = Object::default();
        let mut min_value = f32::MAX;
        let _ = ScanDir::files().read(iteration_path, |iterable|{
            for (entry, _) in iterable {
                let object = Object::from_file(&entry.path().display().to_string());
                if min_value > object.obj_val {
                    min_value = object.obj_val;
                    best_object = object.clone();
                }
            }
        });
        best_object
    }

    fn parse_one_instance(&self, instance_path: &str) -> Object {
        let mut best_object = Object::default();
        let mut min_value = f32::MAX;
        let _ = ScanDir::dirs().read(instance_path, |iterable| {
            for (entry, _) in iterable {
                let iteration_path = entry.path().display().to_string();
                let object = self.parse_one_iteration(&iteration_path);
                if min_value > object.obj_val {
                    min_value = object.obj_val;
                    best_object = object.clone();
                }
            }
        });
        best_object
    }
    
    pub fn parse_all_instances(&self) {
        let _ = ScanDir::dirs().read(&self.data_dir, |iterable|{
            for (entry, _) in iterable {
                let instance_path = entry.path().display().to_string();
                let instance_best_object = self.parse_one_instance(&instance_path);
                println!("{}", instance_best_object.to_readable_string());
            }
        });
    }

}