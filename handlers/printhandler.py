import abstracthandler

class PrintHandler(abstracthandler.AbstractHandler):
    def __init__(self, section_name, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name, dry_run=dry_run)
    
    def runtask(self, name, conf):
        print "-", name
        for item in conf.items():
            print "  ", item

