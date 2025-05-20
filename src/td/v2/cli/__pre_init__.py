import sys
from typer import Typer, Option, Argument
from pydantic import BaseModel
from pydantic_core._pydantic_core import PydanticUndefined
from inspect import signature, Parameter
from typing import Type
from typing_extensions import Annotated

from ..models.nodes import BlankModel
from ..core.db import create_db_and_tables

cli = Typer()
_cli = Typer()
create_db_and_tables()

if len(sys.argv) == 1:
    sys.argv.append("tw")


def register_cli_command(
    cli_name: str,
    long_name: str,
    func,
    schema: Type[BaseModel],
    autocompletions: dict = None,
    shorthands: dict = None,
):
    def command_wrapper(**kwargs):
        instance = schema(**kwargs)
        if hasattr(command_wrapper, "_source"):
            func.__self__._source = command_wrapper._source
        if type(instance) is BlankModel:
            result = func()
        else:
            result = func(instance)
        return result

    def _get_position(field):
        if getattr(field, "json_schema_extra") is not None:
            return field.json_schema_extra.get("position")
        return 100

    parameters = []
    fields = sorted(
        schema.model_fields.items(),
        key=lambda item: (_get_position(item[1]), item[1].is_required()),
    )
    for name, field in fields:
        param_kind = (
            Parameter.POSITIONAL_OR_KEYWORD
            if field.is_required()
            else Parameter.KEYWORD_ONLY
        )
        if (
            not field.is_required() and field.default == PydanticUndefined
        ) or field.frozen:
            continue
        # default = Parameter.empty if field.is_required() else field.default
        # parameters.append(Parameter(name, param_kind, default=default))
        autocompletion = autocompletions.get(name) if autocompletions else None
        shorthand = shorthands.get(name, f"--{name}") if shorthands else f"--{name}"
        if field.is_required():
            default = Parameter.empty
            parameters.append(
                Parameter(
                    name,
                    param_kind,
                    default=default,
                    annotation=Annotated[
                        str,
                        Argument(
                            help=field.description,
                            autocompletion=autocompletion,
                        ),
                    ],
                )
            )
        else:
            default = field.default
            parameters.append(
                Parameter(
                    name,
                    param_kind,
                    default=default,
                    annotation=Annotated[
                        str | None,
                        Option(
                            shorthand,
                            autocompletion=autocompletion,
                        ),
                    ],
                )
            )

    parameters.sort(key=lambda p: p.kind.value)

    command_wrapper.__signature__ = signature(lambda **kwargs: None).replace(
        parameters=parameters
    )
    command_wrapper.__name__ = long_name
    command_wrapper.__doc__ = func.__doc__
    func.__self__._source = "cli"
    command_wrapper._source = "cli"

    cli.command(name=cli_name)(command_wrapper)
    return command_wrapper
