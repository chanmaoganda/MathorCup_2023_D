use handler::Handler;
use object::Object;

mod object;
mod handler;

fn parser(iteration : i32) -> (bool, Vec<i32>) {
    let handler = Handler::new(vec![7.0, 7.0, 2.0]);
    let mut matched_nums = Vec::new();
    let mut result = true;
    for index in 0..100 {
        let object = Object::new(format!("../data/iteration-{iteration}/0-{}-solution.json", index).as_str());
        if handler.compare_to_expected(&object) {
            matched_nums.push(index);
        } else {
            result &= false;
        }
    }
    (result, matched_nums)
}

fn main() {
    let mut match_iteration_nums = Vec::new();
    for index in 1..=44 {
        let (_, matched_indexes) = parser(index);
        match_iteration_nums.push(matched_indexes.len());
        println!("itertaion {index} \t- matched numbers: {:?}", matched_indexes)
    }
    println!("total matched numbers: {:?}", match_iteration_nums);
    println!("averaged matched numbers: {:.1}", match_iteration_nums.iter().sum::<usize>() as f32 / match_iteration_nums.len() as f32);
}
