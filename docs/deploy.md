# Deploying your own copy to the internet

This guide walks through putting your own copy of the Stylometric
Comparison tool on the public internet, with its own URL like
`https://yourname-stylometric.fly.dev/`. It uses Fly.io, the same
service the official version runs on.

It's written for someone who's never deployed a web app before. If
you have, you might prefer the more compressed
[operations.md](operations.md), which is the maintenance guide.

You only need to do this if you want your *own* internet-hosted
copy — to share with colleagues, students, or readers, or to run
under your own URL. If you just want to use the tool on your own
computer, [install.md](install.md) is the right guide.

**Time:** about 15 minutes for first-time setup, then a few minutes
for each deploy.

**Cost:** roughly $5 a month if you keep the machine always-on
(this is the default setting), or essentially free if you let the
machine auto-stop when idle and only occasionally use it. Fly's
pricing is at <https://fly.io/docs/about/pricing/>.

---

## Before you start

You need:

- **The repo cloned and working on your own machine.** Follow
  [install.md](install.md) first if you haven't already. You don't
  technically need a working local install for the deploy itself,
  but you'll want the project folder on your computer so you can
  make changes and re-deploy.
- **A Fly.io account.** Sign up at <https://fly.io>. They'll ask for
  a credit card — even on the free tier, this is required. Resource
  usage from this tool is tiny.
- **The `fly` command-line tool** (called `flyctl`). Installation
  steps for each OS are below.

---

## Step 1 — Install flyctl

This is the program that talks to Fly from your terminal.

**macOS** (using Homebrew):
```
brew install flyctl
```

**Linux:**
```
curl -L https://fly.io/install.sh | sh
```

**Windows** (PowerShell):
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

After installation, check that it worked:

```
fly version
```

You should see a version number. If you get "command not found,"
close and reopen your terminal — the installer often updates your
PATH but the change doesn't apply until the next session.

For other installation methods, see
<https://fly.io/docs/hands-on/install-flyctl/>.

---

## Step 2 — Log in

```
fly auth login
```

This opens your browser. Sign in to Fly (or sign up if you haven't
yet). Once you're signed in there, come back to the terminal —
flyctl will detect the login automatically.

Confirm you're logged in:

```
fly auth whoami
```

It should print your Fly email address.

---

## Step 3 — Pick a name for your app

Fly app names are **globally unique**. The official version uses
`stylometric-compare`, which is taken. You need to pick something
else — your name, your institution, anything. The name becomes part
of your URL: `https://<your-name>.fly.dev/`.

Some examples:
- `lewis-stylometric` → <https://lewis-stylometric.fly.dev/>
- `acme-writing-tool` → <https://acme-writing-tool.fly.dev/>
- `prof-smith-style` → <https://prof-smith-style.fly.dev/>

Rules: lowercase letters, numbers, and hyphens only. 30 characters
max.

Once you've picked one, **open `fly.toml`** (in the root of the
project folder) and change the first line:

```toml
app = "stylometric-compare"
```

to:

```toml
app = "your-chosen-name"
```

Save the file.

---

## Step 4 — (Optional) Pick a region

`fly.toml` also has a `primary_region` line — by default it's
`"sjc"` (San Jose). Fly has data centers around the world; pick the
one closest to you or your users:

| Code | City |
|---|---|
| `sjc` | San Jose, USA |
| `lax` | Los Angeles, USA |
| `dfw` | Dallas, USA |
| `ord` | Chicago, USA |
| `iad` | Ashburn, Virginia, USA |
| `ewr` | Newark, USA |
| `yyz` | Toronto, Canada |
| `lhr` | London, UK |
| `fra` | Frankfurt, Germany |
| `nrt` | Tokyo, Japan |
| `syd` | Sydney, Australia |

The full list is at
<https://fly.io/docs/reference/regions/>. Pick one and edit
`fly.toml`:

```toml
primary_region = "your-region-code"
```

If you skip this step, the app deploys to San Jose. That's fine for
most cases.

---

## Step 5 — Create the app on Fly

From inside the project folder, run:

```
fly apps create your-chosen-name
```

(Use the name you picked in Step 3.) Fly will confirm with something
like:

```
New app created: your-chosen-name
```

If the name is taken, you'll get an error — just pick a different
name and try again. Remember to also update `fly.toml` to match.

This step doesn't deploy anything yet; it just reserves the name
and creates an empty app slot on Fly.

---

## Step 6 — Deploy

This is the big one. Run:

```
fly deploy --ha=false
```

The `--ha=false` flag tells Fly to create a single machine instead
of two (the default for "high availability"). For a personal tool,
one machine is plenty and costs half as much.

Behind the scenes, Fly is:

1. Reading the `Dockerfile` in the project.
2. Building a container image with Python, Flask, spaCy, and the
   project code.
3. Downloading the spaCy English model into the image.
4. Pushing the image to Fly's registry.
5. Starting a machine that runs the image.
6. Connecting it to a URL.

The first deploy takes 3–5 minutes. Most of that time is
downloading and installing dependencies. You'll see a lot of output
— progress bars, log lines from `pip install`, etc. That's all
normal.

