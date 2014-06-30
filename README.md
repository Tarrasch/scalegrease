Scalegrease
===========

A tool chain for scheduling, load balancing, deploying, running, and debugging data processing jobs.

DISCLAIMER
----------

**This is alpha software, occasionally not working.**  We are experimenting with creating
a project as open source from scratch.  Beware that this project may radically change in
incompatible ways until 1.0 is released, and that the development will be driven by Spotify's
internal needs for the near future.


Goals
=====

Provide a batch job execution platform, where data pipeline developers easily can express when and
how jobs should be run, without needing to operate dedicated machines for scheduling and execution.

Design goals:

* Stable under load.  Job execution service must not fall over under heavy
  load, e.g. when recomputing or backfilling.
* Minimal developer effort to package, deploy, schedule, and debug a batch
  job.
* Jobs run on a homogeneous cluster of tightly normalised machines, with
  few dependencies on software installed on the machines.  Jobs are
  self-contained.
* Integrate well with an efficient CI/CD workflow.
* Simplify failure debugging, without requiring users to locate which
  machine ran a particular job.
* Last but most importantly, separate the different scopes, describe below
  as much in order to be able to change implementation without affecting
  users heavily.
* No single point of failure.



Scopes
======

Running a batch computation involves multiple steps and considerations.  For the first iteration,
we will address the deployment, execution, and debug scopes, described below.  For the other 
scopes, we will use existing (Spotify) infrastructure, e.g. crontabs and Luigi, for the near future.
Regarding Luigi, it has a rich set of functionality, and parts of it will likely be used, at least
for the foreseeable future.


Dispatch
--------

A job can be dispatched in multiple ways:

* Manually.  A developer or analyst runs a one-off job.
* Scheduled.  Production jobs that run at regular intervals.
* Induced.  Production jobs that depend on input data sets, and run when
  the inputs are available.

Note that Luigi performs induced dispatch for multiple tasks packaged
together in a single module.  Such a sequence of tasks is regarded as a
single job from a scalegrease point of view.

Many jobs are parameterised, e.g. on date.  The dispatch mechanism or the
execution mechanism should fill in the dynamic parameters.


Arbitration
-----------

Jobs need resources.  Resources should not be overallocated.  In times of
excessive load, drop jobs rather than overcommit resources.  

An arbiter typically keeps a queue of dispatched jobs, which are pulled or
pushed to workers capable of taking another job.


Deployment
----------

Getting the job implementation to the worker machine.  Avoid stateful
technologies, such as Debian packages and Puppet.



Execution
---------

Running the job, with the right runner script.

There will be cases for multiple types of runners:

* ShellRunner: Run a single shell script, shipped with the jar.
* HadoopRunner: Run with 'hadoop jar'.
* LuigiRunner: Unpack a Luigi job specification and use Luigi to execute it.


Debugging
---------

Collect the relevant execution tracing information, aka logs, to enable
debugging job failures.


Development
===========

Requirements for development
----------------------------

```bash
sudo pip install -r requirements.txt
```

Test running locally
--------------------

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
# Look in conf/scalegrease.json, and set the desired variables for local interactive testing
export SCALEGREASE_ETC_CROND=/tmp/cron.d
mkdir -p /tmp/cron.d
./bin/greaserun --help
```

Roadmap
=======

Iteration 1
-----------

Manual and scheduled dispatch are supported.  For manual dispatch, use greaserun, which dynamically 
downloads a specified fat jar and executes a 
compute job contained therein.  It also supports running a job contained in a jar stored on the 
local file system.

Scheduled dispatch is supported in a primitive manner, with
crontab lines on redundant scheduling machines.  In order to distribute crontabs to a farm, 
use greaselaunch, which distributes all crontabs found in the project to a central location.  
Farm worker machines periodically call the script greasesnatch, which copies crontab files to 
/etc/cron.d.   

The crontabs typically contain greaserun commands, which ensures that the fat job jars are 
dynamically deployed.  Job jars should contain Luigi job DSL files, 
and be executed with the greaserun Luigi runner.  The Luigi central scheduler ensures 
that no duplicate jobs are executed.

As a poor man's arbitration, greaserun will be complemented with a simple overload guard.  It 
runs jobs only if the machine load complies with constraints, expressed e.g. in terms of loadavg,
number of greaserun processes, etc.

Logs are generated/copied to a common log directory, which should live on
shared storage, e.g. an NFS mount.


Iteration 2
-----------

A Jenkins job DSL specification ensures that greaselaunch is called, automatically scheduling 
jobs after new code is pushed to the source code repository. 

A scheduling system dispatches jobs it to the arbitration stage.  Possible
technologies:  Chronos, Azkaban, Aurora.

Depending on scheduling technology, it may also provide induced dispatch,
and sophisticated arbitration, e.g. with strong resource allocation and
isolation.  Possible technologies: Mesos, simpler ZK job queue without
deduplication.
