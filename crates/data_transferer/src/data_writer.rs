use std::collections::HashMap;

use data_dealer::Solution;
use mysql::{prelude::*, *};

pub struct DataWriter {
    file_path: String,
}

impl DataWriter {
    pub fn foo(&self, table_name: &str) -> Result<(), Box<dyn std::error::Error>> {
        let url = "mysql://avania:331469@localhost:3307/db_name";
        let pool = Pool::new(url)?;

        let mut conn = pool.get_conn()?;
        let query = format!("SELECT name FROM {};", table_name);
        let results = conn.query_map(query, |name: String|{
            Solution::from_file(&name)
        })?;
        
        Ok(())
    }
}