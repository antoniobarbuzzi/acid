import abstracthandler

class NullHandler(abstracthandler.AbstractHandler):
    def __init__(self, section_name, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name, dry_run=dry_run)
    
    def runtask(self, name, confsection):
        pass
    
