Scalegrease
===========

A tool chain for scheduling, load balancing, deploying, running, and debugging data processing jobs.

DISCLAIMER
----------

**This is alpha software, occasionally not working.**  We are experimenting with creating
a project as open source from scratch.  Beware that this project may radically change in
incompatible ways until 1.0 is released, and that the development will be driven by Spotify's
internal needs for the near future.


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
