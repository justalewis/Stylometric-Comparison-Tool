# Deployment

The project ships with a `Dockerfile` and a `fly.toml` tuned for
Fly.io. This document covers initial provisioning, secrets, scaling,
region selection, and troubleshooting.

The same image can be run anywhere Docker runs — Fly is the default
because the live deployment uses it, but nothing in the container is
Fly-specific.

---

## Container image

`Dockerfile` produces a ~130 MB image based on `python:3.12-slim`. The
build steps:

1. Install `Flask`, `spacy`, `gunicorn`, `python-docx`, `pypdf` from
   `requirements.txt`.
2. Download the `en_core_web_sm` spaCy model.
3. Copy the application source.
4. Create a non-root `appuser` (UID 1000) and chown the working
   directory.
5. Run gunicorn as `appuser`:
   ```
   gunicorn --bind 0.0.0.0:8080 \
            --workers 1 --threads 2 --timeout 120 \
            --access-logfile - --error-logfile - \
            app:app
   ```

**Why one worker.** spaCy's resident model is large enough that loading
it in multiple workers would exceed the 512 MB machine. One worker
with two threads handles concurrent requests well enough for a tool
that processes one comparison at a time. To raise throughput, scale
horizontally (add machines) rather than vertically (add workers).

**Why `--timeout 120`.** Large texts (close to the 2 MB request limit)
can take 15–30 seconds to parse. The default 30-second gunicorn
timeout is too tight; 120 seconds is comfortably loose.

---

## Initial deploy to Fly

Prerequisites: a Fly account, `flyctl` installed, and `fly auth login`
already done.

```powershell
cd C:\Users\Justin\Desktop\Stylometric-Compare

# 1. Create the app shell (one-time).
fly apps create stylometric-compare

# 2. Stage the auth secret. --stage means "save it but don't deploy yet."
fly secrets set STYLOMETRIC_PASSWORD="<a-strong-password>" --app stylometric-compare --stage

# 3. (Optional) Override the default username "user".
fly secrets set STYLOMETRIC_USERNAME="justin" --app stylometric-compare --stage

# 4. Build the image, push to Fly's registry, launch the machine.
#    --ha=false provisions a single machine instead of the default HA pair.
fly deploy --app stylometric-compare --ha=false
```

After a successful deploy:

- The app is reachable at `https://<app-name>.fly.dev/`.
- HTTPS is enforced (HTTP redirects to HTTPS).
- A single shared-cpu-1x machine with 512 MB RAM is running in `sjc`.

### Region

`fly.toml` sets `primary_region = "sjc"` (San Jose). Fly has deprecated
the Seattle region (`sea`) and won't provision new resources there.
Other reasonable West Coast / North America options:

| Code | Location |
|---|---|
| `sjc` | San Jose, USA |
| `lax` | Los Angeles, USA |
| `phx` | Phoenix, USA |
| `den` | Denver, USA |
| `dfw` | Dallas, USA |
| `ord` | Chicago, USA |
| `iad` | Ashburn (Virginia), USA |
| `ewr` | Newark, USA |
| `yyz` | Toronto, Canada |

To move the app to a different region:

```powershell
# Edit fly.toml: primary_region = "lax"
fly deploy --app stylometric-compare --ha=false
```

The next deploy will create a new machine in the target region. To
remove the old one once the new one is healthy:

```powershell
fly machine list --app stylometric-compare
fly machine stop <old-machine-id> --app stylometric-compare
fly machine destroy <old-machine-id> --app stylometric-compare
```

---

## Configuration

### `fly.toml` highlights

```toml
app = "stylometric-compare"
primary_region = "sjc"

[env]
  PORT = "8080"

[http_service]
  internal_port      = 8080
  force_https        = true
  auto_stop_machines = "off"      # Always-on
  auto_start_machines = true
  min_machines_running = 1

  [[http_service.checks]]
    interval = "30s"
    timeout  = "5s"
    grace_period = "10s"
    method = "GET"
    path = "/healthz"

[[vm]]
  size       = "shared-cpu-1x"
  memory     = "512mb"
  cpu_kind   = "shared"
  cpus       = 1
```

**`auto_stop_machines = "off"`** keeps the machine warm. spaCy model
load is the slow path on cold start (1–3 seconds); always-on avoids
that latency for occasional users. Cost is roughly $5/month for the
machine.

To enable cost-saving auto-stop instead:

```toml
auto_stop_machines   = "stop"
min_machines_running = 0
```

The first request after idle pays a ~5–10 second cold-start tax.

### Health check

The Flask app exposes `/healthz`:

```python
@app.route("/healthz", methods=["GET"])
def healthz():
    return Response("ok", mimetype="text/plain")
```

`/healthz` is **excluded from the auth gate** so Fly's checks don't
need credentials. Verify after each deploy:

