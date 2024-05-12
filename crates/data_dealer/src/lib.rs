mod handler;
mod object;

pub use handler::Handler;
#[cfg(test)]
mod test {

    use crate::handler::Handler;

    #[test]
    fn test_handler() {
        let handler = Handler::new(vec![7.0, 7.0, 2.0], vec![7.0, 7.0, 2.0]);
        handler.parse_all_iterations();
    }
}