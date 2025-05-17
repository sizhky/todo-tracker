from inspect import signature, Parameter
from typing import get_type_hints
from pydantic import create_model
from fastapi import FastAPI, Body
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from torch_snippets import AD


from td.__pre_init__ import cli


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
    Process the context settings of a CLI command to determine its API route and methods.

    Args:
        command: A Click command object with callback and context_settings attributes.

    Returns:
        An AD (AttributeDict) object containing:
            - route: The API endpoint route path, defaulting to '/api/v1/{command_name}'.
            - methods: HTTP methods allowed for this endpoint, defaulting to ["POST"].
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
    """
    Create a FastAPI route function from a CLI command function.

    This function dynamically creates a Pydantic model based on the function's signature
    and type hints, then wraps the original function in an async route handler that
    validates input data according to the model.

    Args:
        func: The original CLI function to be converted to an API route.
        sig: The signature object of the function.
        hints: Type hints dictionary for the function parameters.

    Returns:
        An async route function that can be used with FastAPI's add_api_route.
    """
    fields = {}
    for param in sig.parameters.values():
        annotation = hints.get(param.name, str)
        default = ... if param.default == Parameter.empty else param.default
        fields[param.name] = (annotation, default)

    Model = create_model(f"{func.__name__.capitalize()}Model", **fields)

    async def route_func(data: Model = Body(...)):  # noqa
        """
        FastAPI route handler that processes incoming request data.

        This function validates the request data against the created Pydantic model,
        calls the original CLI function with the validated data, and handles any
        exceptions by returning appropriate HTTP error responses.

        Args:
            data: Request body data validated against the Pydantic model.

        Returns:
            The result of the original CLI function call.

        Raises:
            HTTPException: If an exception occurs during the function execution.
        """
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

    uvicorn.run("td.api:api", host="127.0.0.1", port=8765, reload=True)