```powershell
curl -s -o NUL -w "%{http_code}`n" https://stylometric-compare.fly.dev/healthz
# → 200
```

---

## Secrets

The app refuses to serve unless `STYLOMETRIC_PASSWORD` is set. This is
deliberate: silent fallback to "no auth" would be a serious foot-gun
on a public URL.

```powershell
# List secrets (names only; values are not retrievable).
fly secrets list --app stylometric-compare

# Update a secret. By default this triggers a redeploy.
fly secrets set STYLOMETRIC_PASSWORD="<new-password>" --app stylometric-compare

# Stage a secret without redeploying.
fly secrets set STYLOMETRIC_PASSWORD="<new-password>" --app stylometric-compare --stage

# Apply staged secrets to running machines without rebuilding.
fly secrets deploy --app stylometric-compare

# Remove a secret.
fly secrets unset STYLOMETRIC_USERNAME --app stylometric-compare
```

Username defaults to `user` when `STYLOMETRIC_USERNAME` is unset.

---

## Shipping code changes

```powershell
# Make your edits, commit them.
git add -A
git commit -m "describe the change"
git push

# Build and deploy.
fly deploy --app stylometric-compare --ha=false
```

The deploy is incremental: layers up to `requirements.txt` are cached,
so code-only changes rebuild in seconds. Dependency changes invalidate
the deps layer and incur the full pip-install + spaCy-model download
again.

The rolling deploy keeps the previous machine running until the new
one passes health checks, then swaps. Zero downtime in practice.

---

## Operational commands

```powershell
# Machine state.
fly status --app stylometric-compare

# Tail logs (last few minutes, then follow).
fly logs --app stylometric-compare

# Run a one-off command in the container (e.g., debugging).
fly ssh console --app stylometric-compare

# Restart the app (graceful).
fly machine restart --app stylometric-compare

# Tear it all down.
fly apps destroy stylometric-compare
```

To pause without destroying:

```powershell
fly machine list --app stylometric-compare
fly machine stop <id> --app stylometric-compare
```

The app retains its DNS, IPs, and secrets. Bring it back with
`fly machine start <id>`.

---

## Resource sizing

The default 512 MB / shared-cpu-1x machine is comfortable for the
intended use case (one analyst submitting comparisons every few
minutes). Signs you should size up:

- Memory pressure warnings in `fly logs`.
- Gunicorn worker restarts under load.
- Sustained CPU saturation visible in `fly status`.

To resize:

```powershell
# Edit fly.toml [[vm]] block to memory = "1gb", then redeploy.
fly deploy --app stylometric-compare --ha=false
```

For sustained multi-user traffic, scale horizontally:

```powershell
fly scale count 2 --app stylometric-compare
```

This adds a second machine in the same region; Fly's edge round-robins
between them. Each machine is independent — the app is stateless, so
no coordination is needed.

---

## Troubleshooting

### "Region X is deprecated and cannot have new resources provisioned"

Some Fly regions are wound down over time. The error message lists an
alternate region. Edit `primary_region` in `fly.toml` and redeploy.
(That is exactly how this app ended up in `sjc` instead of `sea`.)

### "Server is missing STYLOMETRIC_PASSWORD; refusing to serve."

The secret hasn't been set or the deploy ran before the secret was
applied. Run:

```powershell
fly secrets list --app stylometric-compare
fly secrets set STYLOMETRIC_PASSWORD="..." --app stylometric-compare
```

### Cold-start latency

The first request after the machine starts loads the spaCy model and
can take 5–10 seconds. With `auto_stop_machines = "off"` this only
happens after a deploy or an explicit restart. If you've enabled
auto-stop and want to avoid cold starts, switch back to
`auto_stop_machines = "off"` and `min_machines_running = 1`.

### "Address already in use" locally

The dev server defaults to port 5050. If that port is in use:

```powershell
# Run on a different port:
$env:PORT="6000"
python -c "import app; app.app.run(port=6000)"
```

The production container is fixed to port 8080 (matched by
`fly.toml [http_service].internal_port`); don't change one without the
other.

### Failed gunicorn boot

`fly logs` will show the worker traceback. The most common causes:

- Missing spaCy model (only happens if the Dockerfile build was
  bypassed) — fix by rebuilding the image.
- `requirements.txt` declares a version that conflicts with the
  Python version — pin or relax the version, redeploy.

---

## Local Docker testing

Verify the production container locally before pushing to Fly:

```powershell
docker build -t stylometric-compare .
docker run --rm -p 8080:8080 -e STYLOMETRIC_PASSWORD=local stylometric-compare
```

Then `curl http://127.0.0.1:8080/healthz` should return `ok`, and
`curl -u user:local http://127.0.0.1:8080/` should return the form.
