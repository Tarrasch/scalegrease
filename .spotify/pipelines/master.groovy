// This file contains build specifications for Spotify internal CI/CD pipeline.  It can be safely
// ignored.

@Grab(group='com.spotify', module='pipeline-conventions', version='1.0.2')
import com.spotify.pipeline.Pipeline

new Pipeline(this) {{ build {
  group(name: 'Test') {
    shell.run(cmd: 'nosetests -v')
  }
  debian.pipelineVersionFromDebianChangelog()
  group(name: 'Build & Upload squeeze') {
    sbuild.build(distro: 'unstable', release: 'squeeze')
    debian.upload(distro: 'unstable', release: 'squeeze')
    debian.upload(distro: 'stable', release: 'squeeze')
  }
  group(name: 'Build & Upload trusty') {
    sbuild.build(distro: 'unstable', release: 'trusty')
    debian.upload(distro: 'unstable', release: 'trusty')
    debian.upload(distro: 'stable', release: 'trusty')
  }
}}}

