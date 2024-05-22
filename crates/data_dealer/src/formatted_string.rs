use std::collections::BTreeMap;

use color_print::cformat;

pub trait FormattedString {
    fn format(&self) -> String;
}


impl FormattedString for BTreeMap<String, f32> {
    fn format(&self) -> String {
        let mut formatted_output_string = String::new();
        self.iter().for_each(|(key, value)| {
            formatted_output_string.push_str(&cformat!("<m>{}</>: <y>{:.1}</>,", key, value));
        });
        formatted_output_string
    }
}