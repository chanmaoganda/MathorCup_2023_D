use data_dealer::Handler;

fn main() {
    let total_iterations = 100;
    let handler = Handler::new(vec![7.0, 7.0, 2.0], vec![7.0, 7.0, 2.0]);
    handler.parse_all_iterations(total_iterations);
}