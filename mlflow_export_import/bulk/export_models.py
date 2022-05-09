"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import json
import time
import click
from concurrent.futures import ThreadPoolExecutor
import mlflow
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import import utils, click_doc
from mlflow_export_import.bulk import write_export_manifest_file
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models
from mlflow_export_import.bulk import bulk_utils

client = mlflow.tracking.MlflowClient()

def _export_models(model_names, output_dir, notebook_formats, stages, export_run=True, use_threads=False):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()
    model_names = bulk_utils.get_model_names(model_names)
    print("Models to export:")
    for model_name in model_names:
        print(f"  {model_name}")

    exporter = ModelExporter(stages=stages, notebook_formats=utils.string_to_list(notebook_formats), export_run=export_run)
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model_name in model_names:
            dir = os.path.join(output_dir, model_name)
            future = executor.submit(exporter.export_model, model_name, dir)
            futures.append(future)
    ok_models = [] ; failed_models = []
    for future in futures:
        result = future.result()
        if result[0]: ok_models.append(result[1])
        else: failed_models.append(result[1])

    duration = round(time.time() - start_time, 1)
    manifest = {
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice(),
            "total_models": len(model_names),
            "ok_models": len(ok_models),
            "failed_models": len(failed_models),
            "duration": duration
        },
        "stages": stages,
        "notebook_formats": notebook_formats,
        "ok_models": ok_models,
        "failed_models": failed_models
    }

    fs = _filesystem.get_filesystem(output_dir)
    fs.mkdirs(output_dir)
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        f.write(json.dumps(manifest, indent=2)+"\n")

    print(f"{len(model_names)} models exported")
    print(f"Duration for registered models export: {duration} seconds")


def export_models_wrapper(model_names, output_dir, notebook_formats, stages="",
                          export_all_runs=False, use_threads=False):
    exps_and_runs = get_experiments_runs_of_models(model_names)
    exp_ids = exps_and_runs.keys()
    start_time = time.time()
    out_dir = os.path.join(output_dir,"experiments")
    exps_to_export = exp_ids if export_all_runs else exps_and_runs
    export_experiments.export_experiments(exps_to_export, out_dir, True, notebook_formats, use_threads)
    _export_models(model_names, os.path.join(output_dir,"models"), notebook_formats, stages, export_run=False, use_threads=use_threads)
    duration = round(time.time() - start_time, 1)
    write_export_manifest_file(output_dir, duration, stages, notebook_formats)
    print(f"Duration for total registered models and versions' runs export: {duration} seconds")


@click.command()
@click.option("--output-dir",
     help="Output directory.",
     type=str,
    required=True
)
@click.option("--models",
    help="Models to export. Values are 'all', comma seperated list of models or model prefix with * ('sklearn*'). Default is 'all'",
    type=str,
    default="all"
)
@click.option("--stages",
    help=click_doc.model_stages,
    type=str,
    required=False
)
@click.option("--notebook-formats",
    help=click_doc.notebook_formats,
    type=str,
    default="",
    show_default=True
)
@click.option("--export-all-runs",
    help="Export all runs of experiment or just runs associated with registered model versions.",
    type=bool,
    default=False,
    show_default=False
)
@click.option("--use-threads",
    help=click_doc.use_threads,
    type=bool,
    default=False,
    show_default=True
)
def export_models(models,
                  output_dir,
                  stages,
                  notebook_formats,
                  export_all_runs,
                  use_threads):
    """
    Exports models and their versions' backing

    Run along with the experiment that the run belongs to.
    """
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_models_wrapper(models,
                          output_dir=output_dir,
                          notebook_formats=notebook_formats,
                          stages=stages,
                          export_all_runs=export_all_runs,
                          use_threads=use_threads)


if __name__ == "__main__":
    export_models()
