"""
MLflow Export / Import CLI
"""

from typing import List

import click

from mlflow_export_import._version import __mlflow_export_import__, __version__
from mlflow_export_import.bulk.export_all import export_all
from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.import_experiments import import_experiments
from mlflow_export_import.bulk.import_models import import_models
from mlflow_export_import.common.find_artifacts import find_artifacts
from mlflow_export_import.common.http_client import http_client
from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment
from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model
from mlflow_export_import.model.list_registered_models import list_models
from mlflow_export_import.run.export_run import export_run
from mlflow_export_import.run.import_run import import_run


@click.group()
@click.version_option(version=__version__, prog_name=__mlflow_export_import__)
@click.pass_context
def cli(ctx: click.core.Context) -> None:
    """
    MLflow Export / Import CLI: Command Line Interface
    """
    ctx.ensure_object(dict)


CLI_COMMANDS: List[click.Command] = [
    export_all,
    export_models,
    import_models,
    export_run,
    import_run,
    export_experiment,
    import_experiment,
    export_experiments,
    import_experiments,
    export_model,
    import_model,
    list_models,
    http_client,
    find_artifacts,
]

for command in CLI_COMMANDS:
    cli.add_command(command)

if __name__ == "__main__":
    cli()
