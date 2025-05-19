__all__ = ["cli"]

from .__pre_init__ import cli
from .db import *
from .sector import *
from .area import *
from .project import *
from .section import *
from .task import *
from .display import *


@cli.command(name="onboard")
def onboard():
    """
    Initialize the database with default areas, projects, and tasks.

    Creates predefined areas, projects, and tasks to help get started with the application.

    Returns:
        None. The function creates default data in the database.
    """
    set_database("default")
    remove_database("onboard")
    set_database("onboard")
    import importlib
    from . import sector, area, project, task, section

    for m in [sector, area, project, task, section]:
        importlib.reload(m)
    from .sector import sector_crud
    from .area import area_crud
    from .project import project_crud
    from .task import task_crud
    from .section import section_crud

    sector_crud.Create(
        data=SectorCreate(title="office,personal,gym,home,outdoor,kitchen")
    )
    area_crud.Create(
        data=AreaCreate(title="supplies,intro,desk,clients", sector_name="office")
    )
    area_crud.Create(data=AreaCreate(title="groceries,food", sector_name="kitchen"))
    area_crud.Create(data=AreaCreate(title="clothes", sector_name="personal"))
    project_crud.Create(
        data=ProjectCreate(
            title="onboarding,visit HQ,setup calendar",
            area_name="intro",
            sector_name="office",
        )
    )
    section_crud.Create(
        data=SectionCreate(
            title="meet with HR,cards and keys", path="office/intro/visit HQ"
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="ID Card,Laptop,Keys",
            path="office/intro/visit HQ/cards and keys",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Buy pens,Order printer paper,Purchase staplers",
            area_name="supplies",
            sector_name="office",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Buy milk,Get eggs,Purchase bread,Find cheese",
            area_name="groceries",
            sector_name="personal",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Schedule introductory meetings,Prepare onboarding documents,Set up new user accounts,Review company policies",
            area_name="intro",
            sector_name="office",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Organize desk,Arrange files,Set up computer",
            area_name="desk",
            sector_name="office",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Meet with clients,Prepare presentations,Send follow-up emails",
            area_name="clients",
            sector_name="office",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Buy running shoes,Get gym membership,Join yoga class",
            area_name="gym",
            sector_name="home",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Clean the house,Organize garage,Do laundry",
            area_name="recurring",
            sector_name="home",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Go for a walk,Plan a hike,Visit a park",
            area_name="outdoor",
            sector_name="outdoor",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Buy groceries,Plan meals,Organize pantry",
            area_name="groceries",
            sector_name="personal",
        )
    )
    task_crud.Create(
        data=TaskCreate(
            title="Cook dinner,Prepare lunch,Make breakfast",
            area_name="food",
            sector_name="personal",
        )
    )
    print(
        "-" * 10,
        "\nOnboarding complete! Default areas, projects, and tasks have been created in the database - onboard.db\n"
        "If you want to switch to a new personal database, use 'td dset <name>'\n",
        "-" * 10,
    )
