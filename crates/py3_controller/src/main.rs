use pyo3::prelude::*;
use pyo3::py_run;


fn main() -> PyResult<()> {
    Python::with_gil(|py| {
        let builtins = PyModule::import_bound(py, "annealers")?;
        let total: i32 = builtins
            .getattr("sum")?
            .call1((vec![1, 2, 3],))?
            .extract()?;
        assert_eq!(total, 6);
        Ok(())
    })
}