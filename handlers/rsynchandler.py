import abstracthandler
import fabric.api
import fabric.contrib.project 


class RsyncHandler(abstracthandler.AbstractHandler):
    def __init__(self, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="RSYNC", dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        source_dir = confsection["source_dir"] + "/"
        remote_dir = confsection["remote_dir"] + "/"        
        user = confsection["user"]

    
    def runtask(self, option, confsection):
        source_dir = confsection["source_dir"] + "/"
        remote_dir = confsection["remote_dir"] + "/"        
        user = confsection["user"]
        
        with fabric.api.settings(user=user):
            if not self.dry_run:
                fabric.contrib.project.rsync_project(remote_dir=remote_dir, local_dir=source_dir)

