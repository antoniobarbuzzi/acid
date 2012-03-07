#!/usr/bin/env python
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import functools
import urllib
import configobj
import fabric
import fabric.tasks



from lrucache import lru_cache

def setup_fabric():
    fabric.state.env.skip_on_failure = True
    fabric.state.env.preconnect = True
    fabric.state.env.skip_bad_hosts = True
    fabric.state.env.connection_attempts = 3
    fabric.state.env.pool_size = 10
    fabric.state.env.parallel = True
    #fabric.state.env.deploy_user='hadoop' #FIXME
    fabric.state.output.debug = False
    fabric.state.output.running = False

setup_fabric()

class InvalidConfigurationFile(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AbstractHandler(object):
    def __init__(self, section_name, dry_run):
        self.section_name = section_name
        self.dry_run = dry_run
        
    @lru_cache(maxsize=20)
    def get_machines(self, url):
        machines = []
        for line in urllib.urlopen(url):
            line = line.strip()
            if line and not line.startswith("#"):
                machines.append(line)
        return machines

    def validate_conf(self, name, confsection):
        machines = confsection["machines"]
        self.get_machines(machines)
    
    def validate_configuration(self, option, value):
        AbstractHandler.validate_conf(self, option, value)
        self.validate_conf(option, value)
    
    def execute_target(self, section_name, subsection_name, subection_conf):
        if isinstance(subection_conf, configobj.Section):
            self.init(subsection_name, subection_conf)
            runtask = functools.partial(self.runtask, subsection_name, subection_conf)
            runtask.name = "%s:%s" % (section_name, subsection_name)
            fabric.tasks.execute(runtask, hosts=self.get_machines(subection_conf["machines"]))
            self.close(subsection_name, subection_conf)
        else:
            raise InvalidConfigurationFile("Cannot use '%s = %s'" % (subsection_name, subection_conf))

    def init(self, option, value):
        pass
    
    def runtask(self, option, value):
        raise NotImplemented()
    
    def close(self, option, value):
        pass


    
    