When it finishes, you'll see something like:

```
Visit your newly deployed app at https://your-chosen-name.fly.dev/
```

Open that URL in your browser. You should see the Stylometric
Comparison form. Done.

---

## Updating your deployment

Whenever you change the code on your computer and want the live
site to reflect the change:

```
git add -A
git commit -m "describe what changed"
fly deploy --ha=false
```

You don't need to recreate the app — `fly deploy` just rebuilds the
image and updates the running machine. Subsequent deploys are
faster than the first one because Fly caches the dependency
installation step.

---

## Useful commands

Run these from inside the project folder. They all act on the app
named in `fly.toml`.

```
fly status                  # is the machine running? when did it last restart?
fly logs                    # tail recent log output
fly logs -i <machine-id>    # logs for a specific machine
fly ssh console             # open a shell inside the running container (for debugging)
fly machine list            # see all machines for this app
fly machine restart <id>    # restart one
fly apps destroy <name>     # delete the app entirely (be careful — irreversible)
```

---

## Optional: a custom domain

If you want your tool at `https://writing.yourdomain.com/` instead
of `https://your-chosen-name.fly.dev/`, you can set up a custom
domain.

Fly's full guide is at
<https://fly.io/docs/networking/custom-domain/>. The short version:

1. Tell Fly about the domain:
   ```
   fly certs create writing.yourdomain.com
   ```
2. Fly will tell you which DNS records to add. Add them at your
   domain registrar (Cloudflare, Namecheap, etc.).
3. Wait a few minutes for DNS to propagate, then check:
   ```
   fly certs list
   ```
   The status should change from "Awaiting configuration" to
   "Verified."

Once verified, your tool answers at both URLs.

---

## Optional: add a password back

The current code has no authentication — anyone with the URL can
use the tool. If you'd prefer a shared password gate (like the
official version had before going public), you can restore the auth
handler from git history.

The commit that removed it is `e53cfda` (May 2026). Either revert
that single change:

```
git revert e53cfda
```

…or copy the `@app.before_request` block from
[that commit](https://github.com/justalewis/Stylometric-Comparison-Tool/commit/e53cfda)
into your `app.py` by hand.

Then set the password as a Fly secret:

```
fly secrets set STYLOMETRIC_PASSWORD="a-strong-password"
```

…and redeploy:

```
fly deploy --ha=false
```

Visitors will now get a browser auth prompt. Username is `user` by
default; change it with `fly secrets set STYLOMETRIC_USERNAME="..."`.

---

## Stopping or removing your deployment

To **pause** the app temporarily (stops the machine, keeps
everything else):

```
fly machine list
fly machine stop <machine-id>
```

Start it again later with:

```
fly machine start <machine-id>
```

To **destroy** the app entirely (irreversible — wipes the app,
release the name, stop billing):

```
fly apps destroy your-chosen-name
```

---

## Cost expectations

The default configuration in `fly.toml` is:

- **One shared-cpu-1x machine with 512 MB RAM**, always running.
- Roughly **$5 per month** at current pricing. Fly's free
  allowance covers small amounts of compute and data transfer; if
  you're a light user the actual bill may be lower.

To make it cheaper, edit `fly.toml`:

```toml
[http_service]
  auto_stop_machines = "stop"      # was "off"
  min_machines_running = 0          # was 1
```

Then redeploy. The machine will shut down when there's no traffic,
costing essentially nothing, but the first request after idle will
take 5–10 seconds to spin up. For a tool used occasionally rather
than constantly, this is usually the right trade-off.

For exact pricing, see <https://fly.io/docs/about/pricing/>. You
can also check your current bill at any time:

```
fly billing show
```

---

## Common problems

### "Region X is deprecated and cannot have new resources provisioned"

Fly winds down regions over time. The error message will suggest an
alternative. Open `fly.toml`, change `primary_region` to the
suggested code, and run `fly deploy --ha=false` again.

### "App name is taken" or "App name not available"

Names are globally unique on Fly. Pick a different name and update
`fly.toml`.

### Deploy fails partway through

Run `fly logs` to see what happened. The most common issues:

- **Out of memory during build** — usually a temporary Fly issue;
  re-run `fly deploy --ha=false`.
- **`pip install` failure** — a dependency in `requirements.txt`
  failed to install. Check the specific package; you may need to
  pin a version.

### Site loads but the form doesn't submit

Check `fly logs`. The most common cause is a missing spaCy model,
which would mean the Dockerfile's model-download step failed.
Look for `python -m spacy download en_core_web_sm` errors in the
build output.

### URL shows "Connection refused" or "Application Error"

The machine isn't running. Try:

```
fly status            # see machine state
fly machine list      # find the machine ID
fly machine start <id>
```

If it keeps failing, `fly logs` should show why.

---

## Getting unstuck

- **Fly's docs:** <https://fly.io/docs/>
- **Fly's community forum:** <https://community.fly.io/>
- **Open an issue on this repo:**
  <https://github.com/justalewis/Stylometric-Comparison-Tool/issues>

For ongoing operations on a running deployment (scaling, logs
analysis, region migration), see [operations.md](operations.md).
