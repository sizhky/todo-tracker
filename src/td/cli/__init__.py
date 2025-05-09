__all__ = ["cli"]

from .__pre_init__ import cli
from .area import *
from .project import *
from .task import *


@cli.command(name="onboard")
def onboard():
    create_area("office,personal,gym,home,outdoor")
    create_project("supplies,intro,desk,clients", area="office")
    create_project("groceries,food,clothes", area="personal")
    create_task("a,b,c,d,e", project="supplies", area="office")
    create_task("f,g,h,i,j", project="groceries", area="personal")
    create_task("k,l,m,n,o", project="intro", area="office")
