use data_dealer::Handler;

fn main() {
    let handler = Handler::new(vec![7.0, 7.0, 2.0], vec![7.0, 7.0, 2.0]);
    handler.parse_all_iterations();
}