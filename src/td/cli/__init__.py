__all__ = ["cli"]

from .__pre_init__ import cli
from .area import *
from .project import *
from .task import *


@cli.command(name="onboard")
def onboard():
    """
    Initialize the database with default areas, projects, and tasks.

    Creates predefined areas, projects, and tasks to help get started with the application.

    Returns:
        None. The function creates default data in the database.
    """
    create_area("office,personal,gym,home,outdoor")
    create_project("supplies,intro,desk,clients", area="office")
    create_project("groceries,food,clothes", area="personal")
    create_task(
        "Buy pens,Order printer paper,Purchase staplers",
        project="supplies",
        area="office",
    )
    create_task(
        "Buy milk,Get eggs,Purchase bread,Find cheese",
        project="groceries",
        area="personal",
    )
    create_task(
        "Schedule introductory meetings,Prepare onboarding documents,Set up new user accounts,Review company policies",
        project="intro",
        area="office",
    )
    create_task(
        "Organize desk,Arrange files,Set up computer", project="desk", area="office"
    )
    create_task(
        "Meet with clients,Prepare presentations,Send follow-up emails",
        project="clients",
        area="office",
    )
    create_task(
        "Buy running shoes,Get gym membership,Join yoga class",
        project="gym",
        area="home",
    )
    create_task(
        "Clean the house,Organize garage,Do laundry", project="home", area="home"
    )
    create_task(
        "Go for a walk,Plan a hike,Visit a park", project="outdoor", area="outdoor"
    )
    create_task(
        "Buy groceries,Plan meals,Organize pantry", project="groceries", area="personal"
    )
    create_task(
        "Cook dinner,Prepare lunch,Make breakfast", project="food", area="personal"
    )
