import abstracthandler
from fabric_libs.fab_utils import adduser

class UserHandler(abstracthandler.AbstractHandler):
    def __init__(self, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="USERS", dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        user=confsection["user"]
        password=confsection["password"]
        home=confsection["home"]
        gecos=confsection["gecos"]
        shell=confsection["shell"]

    
    def runtask(self, name, confsection):
        user=confsection["user"]
        password=confsection["password"]
        home=confsection["home"]
        gecos=confsection["gecos"]
        shell=confsection["shell"]
        if not self.dry_run:
            adduser(user, password, home, gecos, shell)
