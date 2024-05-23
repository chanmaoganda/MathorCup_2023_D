use std::collections::BTreeMap;

use color_print::cformat;

pub trait FormattedString {
    fn format(&self) -> String;

    fn format_with_color(&self) -> String;
}


impl<K, V> FormattedString for BTreeMap<K, V>
    where K : std::fmt::Display, V : std::fmt::Display {
    fn format(&self) -> String {
        let mut formatted_output_string = String::new();
        self.iter().for_each(|(key, value)| {
            formatted_output_string.push_str(&format!("{}: {:.1},", key, value));
        });
        formatted_output_string
    }

    fn format_with_color(&self) -> String {
        let mut formatted_output_string = String::new();
        self.iter().for_each(|(key, value)| {
            formatted_output_string.push_str(&cformat!("<m>{}</>: <y>{:.1}</>,", key, value));
        });
        formatted_output_string
    }
}