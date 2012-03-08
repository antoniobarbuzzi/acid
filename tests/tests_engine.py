import path
import unittest
from cStringIO import StringIO
from engine import *
from handlers import NullHandler
import configobj

cycle_configuration = """
[USERS]
    [[HADOOP_USER]]
    depends = RSYNC:HADOOP
[PACKAGES]
    [[BASIC_DEPENDENCIES]]
    depends = USERS:HADOOP_USER
[RSYNC]
    [[HADOOP]]
    depends = RSYNC:JAVA
    [[JAVA]]
    depends = PACKAGES:BASIC_DEPENDENCIES
"""

missing_colon = """
[USERS]
    [[HADOOP_USER]]
    depends = RSYNCHADOOP
"""

double_colon = """
[USERS]
    [[HADOOP_USER]]
    depends = RS:YNCHAD:OOP
"""

invalid_file_1 = """
[ASD
val = ciao
"""

invalid_file_2 = """
[ASD]
    val = ciao
    [[CIAO]]
    pass
"""

dependency_not_defined = """
[USERS]
    [[HADOOP_USER]]
    depends = RSYNC:HADOOP
"""


order_1 = """
[A]
 [[1]]
 depends = A:2, B:1
 [[2]]
 depends = B:1, D:1
[B]
 [[1]]
 depends = C:1
[C]
 [[1]]
 depends = D:1
[D]
 [[1]]
 depends =
"""
correct_order_1 = [('D', '1'), ('C', '1'), ('B', '1'), ('A', '2'), ('A', '1')]


order_2 = """
[A]
 [[1]]
 depends = B:1
 [[2]]
 depends = B:1, A:1
[B]
 [[1]]
 depends = C:1
[C]
 [[1]]
 depends = D:1
[D]
 [[1]]
 depends =
"""
correct_order_2 = [('D', '1'), ('C', '1'), ('B', '1'), ('A', '1'), ('A', '2')]

class TestEngine(unittest.TestCase):

    #def setUp(self):
        #self.engine = Engine("config-example.ini")

    def test_exampleconfig(self):
        engine = Engine("../config-example.ini")
        
    
    def test_correct_order_1(self):
        f = StringIO(order_1)
        e = Engine(f)
        self.assertEqual(e.run_order, correct_order_1)
    
    def test_correct_order_2(self):
        f = StringIO(order_2)
        e = Engine(f)
        self.assertEqual(e.run_order, correct_order_2)

class TestEngineExceptions(unittest.TestCase):
    #HandlerNotFoundException
    def test_handler_not_found(self):
        e = Engine("../config-example.ini")
        e.add_handler(NullHandler("TEST"))
        self.assertRaises(HandlerNotFoundException, e.execute_section, "GIT")
        
    #IOError
    def test_configuration_not_found(self):
        self.assertRaises(IOError, lambda x:Engine(x), "/tmp/invalidfilename")
    
    #ParseError
    def test_invalid_file(self):
        f = StringIO(invalid_file_1)
        self.assertRaises(configobj.ParseError, lambda x:Engine(x), f)
        f = StringIO(invalid_file_2)
        self.assertRaises(configobj.ParseError, lambda x:Engine(x), f)
    
    #CyclicDependenciesException
    def test_cycle_exception(self):
        f = StringIO(cycle_configuration)
        self.assertRaises(CyclicDependenciesException, lambda x:Engine(x), f)
    
    #InvalidSubsectionException
    def test_missing_colon(self):
        f = StringIO(missing_colon)
        self.assertRaises(InvalidSubsectionException, lambda x:Engine(x), f)

    def test_double_colon(self):
        f = StringIO(double_colon)
        self.assertRaises(InvalidSubsectionException, lambda x:Engine(x), f)
    
    def test_execute_subsection_error(self):
        engine = Engine("../config-example.ini")
        self.assertRaises(InvalidSubsectionException, engine.execute_subsection, "PROVA")
    
    # HandlerAlreadyDefinedException
    def test_handler_already_defined(self):
        engine = Engine("../config-example.ini")
        engine.add_handler(NullHandler("TEST"))
        self.assertRaises(HandlerAlreadyDefinedException, engine.add_handler, NullHandler("TEST"))
    
    #InvalidDependencyException    
    def test_dependency_not_defined(self):
        f = StringIO(dependency_not_defined)
        self.assertRaises(InvalidDependencyException, lambda x:Engine(x), f)
    
    
    

class TestEngineExecution(unittest.TestCase):
    def setUp(self):
        self.engine = Engine("../config-example.ini")
        self.engine.add_handler(NullHandler("RSYNC"))
        self.engine.add_handler(NullHandler("GIT"))
        self.engine.add_handler(NullHandler("SCRIPT"))
        self.engine.add_handler(NullHandler("USERS"))
        self.engine.add_handler(NullHandler("PACKAGES"))
    
    def test_execute_all(self):
        self.engine.execute_all()
    
    def test_execute_section(self):
        self.engine.execute_section("RSYNC")
    
    def test_execute_subsection(self):
        self.engine.execute_subsection("GIT:HADOOP_CONFIGURATION")
        

if __name__ == '__main__':
    unittest.main()

