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
        
class RecursiveSection(configobj.Section):
    def __init__(self, section):
        configobj.Section.__init__(self, section.parent, section.depth, section.main, section, section.name)
    
    def __getitem__(self, key):
        if key == "handlers" or self.parent == self or dict(self).has_key(key):
            return configobj.Section.__getitem__(self, key)
        else:
            return RecursiveSection.__getitem__(RecursiveSection(self.parent), key)
    
    def has_key(self, key):
        try:
            self.__getitem__(key)
        except:
            return False
        else:
            return True


class Engine():
    def __init__(self, infile, verbose=False, dry_run=False):
        self.infile = infile
        self.verbose = verbose
        self.dry_run = dry_run
        
        self.conf = configobj.ConfigObj(infile, file_error=True, list_values=True, create_empty=False, interpolation=True)
        self.__handlers__ = {}
        self.__sections_to_stringhandlers = {}
        self.DG = self.__construct_graph()
        if not nx.is_directed_acyclic_graph(self.DG):
            raise CyclicDependenciesException() #FIXME Add cycle list
        self.run_order = nx.topological_sort(self.DG)
        
    
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
        edges = set()
        incomplete_edges = set()
        nodes = set()
        
        def fullname(section):
            tmp = section.name
            namelist = []
            while True:
                if section.name is None:
                    break
                else:
                    namelist.append(section.name)
                    section = section.parent
            return ":".join(reversed(namelist))        

        def resolve_dep(thisection, dep):
            if ":" in dep or dep == "ALL":
                return dep
            elif thisection.name is None and dep in thisection:
                return dep
            elif thisection.name is None:
                raise Exception("Unable to resolve dependency %s" % dep)
            elif dep in thisection.sections:
                return fullname(thisection) + ":" + dep
            else:
                return resolve_dep(thisection.parent, dep)
                
        def __recursive_walk(thisection):
            section_name = fullname(thisection)
            if section_name != "INIT" and section_name!="":
                edges.add(("INIT", section_name))
            if thisection.has_key("handler"):
                self.__sections_to_stringhandlers[section_name] = thisection["handler"]
                assert(section_name!="")
                nodes.add(section_name)
                if thisection.has_key("depends"):
                    dependencies = thisection.as_list("depends")
                    dependencies = [resolve_dep(thisection, dep) for dep in dependencies if dep!=""]
                    for dep in dependencies:
                        if dep=="ALL":
                            incomplete_edges.add(section_name)
                        else:
                            edges.add((dep, section_name))
            else:
                for section in thisection.sections:
                    if thisection.name is not None:
                        edges.add((fullname(thisection[section]), section_name))
                    __recursive_walk(RecursiveSection(thisection[section]))
        
        __recursive_walk(RecursiveSection(self.conf))
        
        for edge_node in incomplete_edges:
            for node in nodes:
                if node != edge_node:
                    edges.add((node, edge_node))
        
        DG.add_nodes_from(nodes)
        DG.add_edges_from(edges)
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
        for section in self.run_order:
            if section in self.__sections_to_stringhandlers:
                self.__execute_subsection(section)
    
    def __execute_subsection(self, section):
        handler = self.__get_handler(self.__sections_to_stringhandlers[section])
        conf = self.conf
        for s in section.split(":"):
            conf = conf[s]
        print "Executing [%s]" % (section)
        if self.dry_run:
            print "DryRun handler.execute(%s, conf)" % section
        else:
            handler.execute(section, RecursiveSection(conf))

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


if __name__ == '__main__':
    e = Engine("config-example.ini")
    print e.DG