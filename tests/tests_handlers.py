import path
import unittest
from cStringIO import StringIO
import configobj
from handlers import *
from handlers.abstracthandler import *
import getpass
import tempfile
import subprocess
import shutil

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
    machines = {tmpfile}
    user = %s
    source_dir = ../tests
    remote_dir = {tmpdir}/
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
        tmpfile = tempfile.mkstemp(suffix="acidtest")[1]
        tmpdir = tempfile.mkdtemp(suffix="acidtest")
        rh = RsyncHandler()
        c = rsync_conf.format(tmpfile=tmpfile, tmpdir=tmpdir)
        print c
        conf = configobj.ConfigObj(StringIO(c))
        
        with open(tmpfile, "w") as f:
            f.write("localhost\n")
        for sub in conf["RSYNC"]:
            rh.execute(sub, conf[rh.section_name][sub])
            rh.validate_configuration(sub, conf[rh.section_name][sub])
        ret = subprocess.call(["diff", "-rq", "../tests", tmpdir])
        self.assertEqual(ret, 0)
        for sub in conf["RSYNC"]:
            rh.execute(sub, conf[rh.section_name][sub])
            rh.validate_configuration(sub, conf[rh.section_name][sub])
        ret = subprocess.call(["diff", "-rq", "../tests", tmpdir])
        self.assertEqual(ret, 0)
        
        os.remove(tmpfile)
        shutil.rmtree(tmpdir)
        
    
    def test_scripthandler(self):
        sh = ScriptHandler()
        
        
        
        

        

if __name__ == '__main__':
    unittest.main()

