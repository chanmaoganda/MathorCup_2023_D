# This repository contains the code for the MathorCup D-2023.
- This problem is asking to find the best combination of trucks and excavators to make the most profit. 
- This repo aims to make the problem more simple and easy via tearing this problem into smaller sub-problems.
### SubProblems
- make a list of all possible combinations of trucks and excavators.
- calculate the profit for each combination of trucks and excavators.
- find the combination with the highest profit.
### Code Structure
- Since quantum computing sdk only offers Python version(py3.8), the main code will be written in Python.
- Each group of one iteration contains 100 possible combinations, we select the `top 50` solutions and write them to a directory(`each solution in a single json file`)
- To find the best solution in so many combinations, we choose to use rust to find the best solution in each iteration.
- The rust code will read the json files and find the best solution for each iteration in the order of obj_val(which is the object value of the target function).
- Finally, we will combine the solutions from each iteration to find the best solution for the entire problem.

## How to run the code
- Clone the repository
- just run the file `python3 ./crates/annealers/run.py`
- Then the code will run and generate the solutions in the `data` directory as the `data_example` shows
- To find the best solution, run the `rust` code: `cargo run --bin runner`
- Cargo will fetch libraries and compile the code, then run to get the best solution.