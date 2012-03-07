ACID - Automatic Cluster Installation Driver
==================

ACID is an open source tool for automatize installation of software on a cluster
of machines. It is originally developed in order to install Apache Hadoop, but 
it can be easily used to install everything.

The whole installation process is managed by a ini configuration file (see the
example included), that defines a set of 'Sections'.
Each section is managed by a specific handler (for example, [RSYNC] section is
managed by RsyncHandler).
The installation is managed my a series of subsections, that defines what to do.
For example, each subsection of RSYNC have the source and destination path for rsync.

The subsection configurations are handler specific, except for "depends" and "machines":
 - "machines" defines the list of machine where the subsection should be executed
 - "depends" defines the list of dependencies.

ACID creates a list of subsections to execute in order to satisfy all the dependencies
declared in the configuration file, and execute the remote 

Quick start
-----------
Install all the dependencies:
 - fabric
 - networkx

It is suggested to use the lastest version of fabric from github, that supports the parallel
execution of tasks.

In order to run parallely, you need to create an ssh key and copy it on the remote machine.

Then create a configuration file (look at the example configuration) and execute acid:
    
    python acid.py --config configuration.ini --all

In order to execute a specific subsection:
    
    python acid.py --config configuration.ini --subsection RSYNC:HADOOP_CONFIGURATION


Dependencies
-----------
ACID works like Ant or Make: each subsection corresponds to an Ant's target, and has a
list of all the sections that have to be executed before it.

In the following example, ACID execute first COPY_PROGRAM and after its completion, COPY_CONF
    
    [RSYNC]
        [[COPY_PROGRAM]]
        depends = 
        ... 
        
        [[COPY_CONF]]
        depends = RSYNC:COPY_PROGRAM


Handlers
------------------
Now there are only a few handlers:

 - GitHandler: clone a GIT project in a remote directory
 - UserHandler: create a user
 - ScriptHandler: execute a script on the remote hosts
 - PackageHandler: install a list of packages on the remote hosts
 - RsyncHandler: copy, using rsync, a local directory to a remote one

Defining a new handler is foolproof: just create a new class that inheriths from
AbstractHandler and define a runtask method. The runtask method is the task that is
executed on a remote host.

ACID uses fabric (http://fabfile.org/) in order to execute the remote tasks.


Contributing
------------

Contributions are extremely welcome, as are suggestions about how to structure,
package, and test the program. Feel free to send me an email or pull request
and I'll get back ASAP.