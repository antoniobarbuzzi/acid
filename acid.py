#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""acid.py: ACID. """
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import sys
import argparse

from engine import *
from handlers import *

def parse_arguments():
    parser = argparse.ArgumentParser(description='Automatic Cluster Installation Driver', epilog="For further informations, read the README file.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose")
    parser.add_argument('-c', '--config', default="config.ini", help="Read the configuration from the specified configuration file (default=config.ini)")
    parser.add_argument('--dry-run', action='store_true', help="Run the engine without really executing the script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help="Execute all the config file")
    group.add_argument('--sections', nargs='+', help="Execute all the subsections in a list of section. Ignore dependencies")
    group.add_argument('--subsections', nargs='+', help="Excute all the listed subsections. Ignore dependencies")
    group.add_argument('--validate', action='store_true', help="Validate the configuration file and exit")
    return parser.parse_args()
   
def run():
    args = parse_arguments()
    try:
        engine = Engine(args.config)
        engine.add_handler(RsyncHandler(args.dry_run))
        engine.add_handler(GitHandler(args.dry_run))
        engine.add_handler(UserHandler(args.dry_run))
        engine.add_handler(ScriptHandler(args.dry_run))
        engine.add_handler(PackageHandler(args.dry_run))
        #engine.add_handler(NullHandler("RSYNC"))
        #engine.add_handler(PrintHandler("GIT"))
        #engine.add_handler(NullHandler("GIT"))
        #engine.add_handler(NullHandler("SCRIPT"))
        #engine.add_handler(NullHandler("USERS"))
    except CyclicDependenciesException, e:
        print "ERROR: The configuration has cyclyc dependencies", e
        sys.exit(1)
    except HandlerAlreadyDefinedException, e:
        print "Handler Already Defined", e
        sys.exit(1)
    except InvalidSubsectionException, e:
        print "Invalid dependency target %s" % e
        sys.exit(1)
    
    if args.verbose:
        engine.print_conf()
    
    if not engine.validate_configuration():
        print "Invalid Configuration"
        sys.exit(1)
    if args.validate:
        sys.exit(0)
    
    try:
        if args.all:
            engine.execute_all()
        elif args.sections:
            for sec in args.sections:
                engine.execute_section(sec)
        elif args.subsections:
            for subsec in args.subsections:
                engine.execute_target(subsec)
        else:
            assert(False)
    except HandlerNotFoundException, e:
        print "Handler for section %s not found" % e
        sys.exit(1)
    except ConfigurationNotFoundException, e:
        print "Configuration not found for target %s" % e
        sys.exit(1)
    except InvalidSubsectionException, e:
        print "Invalid target %s" % e
        sys.exit(1)
        
run()
