use data_dealer::Handler;

fn main() {
    let handler = Handler::new();
    handler.parse_all_instances();
}
