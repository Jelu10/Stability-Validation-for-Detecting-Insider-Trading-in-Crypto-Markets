# How to run the Aster case study experiments



Experiment execution and data retrieval are intentionally sepperated.
To gain the data to execute the experiments on, either download here at '[zenodo.com](https://zenodo.org/records/19699438?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjVhYzkxOTBlLTZiMjEtNGY4OC04MDVlLTk5MTJmZjk5NjI2MSIsImRhdGEiOnt9LCJyYW5kb20iOiI3OTMzY2Y4M2M5YjI0MjkyNWZjNTdkYTcxMTk2YWFhYyJ9.UuRfrKONUII3uOld3PaSl5zTfonz3yvCRUuPkQRNVOA4WBQww8xle0NCNnUSdyLjDDGcII_5CayBgLAU8AUhsw)' or retrieve it through querying dune.com with
the queries specified in the `queries` directory and the following command:

```powershell
$env:PYTHONPATH = "src"
python -m aster_experiments download
```


After retrieving the data place it into `data/`.


Run the experiments with the following command:

```powershell
$env:PYTHONPATH = "src"
python -m aster_experiments run-skip-download
```

You can customize the configuration or create your own and run this command:

```powershell
python -m aster_experiments --config path/to/config.json run-skip-download
```



## Project Responsibiliteis
- Processes DEX trading data into address level features
- Derrives features encoding
    - raw behavior
    - delta or change in behavior
    - time
    - network
- Runs Isolation Forest anomaly detection across multiple seeds
- Evaluates stability using Jaccard similarity and AUC metrics
- Compares temporal windows (pre, post, controls)

## Outputs
Running the experiments will output:
- Jaccard similarity between feature sets across runs
- Stability test results based on the aggregated AUC of the jaccard similarity
    - Testing significant difference between feature sets within a window
    - Testing significant difference of windows across top feature sets

## Requirements
- Developed with Python 3.14
- Install dependencies:
  pip install -r requirements.txt

## Configuration
The default config is `src/aster_experiments/defaults/aster_v2.json`. This is the experiment configuration from the paper.
- 40 stochastic runs
- predefined temporal windows
- feature subset comparisons

