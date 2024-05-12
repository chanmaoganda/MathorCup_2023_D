use pyo3::prelude::*;

pub fn generate_data(total_iterations: i32)-> PyResult<()>{
    Python::with_gil(|py| {
        let py_app = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../annealers/run.py"));
        let builtins : Py<PyAny> = PyModule::from_code_bound(py, &py_app, "", "")?.getattr("solve_all_instances")?.into();
        builtins.call1(py, (total_iterations,))?;
        Ok(())
    })
}