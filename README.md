# Export and Import MLflow Experiments, Runs or Models

Tools to export and import MLflow runs, experiments or registered models from one tracking server to another.

There are two ways to run the tools:
* As a normal Python package - this page.
* [Databricks notebooks](databricks_notebooks/README.md) accessing the wheel library.

Note, there is also a secondary "[direct copy](README_copy.md)" feature with documented limitations.

## Architecture

<img src="export_import_architecture.png" height="330" >

## Overview

### Experiments
  * Export experiments to a directory.
  * Import experiments from a directory.

### Runs
  * Export a run to  a directory or zip file.
  * Import a run from a directory or zip file.

### Registered Models
  * Export a registered model to a directory.
  * Import a registered model from a directory.
  * List all registered models.


## Limitations

### General Limitations

* Nested runs are only supported when you import an experiment. For a run, it is still a TODO.

### Databricks Limitations

* The Databricks API does not support exporting or importing notebook revisions.
The [workspace/export](https://docs.databricks.com/dev-tools/api/latest/workspace.html#export) API endpoint only exports a notebook representing the latest revision.
* When you import a run, the link to its source notebook revision ID will appear in the UI but you cannot reach that revision (link is dead).
* For convenience, the export tool exports the latest notebook revision for a notebook-based experiment but again, it cannot be attached to a run when imported. Its stored as an artifact in the "notebooks" folder of the run's artifact root.

## Common options details 

`notebook-formats` - If exporting a Databricks experiment, the run's notebook (latest revision, not the revision associated with the run) can be saved in the specified formats (comma-delimited argument). Each format is saved in the notebooks folder of the run's artifact root directory as `notebook.{format}`. Supported formats are  SOURCE, HTML, JUPYTER and DBC. See Databricks [Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.

`use-src-user-id` -  Set the destination user ID to the source user ID. Source user ID is ignored when importing into Databricks since the user is automatically picked up from your Databricks access token.

`export-metadata-tags` - Creates metadata tags (starting with `mlflow_export_import.metadata`) that contain export information. These are the source `mlflow` tags in addition to other information. This is useful for provenance and auditing purposes in regulated industries.

```
Name                                  Value
mlflow_export_import.metadata.timestamp       1551037752
mlflow_export_import.metadata.timestamp_nice  2019-02-24 19:49:12
mlflow_export_import.metadata.experiment_id   2
mlflow_export_import.metadata.experiment-name sklearn_wine
mlflow_export_import.metadata.run-id          50fa90e751eb4b3f9ba9cef0efe8ea30
mlflow_export_import.metadata.tracking_uri    http://localhost:5000
```

## Setup

Supports python 3.7.6 or above.

### Local setup

First create a virtual environment.
```
python -m venv mlflow-export-import
source mlflow-export-import/bin/activate
```

There are two different ways to install the package.

#### Install from github directly

```
pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
```

#### Install from github clone
```
git clone https://github.com/amesar/mlflow-export-import
cd mlflow-export-import
pip install -e .
```

### Databricks setup

There are two different ways to install the package.

#### Install package in notebook

[Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).


```
pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
```

#### Install package as a wheel on cluster

Build the wheel artifact, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).

```
python setup.py bdist_wheel
databricks fs cp dist/mlflow_export_import-1.0.0-py3-none-any.whl {MY_DBFS_PATH}
```

## Experiments 

### Export Experiments

There are two main programs to export experiments:
* `export_experiment` - exports one experiment.
* `export_experiment_list` - exports a list of  experiments.

Both accept either an experiment ID or name.

#### export_experiment

Export one experiment to a directory.

##### Usage

```
python -u -m mlflow_export_import.experiment.export_experiment --help

Options:
  --experiment TEXT               Experiment name or ID.  [required]
  --output-dir TEXT               Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False]
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC.  [default: ]
```

##### Export examples

Export experiment by experiment ID.
```
python -u -m mlflow_export_import.experiment.export_experiment \
  --experiment 2 --output-dir out
```

Export experiment by experiment name.
```
python -u -m mlflow_export_import.experiment.export_experiment \
  --experiment sklearn-wine --output-dir out
```

##### Databricks export examples

See [Access the MLflow tracking server from outside Databricks](https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html).
```
export MLFLOW_TRACKING_URI=databricks
export DATABRICKS_HOST=https://mycompany.cloud.databricks.com
export DATABRICKS_TOKEN=MY_TOKEN

python -u -m mlflow_export_import.experiment.export_experiment \
  --experiment /Users/me@mycompany.com/SklearnWine \
  --output-dir out \
  --notebook-formats DBC,SOURCE 
```

##### Export directory structure

The output directory contains a manifest file and a subdirectory for each run (by run ID).
The run directory contains a `run.json` file containing run metadata and an artifact hierarchy.

```
+-manifest.json
+-441985c7a04b4736921daad29fd4589d/
| +-artifacts/
|   +-plot.png
|   +-sklearn-model/
|     +-model.pkl
|     +-conda.yaml
|     +-MLmodel
```

#### export_experiment_list

Export several (or all) experiments to a directory.

##### Usage
```
python -u -m mlflow_export_import.experiment.export_experiment_list --help

  --experiments TEXT              Experiment names or IDs (comma delimited).
                                  'all' will export all experiments.  [required]

  --output-dir TEXT               Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False]

  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC.  [default: ]
```

##### Export list examples

Export experiments by experiment ID.
```
python -u -m mlflow_export_import.experiment.export_experiment_list \
  --experiments 2,3 --output-dir out
```

Export experiments by experiment name.
```
python -u -m mlflow_export_import.experiment.export_experiment_list \
  --experiments sklearn,sparkml --output-dir out
```

Export all experiments.
```
python -u -m mlflow_export_import.experiment.export_experiment_list \
  --experiments all --output-dir out
```

##### Export directory structure

The output directory contains a manifest file and a subdirectory for each experiment (by experiment ID).

Each experiment subdirectory in turn contains its own manifest file and a subdirectory for each run.
The run directory contains a run.json file containing run metadata and an artifact hierarchy.

In the example below we have two experiments - 1 and 7. Experiment 1 (sklearn) has two runs (f4eaa7ddbb7c41148fe03c530d9b486f and 5f80bb7cd0fc40038e0e17abe22b304c) whereas experiment 7 (sparkml) has one run (ffb7f72a8dfb46edb4b11aed21de444b).

```
+-manifest.json
+-1/
| +-manifest.json
| +-f4eaa7ddbb7c41148fe03c530d9b486f/
| | +-run.json
| | +-artifacts/
| |   +-plot.png
| |   +-sklearn-model/
| |   | +-model.pkl
| |   | +-conda.yaml
| |   | +-MLmodel
| |   +-onnx-model/
| |     +-model.onnx
| |     +-conda.yaml
| |     +-MLmodel
| +-5f80bb7cd0fc40038e0e17abe22b304c/
| | +-run.json
|   +-artifacts/
|     +-plot.png
|     +-sklearn-model/
|     | +-model.pkl
|     | +-conda.yaml
|     | +-MLmodel
|     +-onnx-model/
|       +-model.onnx
|       +-conda.yaml
|       +-MLmodel
+-7/
| +-manifest.json
| +-ffb7f72a8dfb46edb4b11aed21de444b/
| | +-run.json
|   +-artifacts/
|     +-spark-model/
|     | +-sparkml/
|     |   +-stages/
|     |   +-metadata/
|     +-mleap-model/
|       +-mleap/
|         +-model/
```

Sample [experiment list manifest.json](samples/experiment_list/manifest.json).
```
{
  "info": {
    "mlflow_version": "1.11.0",
    "mlflow_tracking_uri": "http://localhost:5000",
    "export_time": "2020-09-10 20:23:45"
  },
  "experiments": [
    {
      "id": "1",
      "name": "sklearn"
    },
    {
      "id": "7",
      "name": "sparkml"
    }
  ]
}
```

Sample [experiment manifest.json](samples/experiment_list/1/manifest.json).

```
{
  "experiment": {
    "experiment_id": "1",
    "name": "sklearn",
    "artifact_location": "/opt/mlflow/server/mlruns/1",
    "lifecycle_stage": "active"
  },
  "export_info": {
    "export_time": "2020-09-10 20:23:45",
    "num_runs": 2
  },
  "run-ids": [
    "f4eaa7ddbb7c41148fe03c530d9b486f",
    "f80bb7cd0fc40038e0e17abe22b304c"
  ],
  "failed_run-ids": []
}
```


### Import Experiments

Import experiments from a directory. Reads the manifest file to import expirements and their runs.

The experiment will be created if it does not exist in the destination tracking server. 
If the experiment already exists, the source runs will be added to it.

There are two main programs to import experiments:
* import_experiment - imports one experiment
* import_experiment_list - imports a list of experiments

#### import_experiment

Imports one experiment.

##### Usage
```
python -u -m mlflow_export_import.experiment.import_experiment --help \

Options:
  --input-dir TEXT                Input path - directory  [required]
  --experiment-name TEXT          Destination experiment name  [required]
  --just-peek BOOLEAN             Just display experiment metadata - do not import
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.
  --import-mlflow-tags BOOLEAN    Import mlflow tags
  --import-metadata-tags BOOLEAN  Import mlflow_export_import tags
```

##### Import examples

```
python -u -m mlflow_export_import.experiment.import_experiment \
  --experiment-name imported_sklearn \
  --input-dir out
```

##### Databricks import examples

```
export MLFLOW_TRACKING_URI=databricks
python -u -m mlflow_export_import.experiment.import_experiment \
  --experiment-name /Users/me@mycompany.com/imported/SklearnWine \
  --input-dir exported_experiments/3532228
```

#### import_experiment_list

Import a list of experiments.

##### Usage

```
python -m mlflow_export_import.experiment.import_experiment_list --help

Options:
  --input-dir TEXT                Input directory.  [required]
  --experiment-name-prefix TEXT   If specified, added as prefix to experiment name.
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]
  --import-mlflow-tags BOOLEAN    Import mlflow tags.  [default: True]
  --import-metadata-tags BOOLEAN  Import mlflow_tools tags.  [default: False]
```

##### Import examples

```
python -u -m mlflow_export_import.experiment.import_experiment_list \
  --experiment-name-prefix imported_ \
  --input-dir out 
```

## Runs

### Export run

Export run to directory or zip file.

**Usage**

```
python -m mlflow_export_import.run.export_run --help

Options:
  --run-id TEXT                   Run ID.  [required]
  --output TEXT                   Output directory or zip file.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False] 
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC.  [default: ]
```


**Run examples**
```
python -u -m mlflow_export_import.run.export_run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --output out
```
```
python -u -m mlflow_export_import.run.export_run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --output run.zip
```

Produces a directory with the following structure:
```
run.json
artifacts
  plot.png
  sklearn-model
    MLmodel
    conda.yaml
    model.pkl
```
Sample [run manifest.json](samples/experiment_list/1/6ccadf17812d43929b093d75cca1c33f/run.json).
```
{   
  "info": {
    "run-id": "50fa90e751eb4b3f9ba9cef0efe8ea30",
    "experiment_id": "2",
    ...
  },
  "params": {
    "max_depth": "16",
    "max_leaf_nodes": "32"
  },
  "metrics": {
    "mae": 0.5845562996214364,
    "r2": 0.28719674214710467,
  },
  "tags": {
    "mlflow.source.git.commit": "a42b9682074f4f07f1cb2cf26afedee96f357f83",
    "mlflow.runName": "demo.sh",
    "run_origin": "demo.sh",
    "mlflow.source.type": "LOCAL",
    "mlflow_export_import.metadata.tracking_uri": "http://localhost:5000",
    "mlflow_export_import.metadata.timestamp": 1563572639,
    "mlflow_export_import.metadata.timestamp_nice": "2019-07-19 21:43:59",
    "mlflow_export_import.metadata.run-id": "130bca8d75e54febb2bfa46875a03d59",
    "mlflow_export_import.metadata.experiment_id": "2",
    "mlflow_export_import.metadata.experiment-name": "sklearn_wine"
  }
}
```

### Import run

Imports a run from a directory or zip file.

#### Usage

```
python -m mlflow_export_import.run.import_run  --help

Options:
  --input TEXT                    Input path - directory or zip file.  [required]
  --experiment-name TEXT          Destination experiment name.  [required]
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]
  --import-mlflow-tags BOOLEAN    Import mlflow tags.  [default: True]
  --import-metadata-tags BOOLEAN  Import mlflow_tools tags.  [default: False]
```

#### Import examples

Directory `out` is where you exported your run.

##### Local import example
```
python -u -m mlflow_export_import.run.import_run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --input out \
  --experiment-name sklearn_wine_imported
```

##### Databricks import example
```
export MLFLOW_TRACKING_URI=databricks
python -u -m mlflow_export_import.run.import_run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --input out \
  --experiment-name /Users/me@mycompany.com/imported/SklearnWine \
```

## Registered Models

### Export registered model

Export a registered model to a directory.
The default is to export all versions of a model including all None and Archived stages.
You can specify a list of stages to export.

Source: [export_model.py](mlflow_export_import/model/export_model.py).

**Usage**

```
python -m mlflow_export_import.model.export_model --help

Options:
  --model TEXT       Registered model name.  [required]
  --output-dir TEXT  Output directory.  [required]
  --stages TEXT      Stages to export (comma seperated). Default is all stages.
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC.  [default: ]
```

#### Run
```
python -u -m mlflow_export_import.model.export_model \
  --model sklearn_wine \
  --output-dir out \
  --stages Production,Staging
```
```
Found 6 versions
Exporting version 3 stage 'Production' with run_id 24aa9cce1388474e9f26d17100724cdd to out/24aa9cce1388474e9f26d17100724cdd
Exporting version 5 stage 'Staging' with run_id 8efd80f59b7946119d8f1838515eea25 to out/8efd80f59b7946119d8f1838515eea25
```

#### Output 

Output export directory example.

```
+-749930c36dee49b8aeb45ee9cdfe1abb/
| +-artifacts/
|   +-plot.png
|   +-sklearn-model/
|   | +-model.pkl
|   | +-conda.yaml
|   | +-MLmodel
|   |  
+-model.json
```

[model.json](samples/models/model.json)
```
{
  "registered_model": {
    "name": "sklearn_wine",
    "creation_timestamp": "1587517284168",
    "last_updated_timestamp": "1587572072601",
    "description": "hi my desc",
    "latest_versions": [
      {
        "name": "sklearn_wine",
        "version": "1",
        "creation_timestamp": "1587517284216",
. . .
```

### Import registered model

Import a registered model from a directory.

Source: [import_model.py](mlflow_export_import/model/import_model.py).

**Usage**

```
python -m mlflow_export_import.model.import_model --help

Options:
  --input-dir TEXT        Input directory produced by export_model.py.
                          [required]

  --model TEXT            New registered model name.  [required]
  --experiment-name TEXT  Destination experiment name  - will be created if it
                          does not exist.  [required]
  --delete-model BOOLEAN  First delete the model if it exists and all its
                          versions.  [default: False]
```


#### Run

```
python -u -m mlflow_export_import.model.import_model \
  --model sklearn_wine \
  --experiment-name sklearn_wine_imported \
  --input-dir out  \
  --delete-model True
```

```
Model to import:
  Name: sklearn_wine
  Description: my model
  2 latest versions
Deleting 1 versions for model 'sklearn_wine_imported'
  version=2 status=READY stage=Production run-id=f93d5e4d182e4f0aba5493a0fa8d9eb6
Importing latest versions:
  Version 1:
    current_stage: None:
    Run to import:
      run-id: 749930c36dee49b8aeb45ee9cdfe1abb
      artifact_uri: file:///opt/mlflow/server/mlruns/1/749930c36dee49b8aeb45ee9cdfe1abb/artifacts
      source:       file:///opt/mlflow/server/mlruns/1/749930c36dee49b8aeb45ee9cdfe1abb/artifacts/sklearn-model
      model_path: sklearn-model
      run-id: 749930c36dee49b8aeb45ee9cdfe1abb
    Importing run into experiment 'scratch' from 'out/749930c36dee49b8aeb45ee9cdfe1abb'
    Imported run:
      run-id: 03d0cfae60774ec99f949c42e1575532
      artifact_uri: file:///opt/mlflow/server/mlruns/13/03d0cfae60774ec99f949c42e1575532/artifacts
      source:       file:///opt/mlflow/server/mlruns/13/03d0cfae60774ec99f949c42e1575532/artifacts/sklearn-model
Version: id=1 status=READY state=None
Waited 0.01 seconds
```

### List all registered models

Calls the `registered-models/list` API endpoint and creates the file `registered_models.json`.
```
python -u -m mlflow_export_import.model.list_registered_models
```

cat registered_models.json
```
{
  "registered_models": [
    {
      "name": "keras_mnist",
      "creation_timestamp": "1601399113433",
      "last_updated_timestamp": "1601399504920",
      "latest_versions": [
        {
          "name": "keras_mnist",
          "version": "1",
          "creation_timestamp": "1601399113486",
          "last_updated_timestamp": "1601399504920",
          "current_stage": "Archived",
          "description": "",
          "source": "file:///opt/mlflow/server/mlruns/1/9176458a78194d819e55247eee7531c3/artifacts/keras-model",
          "run_id": "9176458a78194d819e55247eee7531c3",
          "status": "READY",
          "run_link": ""
        },
