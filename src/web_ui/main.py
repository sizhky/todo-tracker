from torch_snippets import makedir, P
from fasthtml.common import *
from fasthtml.components import Zero_md
from td.v2.cli.display import fetch
from td.v2.cli.sector import _list_sectors
from subprocess import run
import qrcode
import requests

zeromd_headers = [
    Script(type="module", src="https://cdn.jsdelivr.net/npm/zero-md@3?register")
]
static_path = "static"
app, rt = fast_app(hdrs=zeromd_headers, static_path=static_path, static_url="/static")

opened = set("_")


def render_local_md(text, css=""):
    css_template = Template(Style(css), data_append=True)
    md = f"```text\n{text}\n```"
    return Zero_md(css_template, Script(md, type="text/markdown"))


def render_sector(sector):
    return Details(
        Summary(H3(sector)),
        render_local_md(fetch(sector=sector)),
        open=True if sector in opened else False,
    )


@rt("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    print(fname, ext)
    current_dir = P(__file__).resolve().parent
    file_path = current_dir / "public" / f"{fname}.{ext}"
    return FileResponse(file_path)


@rt("/")
def get():
    return Titled(
        "Tracker",
        Div(
            *[render_sector(sector) for sector in _list_sectors()],
            style="text-align: left;",
        ),
        Div(*[Br()] * 3, H4(A("🐍", href="/mobile"))),
        style="text-align: center;",
    )


@rt("/mobile")
def get():
    # Get the public ngrok URL (assumes ngrok is running and API is accessible)
    try:
        resp = requests.get("http://localhost:4040/api/tunnels")
        tunnels = resp.json().get("tunnels", [])
        public_url = tunnels[0]["public_url"] if tunnels else None
        ip = public_url if public_url else "Ngrok not running"
    except Exception as e:
        ip = f"Ngrok not running: {e}"
    img = qrcode.make(ip)
    makedir(static_path)
    img.save(f"{static_path}/ip.png")
    return Titled(
        Div(A("Task Tracker", href="/"), style="text-align: center;"),
        Div(Img(src="ip.png"), Div(A(ip)), style="text-align: center;"),
    )


if __name__ == "__main__":
    serve(port=1234)
