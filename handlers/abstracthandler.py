#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import functools
import urllib
import configobj
import fabric
import fabric.tasks
import re

import sys
import os

from lrucache import lru_cache
from fabric_libs.fab_utils import hostUp

def isValidHostname(hostname):
    validIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
    validHostnameRegex = "^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$";
    if re.match(validIpAddressRegex, hostname) or re.match(validHostnameRegex, hostname):
        return True
    else:
        return False

def setup_fabric():
    fabric.state.env.skip_on_failure = True
    fabric.state.env.preconnect = True
    fabric.state.env.skip_bad_hosts = True
    fabric.state.env.connection_attempts = 3
    fabric.state.env.pool_size = 10
    fabric.state.env.parallel = True
    #fabric.state.env.deploy_user='hadoop' #FIXME
    fabric.state.output.debug = False
    fabric.state.output.running = True

setup_fabric()

class InvalidConfigurationFile(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HandlerExecutionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AbstractHandler(object):
    def __init__(self, section_name, verbose, dry_run):
        self.section_name = section_name
        self.dry_run = dry_run
        self.verbose = verbose
    
    @lru_cache(maxsize=20)
    def _get_machines_uri(self, uri):
        machines = []
        f = urllib.urlopen(uri)
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                machines.append(line)
        return machines
        
    def get_machines(self, uri_or_host_list):
        #confline is a list of uris, hostnames and ip addresses
        machines = []
        for uri_or_host in uri_or_host_list:
            try:
                lst = self._get_machines_uri(uri_or_host)
                machines.extend(lst)
            except IOError:
                if isValidHostname(uri_or_host):
                    machines.append(uri_or_host)
        return machines

    def validate_conf(self, subsection_name, subsection_conf):
        # Override this
        self.get_machines(subsection_conf.as_list("machines"))
    
    def validate_configuration(self, option, value):
        # Do not ovverride
        AbstractHandler.validate_conf(self, option, value)
        self.validate_conf(option, value)
    
    def execute(self, subsection_name, subsection_conf):
        if isinstance(subsection_conf, configobj.Section):
            self.init(subsection_name, subsection_conf)
            runtask = functools.partial(self.runtask, subsection_name, subsection_conf)
            runtask = hostUp(runtask)
            runtask.name = "%s:%s" % (self.section_name, subsection_name)
            try:
                #Fabric does not use any logging facility, so this is the best way to disable output
                #TODO Redirect to log
                stdout = sys.stdout
                stderr = sys.stderr
                if not self.verbose:
                    devnull = open(os.devnull, 'w')
                    sys.stdout = devnull
                    sys.stderr = devnull
                fabric.tasks.execute(runtask, hosts=self.get_machines(subsection_conf.as_list("machines")))
            except SystemExit, e: # remember, Fabric call sys.exit(-1) if the execution of a section fails
                sys.stdout = stdout
                sys.stderr = stderr
                print "One or more hosts failed while executing task %s" % runtask.name
                raise HandlerExecutionError("One or more hosts failed while executing task %s" % runtask.name)
            finally:
                sys.stdout = stdout
                sys.stderr = stderr
                self.close(subsection_name, subsection_conf)
                for host, port in runtask.unreachable_machines:
                    print 'Host {host} on port {port} is down'.format(host=env.host, port=env.port)
        else:
            raise InvalidConfigurationFile("Cannot use '%s = %s'" % (subsection_name, subsection_conf))

    def init(self, subsection_name, confsection):
        pass
    
    def runtask(self, subsection_name, confsection):
        raise NotImplementedError("Subclasses should implement this!")
    
    def close(self, subsection_name, confsection):
        pass


    
    
