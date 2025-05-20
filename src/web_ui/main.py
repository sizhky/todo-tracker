from torch_snippets import makedir, P
from fasthtml.common import *
from fasthtml.components import Zero_md
from td.v2.cli.display import fetch
from td.v2.cli.sector import _list_sectors
from subprocess import run
import qrcode

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
        Div(A("Hello", href="/mobile"), style="text-align: center;"),
        *[render_sector(sector) for sector in _list_sectors()],
    )


@rt("/mobile")
def get():
    ip = run(
        "ifconfig | grep 192", shell=True, capture_output=True, text=True
    ).stdout.split()[1]
    ip = f"http://{ip}:1234"
    img = qrcode.make(ip)
    makedir(static_path)
    img.save(f"{static_path}/ip.png")
    return Titled(
        "Scan QR",
        Div(Img(src="ip.png"), Div(ip), style="text-align: center;"),
    )


if __name__ == "__main__":
    serve(port=1234)
