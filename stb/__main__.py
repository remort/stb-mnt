from typing import List

import typer
from pysh import which

from stb import config, db, run, update, use
from stb.__version__ import __version__

app = typer.Typer(
    name="stb",
    add_completion=False,
    help="Stanislav's Toolbox (stb) helps you manage your local microservices. Specifically, it can set them up for you, create/delete/migrate databases, manage service ports and .env files, and much more",
)

app.add_typer(db.app, name="db")
app.add_typer(update.app)
app.add_typer(config.config_app)


def version_callback(value: bool):
    if value:
        typer.echo(f"Stanislav's Toolbox {__version__}")
        raise typer.Exit()


@app.command(name="use")
def use_(
    package_name: str = typer.Argument(..., help="Package to use. For example, `my_package`", show_default=False),
    version_or_path: str = typer.Argument(
        ...,
        help="Either package version or path to the package. For example, `8.3.1` or `~/my_package`",
        show_default=False,
    ),
) -> None:
    """Switches the version of a company package in the current project. For example, `stb use my_package 0.1.0` or `stb use my_package ~/package`"""
    return use.use_package(package_name, version_or_path)


def run_(
    services: List[str] = typer.Argument(
        ...,
        help="The select services to checkout and run together at the same time",
    ),
) -> None:
    return run.run_services(set(services))


if which("concurrently"):
    run_ = app.command(name="run")(run_)

try:
    from stb import setup

    @app.command(name="setup")
    def setup_(
        services: List[str] = typer.Argument(
            ...,
            help="Names of services to setup. For example, use 'backend/oatmeal' to setup oatmeal service in the backend namespace",
        ),
        no_clone: bool = typer.Option(
            False, "--no-clone", help="Skips cloning the services. Useful if you've already cloned them"
        ),
    ) -> None:
        """Does the initial localhost setup of microservices. Downloads, configures .env, inits submodules, installs the correct pyenv environment, creates the correct poetry environment, and installs dependencies"""
        return setup.setup_services(services, no_clone)

except ImportError:
    pass


@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    ...


if __name__ == "__main__":
    app()
