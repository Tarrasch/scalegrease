# Scalegrease

A tool chain for scheduling, load balancing, deploying, running, and debugging data processing jobs.

## DISCLAIMER

**This is alpha software, occasionally not working.**  We are experimenting with creating
a project as open source from scratch.  Beware that this project may radically change in
incompatible ways until 1.0 is released, and that the development will be driven by Spotify's
internal needs for the near future.


# Installation

First install the dependencies

```bash
sudo pip install -r requirements.txt
```

Then make sure your `$PYTHONPATH` is setup correctly

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
./bin/greaserun --help
```

## The binaries in `bin/` folder

Scalegrease has a set of binaries (programs) that have little in common. The
programs are bundled together mainly for convenience, but they also all relate
to the deploy process in one way or another.

### greaserun

This is the most common tool. It will:

  * Download jar from artifactory (unless you pass a local jar on file system).
  * Takes care of load balancing.
  * Persist logging for you in whatever way the scalegrease administrators think is suitable.
  * If you use the `luigi` runner, it will do decoupling.

Example usages:

```
greaserun --help
./bin/greaserun --help  # If you have not installed it, which is OK
greaserun --verbose --runner luigi ~/THE-JAR.jar -- \
  --module top_tracks_by_artist --task Example3TopTracksByArtistJob --date 2014-07-22
greaserun --config-file ~/scalegrease.json --runner shell testing.foor.fun:arash-stream-count:0.0.1-SNAPSHOT -- \
  echo 'Scalegrease downloads the jar for me to' {jar_path} ', nice huh?'
```

### greasewatch

You can use this to check if your cron files have been installed on a farm node.

```
$ ssh farmmachine.acme.net
$ ls /etc/cron.d/
< ... Lots of cron files starting with scalegrease__ ... >
$ greasewatch
cron-filename (artifact):
    0 * * * * acme-analytics-data greaserun --runner luigi <artifact_spec> <parameters>
```

### greaselaunch

Asynchronously push cron files.

**Note:** The scalegrease administrators might have set this up to be triggered
on code changes.  You probably don't need to run it yourself!

```
$ ls src/main/cron/*.cron
$ greaselaunch
```

### greasesnatch

Asynchronously fetch cron files to farm machine. So this should be run from
farm machine and as root.

**Note:** The scalegrease administrators might have cronned this on the fram
nodes already. You probably don't need to run it yourself!

```
$ ssh farmmachine.acme.net
$ sudo -u root greasesnatch
```

## The json config file

Check out `conf/scalegrease.json`. It has instantiable parameters for local
testing. For production machines, the config should be found in `/etc/scalegrease.json`.

```
export SCALEGREASE_ETC_CROND=/tmp/cron.d
mkdir -p /tmp/cron.d
./bin/greaserun --config-file ./conf/scalegrease.json ...
```
