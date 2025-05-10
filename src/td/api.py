from inspect import signature
from typing import get_type_hints
from pydantic import create_model
from fastapi import FastAPI, Body
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from torch_snippets import AD


from td.cli import cli


api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_command_context(command):
    """
    Check if the context settings have a route.
    """

    _default_route = command.callback.__name__.replace("_", "/")
    output = AD(
        route=f"/api/v1/{_default_route}",
        methods=["POST"],
    )

    context_settings = command.context_settings

    if not context_settings or not isinstance(context_settings, dict):
        return output

    if "route" in context_settings:
        route = context_settings["route"]
        output.route = route
    if "methods" in context_settings:
        output.methods = context_settings["methods"]

    return output


def make_route_func(func, sig, hints):
    fields = {
        param.name: (
            hints.get(param.name, str),
            param.default if param.default != param.empty else ...,
        )
        for param in sig.parameters.values()
    }

    Model = create_model(f"{func.__name__.capitalize()}Model", **fields)

    async def route_func(data: Model = Body(...)):  # noqa
        kwargs = data.dict()
        try:
            return func(**kwargs)
        except Exception as e:
            import traceback

            # return 500 error
            traceback_str = traceback.format_exc()
            print(f"Error: {str(e)}\n{traceback_str}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(e).split("\n"),
                    "traceback": traceback_str.split("\n"),
                },
            )

    route_func.__name__ = func.__name__
    return route_func


for command in cli.registered_commands:
    func = command.callback
    func_context = process_command_context(command)
    func.from_api = True

    sig = signature(func)
    hints = get_type_hints(func)

    api.add_api_route(
        func_context.route,
        make_route_func(func, sig, hints),
        methods=func_context.methods,
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("td.api:api", host="0.0.0.0", port=8765, reload=True)
