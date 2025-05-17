import sys
from typer import Typer
from pydantic import BaseModel
from pydantic_core._pydantic_core import PydanticUndefined
from inspect import signature, Parameter
from typing import Type, Literal, get_origin

from ..models.nodes import BlankModel
from ..core.db import create_db_and_tables

cli = Typer()
create_db_and_tables()

if len(sys.argv) == 1:
    sys.argv.append("tw")


def register_cli_command(cli_name: str, long_name: str, func, schema: Type[BaseModel]):
    def command_wrapper(**kwargs):
        instance = schema(**kwargs)
        if type(instance) is BlankModel:
            result = func()
        else:
            result = func(instance)
        return result

    parameters = []
    for name, field in schema.model_fields.items():
        param_kind = (
            Parameter.POSITIONAL_OR_KEYWORD
            if field.is_required()
            else Parameter.KEYWORD_ONLY
        )
        if (
            not field.is_required() and field.default == PydanticUndefined
        ) or field.frozen:
            continue
        default = Parameter.empty if field.is_required() else field.default
        parameters.append(Parameter(name, param_kind, default=default))

    parameters.sort(key=lambda p: p.kind.value)

    command_wrapper.__signature__ = signature(lambda **kwargs: None).replace(
        parameters=parameters
    )
    command_wrapper.__name__ = long_name
    command_wrapper.__doc__ = func.__doc__
    func.__self__._source = "cli"

    cli.command(name=cli_name)(command_wrapper)
    return command_wrapper
