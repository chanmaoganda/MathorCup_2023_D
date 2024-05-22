mod handler;
mod object;

pub use handler::Handler;
pub use object::Object;

#[cfg(test)]
mod test {

    use scan_dir::ScanDir;

    use crate::*;

    #[test]
    fn test_handler() {
        
    }
}