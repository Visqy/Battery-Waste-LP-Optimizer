import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from shiny import App, ui
from app_modules.state import create_state
from app_modules.page_home import home_ui, home_server
from app_modules.page_template import template_ui, template_server
from app_modules.page_upload import upload_ui, upload_server
from app_modules.page_editor import editor_ui, editor_server
from app_modules.page_validation import validation_ui, validation_server
from app_modules.page_optimization import optimization_ui, optimization_server
from app_modules.page_results import results_ui, results_server
from app_modules.page_documentation import documentation_ui, documentation_server
from app_modules.mathjax import mathjax_support

os.makedirs("data", exist_ok=True)

app_ui = ui.TagList(
    mathjax_support(),
    ui.page_navbar(
        home_ui("home"),
        template_ui("template"),
        upload_ui("upload"),
        editor_ui("editor"),
        validation_ui("validation"),
        optimization_ui("optimization"),
        results_ui("results"),
        documentation_ui("docs"),
        title="NMC Battery Recycling Supply Chain Optimizer",
        id="main_nav",
        bg="#1a5276",
        inverse=True,
    )
)


def server(input, output, session):
    state = create_state()
    home_server("home", state=state)
    template_server("template", state=state)
    upload_server("upload", state=state)
    editor_server("editor", state=state)
    validation_server("validation", state=state)
    optimization_server("optimization", state=state)
    results_server("results", state=state)
    documentation_server("docs", state=state)


app = App(app_ui, server)