mod handler;
mod object;
mod formatted_string;

pub use handler::Handler;
pub use object::Object;
pub use formatted_string::FormattedString;

#[cfg(test)]
mod test {

    use scan_dir::ScanDir;

    use crate::*;

    #[test]
    fn test_handler() {
        
    }
}