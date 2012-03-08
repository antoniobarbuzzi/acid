import path
import unittest
from cStringIO import StringIO
import configobj
from handlers import *
from handlers.abstracthandler import *
import getpass

test_conf = """
[TEST]
    [[SUB_1]]
    machines = ../slave-example.txt
    [[SUB_2]]
    machines = ../slave-example.txt
"""

rsync_conf = """
[RSYNC]
    [[A]]
    machines = /tmp/localhost
    user = %s
    source_dir = ../tests
    remote_dir = /tmp/test
""" % (getpass.getuser())

script_conf = """
[RSYNC]
    [[A]]
    machines = /tmp/localhost
    user = %s
    script = /
""" % (getpass.getuser())

class TestHandlers(unittest.TestCase):
    
    def test_abstracthandler(self):
        ah = AbstractHandler("TEST", False)
        conf = configobj.ConfigObj(StringIO(test_conf))
        def runtask(*args, **kwargs):
            pass
        ah.runtask = runtask        
        for sub in conf["TEST"]:
            ah.execute(sub, conf["TEST"][sub])
            ah.validate_configuration(sub, conf["TEST"][sub])
    
    
    def test_rsynchandler(self):
        rh = RsyncHandler()
        conf = configobj.ConfigObj(StringIO(rsync_conf))
        with open("/tmp/localhost", "w") as f:
            f.write("localhost\n")
        for sub in conf["RSYNC"]:
            rh.execute(sub, conf[rh.section_name][sub])
            rh.validate_configuration(sub, conf[rh.section_name][sub])
    
    def test_scripthandler(self):
        sh = ScriptHandler()
        
        
        
        

        

if __name__ == '__main__':
    unittest.main()

