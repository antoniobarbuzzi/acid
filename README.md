# ACID - Automatic Cluster Installation Driver


**ACID** is an open source tool to automatize the installation of software on a cluster.
It is originally developed in order to install Apache Hadoop, but it can be easily
used to install everything.

## Description

The whole installation process is managed by an *INI* configuration file (see the
example included), that defines a set of *Sections*.
Each section is managed by a specific *handler* (for example, *[RSYNC]* section is
managed by *RsyncHandler*).
Each *Section* contains one or more *Subsections*, which are executed by the handler of the
parent Section, and contain the configuration for the handler.

The subsection configurations are handler specific, except for **depends** and **machines**:

 - **machines** defines the list of machine where the subsection should be executed;
 - **depends** defines the list of dependencies, that is used to decide the execution order.

ACID creates a list of subsections to execute in order to satisfy all the dependencies
declared in the configuration file, and execute the remote 

Let's clarify everything with an example.
## Example
```ini
machines = file:///home/antonio/machine-list.txt
[SCRIPT]
    [[INIT]]
    machine = %s(machines)s
    depends = RSYNC:HADOOP, RSYNC:HBASE
    script = /home/antonio/finalize.sh

[RSYNC]
    [[HADOOP]]
    machine = %s(machines)s
    source_dir = /home/antonio/hadoop-0.20.203.0/
    remote_dir = /home/hadoop/hadoop/
    
    [[HBASE]]
    machine = %s(machines)s
    depends = RSYNC:HADOOP
    source_dir = /home/antonio/hbase/
    remote_dir = /home/hadoop/hbase/
```
The example configuration file contains two *Sections*, **RSYNC** and **SCRIPT**.
**RSYNC** contains two subsections, each of them is passed to the *RsyncHandler* that (as 
it is presumable) copies the *source_dir* to the *remote_dir* on all the machines.

### Dependencies
**ACID** works like Ant or Make: each *subsection* corresponds to an Ant's target, and 
contains an option, **depends**, that lists the *Subsections* that have to be executed before it.

In the previous example, *RSYNC:HADOOP* is executed first, since it has no dependency; then 
it is executed *RSYNC:HBASE*, which depends on *RSYNC:HADOOP*. Last, it is executed *SCRIPT:INIT*,
which depends on both *RSYNC:HBASE* and *RSYNC:HADOOP*
    

## Quick start
-  Install all the dependencies:
   - `fabric` (get the latest version from github, which supports the parallel execution of tasks)
   - `networkx`

-  In order to run parallely, you need to create an ssh key and copy it on the remote machine.

```bash
   $ ssh-keygen
   $ ssh-copy-id -i ~/.ssh/ssh_key.pub user@remotehost
```

-  Create a configuration file (look at the example configuration)

-  Execute *acid.py*:

```bash
   $ python acid.py --config configuration.ini --all
```

-  In order to execute a specific subsection:

```bash
   $ python acid.py --config configuration.ini --subsection RSYNC:HADOOP_CONFIGURATION
```


## Handlers
For the time being there are only a few handlers:

 - `GitHandler`: clone a GIT project in a remote directory
 - `UserHandler`: create a user
 - `ScriptHandler`: execute a script on the remote hosts
 - `PackageHandler`: install a list of packages on the remote hosts
 - `RsyncHandler`: copy, using rsync, a local directory to a remote one

Defining a new handler is foolproof: just create a new class that inheriths from
`AbstractHandler` and define a *runtask* method. The *runtask* method is the task that is
executed on a remote host.

ACID uses *fabric* (http://fabfile.org/) in order to execute the remote tasks.


Contributing
------------

Contributions are extremely welcome, as are suggestions about how to structure,
package, and test the program. Feel free to send me an email or pull request
and I'll get back ASAP.