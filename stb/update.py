from contextlib import suppress
from pathlib import Path
from typing import List

import typer
from pysh import sh

from .db import Choices
from .db import run_on_single_service as stb_db
from .util import (
    ENV_VARS,
    SERVICE_PATHS_ARG,
    add_default_service_path,
    cd_with_log,
    gather_services,
    save_dotenv_file,
    sh_with_log,
)

app = typer.Typer(
    name="update",
    help="Updates your services' configurations, dependencies, submodules, and ports without losing any part of your environment or configurations",
)


@app.command()
@add_default_service_path
def env(service_paths: List[Path] = SERVICE_PATHS_ARG):
    """Update .env files with new/modified fields from .env.example"""
    for service in gather_services(service_paths).values():
        for field, example_value in service.dotenv_example.items():
            replacing_value = example_value or ENV_VARS.get(field)
            if field in service.dotenv:
                pass
            else:
                service.dotenv[field] = str(replacing_value) if replacing_value else ""
        save_dotenv_file(service)
        typer.echo(f"Updated {service.dotenv_path}")


@app.command()
@add_default_service_path
def ports(service_paths: List[Path] = SERVICE_PATHS_ARG) -> None:
    """I update service ports to allow you to quickly set up a set of microservices locally and use all others from dev"""
    services = gather_services(service_paths)
    service_to_port_mapper = {service.dir.name: port for port, service in enumerate(services.values(), start=8000)}
    microservice_fields = {convert_microservice_name_to_env_field(m): n for m, n in service_to_port_mapper.items()}
    for service_name, service in services.items():
        service.dotenv["SERVICE_PORT"] = str(service_to_port_mapper[service_name])
        for field in [f for f in service.dotenv if f.endswith("_URL")]:
            if field in microservice_fields:
                service.dotenv[field] = f"http://localhost:{microservice_fields[field]}"
            else:
                helm_defaults = (service.yaml_config or {}).get(field.lower())
                if helm_defaults is not None and "review" in helm_defaults:
                    service.dotenv[field] = helm_defaults["review"]

        save_dotenv_file(service)
        typer.echo(f"Updated {service.dotenv_path}")


@app.command()
@add_default_service_path
def package(
    service_paths: List[Path] = SERVICE_PATHS_ARG,
    update_dependencies: bool = typer.Option(
        False,
        "-u",
        "--update",
        help="Run poetry update instead of poetry install",
    ),
    pull_changes: bool = typer.Option(
        False,
        "-p",
        "--pull",
        help="Pull changes from remote",
    ),
    update_ports: bool = typer.Option(
        False,
        "-P",
        "--ports",
        help="Update service ports to allow ysou to quickly set up a set of microservices locally and use all others from dev",
    ),
    update_env: bool = typer.Option(
        False,
        "-e",
        "--env",
        help="Update .env files with new/modified fields from .env.example",
    ),
    checkout_to_master: bool = typer.Option(
        False,
        "-c",
        "--checkout",
        help="Stash the current changes and checkout to master",
    ),
    reset_databases: bool = typer.Option(
        False,
        "-d",
        "--reset-databases",
        help="Run 'stb db reset -fp' as well",
    ),
):
    """Install the dependencies from poetry.lock file, update submodules, optionally update dependencies, and optionally reset databases"""
    branches_where_stashes_happened = []

    for service in gather_services(service_paths).values():
        with cd_with_log(service.dir):
            if checkout_to_master:
                res = sh_with_log("git diff", capture=True)
                if res.stdout:
                    sh_with_log("git stash")
                    res = sh("git branch --show-current", capture=True)
                    if res.returncode == 0:
                        branches_where_stashes_happened.append(service.dir.name + "/" + res.stdout.strip())
                sh_with_log("git checkout master")
            if pull_changes:
                sh_with_log("git pull")
            sh_with_log("git submodule update --init --recursive", "", "")
            if update_dependencies:
                sh_with_log("poetry update")
            else:
                sh_with_log("poetry install")
            if update_env:
                env([service.dir])
            if update_ports:
                ports([service.dir])
            if reset_databases:
                with suppress(LookupError):
                    stb_db(service.dir, Choices.drop, force_drop=True)
                    stb_db(service.dir, Choices.create, parallel_migrations=True)

    if branches_where_stashes_happened:
        typer.echo(
            f"------------\nStashed changes in the following branches: {', '.join(branches_where_stashes_happened)}"
        )


def convert_microservice_name_to_env_field(name: str) -> str:
    return name.replace("-", "_").strip().upper() + "_URL"


if __name__ == "__main__":
    app()
