# rock-vs-docker

One tiny Flask + SQLite notes API, packaged three ways, then measured: image size, the user it runs as, and known vulnerabilities (Trivy 0.75, scanned 2026-10-14).

| Build | How | Size | Runs as | CVEs (crit / high / total) |
|---|---|---|---|---|
| `Dockerfile.basic` | `python:3.12`, single stage | 1.12 GB | root | 16 / 312 / 3,609 |
| `Dockerfile.hardened` | `python:3.12-slim`, multi-stage venv, non-root user, healthcheck | 137 MB | `app` | 0 / 44 / 179 |
| `rockcraft.yaml` | Rockcraft `flask-framework`, chiselled `bare` base, Pebble as entrypoint | 116 MB (49 MB `.rock` archive) | `_daemon_` | 0 / 29 / 80 |

## What I learned

- Switching the base image did most of the work: going from `python:3.12` to `-slim` removed about 95% of the CVEs before touching any app code.
- The chiselled rock has **zero OS package CVEs**. Every finding left is in software I chose to ship: the Flask/gunicorn pins (also present in the other two images) and two Go binaries the extension bundles, Pebble and a StatsD exporter (60 of the 80). So the next step is not the base image, it is keeping those bundled binaries current.
- The rock runs the app under Pebble, which also starts a metrics exporter and gives a service manager inside the container instead of a bare `CMD`.

## Run it

```bash
pytest -q                                   # app test
docker build -f Dockerfile.hardened -t notes:hardened .
rockcraft pack                              # needs LXD
rockcraft.skopeo --insecure-policy copy oci-archive:notes_0.1_amd64.rock docker-daemon:notes:rock
trivy image notes:rock
```

Note: my office network blocks DNS inside Docker builds, so the Dockerfiles install from a `wheels/` folder downloaded on the host (`pip download -r requirements.txt -d wheels`). On a normal network you can drop `--no-index --find-links`.
