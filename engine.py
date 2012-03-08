#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""engine.py: ACID. """
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import networkx as nx
import configobj
from handlers import *

class HandlerNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HandlerAlreadyDefinedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CyclicDependenciesException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Graph is cyclic - Topological sorting is meaningful only for directed acyclic graphs. "

class InvalidSubsectionException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidDependencyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Engine():
    def __init__(self, infile):        
        self.conf = configobj.ConfigObj(infile, file_error=True, list_values=True, create_empty=False, interpolation=True)
        self.__handlers__ = {}
        DG = self.__construct_graph()
        if not nx.is_directed_acyclic_graph(DG):
            raise CyclicDependenciesException() #FIXME Add cycle list
        self.run_order = nx.topological_sort(DG)
        #print "Run Order:", self.run_order
    
    def validate_configuration(self):
        correct = True
        for section, subsection in self.run_order:
            #section, subsection = task.split(':')
            if not self.__handlers__.has_key(section):
                raise HandlerNotFoundException(section)
            handler = self.__handlers__[section]
            try:
                handler.validate_configuration(subsection, self.conf[section][subsection])
            except KeyError, e:
                print "\n ** %s:%s: missing %s parameter **" % (section, subsection, e.message)
                correct = False
            except IOError, e:
                print "\n ** %s **" % e
                correct = False

        return correct

    def __construct_graph(self):
        DG = nx.DiGraph()
        conf = self.conf        
        edges = set()
        for section in conf.sections:
            for subsection in conf[section].sections:
                thisnode = (section, subsection)
                DG.add_node(thisnode)
                if conf[section][subsection].has_key("depends"):
                    dep_str = conf[section][subsection].as_list("depends")
                    deps = [tuple(d.split(":")) for d in dep_str if d != ""]
                    for dep in deps:
                        if len(dep)!=2:
                            raise InvalidSubsectionException(dep)
                else:
                    deps = []
                for node in deps:
                    edges.add((node, thisnode))
        
        for edge in edges:
            if not edge[0] in DG: # edge[1] is thisnode and we have it in the configuration file for sure
                raise InvalidDependencyException("%s:%s in section %s:%s" % (edge[0][0], edge[0][1], edge[1][0], edge[1][1]))
            else:
                DG.add_edge(*edge)
        return DG

    def print_conf(self):
        #width = 30
        #headerstring = "Configuration"
        #l = (width - len(headerstring)-2)/2
        #print "=" * l + " " + headerstring + " " + "=" * l
        self.__print_conf(self.conf)
        #print "="*(2*l + 2 + len(headerstring))

    def __print_conf(self, config, level=1):
        indentation = "   " * (level-1)
        for section in config:
            if isinstance(config[section], configobj.Section):
                if level == 1:
                    if self.__handlers__.has_key(section):
                        handler = type(self.__handlers__[section]).__name__
                    else:
                        handler = "No Handler Defined"
                    print indentation, "[" * level, section, "]" * level, "-->", handler
                else:
                    print indentation, "[" * level, section, "]" * level
                for option, value in config[section].iteritems():                
                    if isinstance(value, configobj.Section):
                        self.__print_conf({option:value}, level+1)
                    else:
                        print indentation, "  ", option, "=", value
            else:
                print indentation, section, "=", config[section]
    
    def execute_all(self):
        for section, subsection in self.run_order:
            self.__execute_subsection(section, subsection)

    def execute_section(self, section_name):
        done = False
        for section, subsection in self.run_order:
            if section == section_name:
                done = True
                self.__execute_subsection(section, subsection)
        if not done:
            raise HandlerNotFoundException(section_name)
    
    def execute_subsection(self, subsection_full_name):
        try:
            section, subsection = subsection_full_name.split(":")
        except ValueError, e:
            raise InvalidSubsectionException(subsection_full_name)
        self.__execute_subsection(section, subsection)
    
    def __execute_subsection(self, section, subsection):
        handler = self.__get_handler(section)
        if not self.conf[section].has_key(subsection): # I'm sure that conf[section] exists, otherwise __get_handler would have thrown an exeception
            raise ConfigurationNotFoundException("%s:%s" % (section, subsection))
        conf = self.conf[section][subsection]
        print "Executing [%s:%s]" % (section, subsection)
        handler.execute(subsection, conf)

    def __get_handler(self, section_name):
        if self.__handlers__.has_key(section_name):
                return self.__handlers__[section_name]
        else:
            #print "Handler for %s not found" % section_name
            raise HandlerNotFoundException(section_name)
    
    def add_handler(self, handler):
        if not self.__handlers__.has_key(handler.section_name):
            self.__handlers__[handler.section_name] = handler
        else:
            raise HandlerAlreadyDefinedException(handler.section_name)

            
