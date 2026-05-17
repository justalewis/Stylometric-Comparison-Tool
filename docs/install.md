# Installing the tool on your computer

This guide gets the Stylometric Comparison tool running on your own
machine so you can use it locally — no internet hosting required.
It's written for someone who has used a command line before but
hasn't necessarily installed a Python web app from a repository.

If you'd rather skip the install and use the version Justin hosts,
go to <https://stylometric-compare.fly.dev/>. If you want your *own*
public copy on the internet, see [deploy.md](deploy.md) after you've
finished this guide.

The whole install takes about five minutes once Python and Git are
in place.

---

## Before you start

You need three things on your computer:

- **Python 3.10 or newer** (3.12 is what the project is tested
  against). Check by running:

  ```
  python --version
  ```

  If you see something like `Python 3.12.5`, you're set. If you get
  "command not found" or a version older than 3.10, download from
  <https://www.python.org/downloads/>. On Windows, **check the box
  that says "Add Python to PATH"** during installation.

- **pip**, which usually comes with Python. Verify with:

  ```
  pip --version
  ```

- **Git.** Verify with:

  ```
  git --version
  ```

  If you don't have it, download from <https://git-scm.com/downloads>.

You don't need to know Python or Flask or spaCy to follow this guide.
You're just running a few commands.

---

## Step 1 — Get the code

Pick a folder where you keep projects (anywhere is fine — Desktop,
Documents, a `projects` folder) and run:

```
git clone https://github.com/justalewis/Stylometric-Comparison-Tool.git
cd Stylometric-Comparison-Tool
```

You now have a folder called `Stylometric-Comparison-Tool` with the
project inside. Every command from here on should be run from inside
that folder.

---

## Step 2 — Make a virtual environment

This is a one-time setup step. A "virtual environment" is just a
self-contained folder that holds the project's Python libraries, so
they don't conflict with anything else on your system. It's the
standard way to run Python projects.

```
python -m venv .venv
```

That creates a folder called `.venv` inside the project. Nothing
else changes.

Now **activate** the virtual environment. The command is different
for each operating system:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```
source .venv/bin/activate
```

After activation, your prompt should show `(.venv)` at the start.
That means the virtual environment is on, and any `pip install`
commands will install into it, not into your global Python.

Every time you come back to work on this project, you'll activate
the venv again. You don't need to recreate it.

> **Windows note:** If PowerShell refuses to run the activation
> script with a message about execution policy, run this once in
> PowerShell to allow scripts for your user account:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## Step 3 — Install the project's dependencies

With the venv active, run:

```
pip install -r requirements.txt
```

This downloads and installs Flask, spaCy, gunicorn, python-docx, and
pypdf — the libraries the tool uses. It usually takes 30–90 seconds.
You'll see a lot of output; that's normal.

---

## Step 4 — Download the spaCy English model

spaCy is the library the tool uses to understand sentence structure,
parts of speech, and so on. It needs an English model file, which is
about 12 MB:

```
python -m spacy download en_core_web_sm
```

You only do this once. If you ever upgrade Python or recreate the
virtual environment, you'd run it again.

---

## Step 5 — Start the server

```
python app.py
```

You'll see output that ends with something like:

```
 * Running on http://127.0.0.1:5050
 * Debugger is active!
```

That means the server is running. Open your web browser and go to:

```
http://127.0.0.1:5050
```

You should see the Stylometric Comparison form. Paste two writing
samples, click *Run comparison*, and you've got it.

To stop the server, go back to the terminal where it's running and
press **Ctrl + C**.

---

## Coming back later

Once everything's installed, the workflow each time you want to use
the tool is just:

1. Open a terminal, `cd` into the project folder.
2. Activate the virtual environment (the command from Step 2 above).
3. Run `python app.py`.
4. Open the browser to <http://127.0.0.1:5050>.

You don't need to redo the install steps. The `.venv` folder
remembers everything.

To get updates from the GitHub repository:

```
git pull
pip install -r requirements.txt   # in case dependencies changed
```

---

## Common problems

### "Port 5050 is already in use"

Something else on your computer is using that port — maybe another
copy of the tool you forgot you started. Either close the other
thing, or change the port. To use a different port, edit the very
last line of `app.py`:

```python
app.run(host="127.0.0.1", port=5050, debug=True)
```

Change `5050` to something else, like `5051`. Save the file and run
`python app.py` again.

### "ModuleNotFoundError: No module named 'spacy'" (or 'flask', etc.)

You're not in the virtual environment. Check that your prompt shows
`(.venv)` at the start. If it doesn't, run the activation command
from Step 2.

### "Can't find model 'en_core_web_sm'"

You skipped Step 4 or it didn't finish. Run:

```
python -m spacy download en_core_web_sm
```

### "Command not found: python" or "python: command not found"

Python isn't on your PATH. On Mac and Linux, try `python3` instead
of `python`. On Windows, reinstall Python from
<https://www.python.org/downloads/> and **check the "Add Python to
PATH" box** during installation.

### The form loads but submitting doesn't work

Look at the terminal where you ran `python app.py`. If something
broke, the error will appear there. The most common issue is the
spaCy model not being installed (see above).

### Opening the URL goes to a different page

If `http://127.0.0.1:5050` shows a different app, you have another
service on that port. Try `http://localhost:5050` first; if it still
shows the wrong thing, change the port as described above.

---

## What's next

- **Use the tool.** The form is at the URL above. The glossary at
  `/glossary` walks through every metric with examples.
- **Read the pedagogical framing** at [pedagogy.md](pedagogy.md) if
  you plan to use this with students.
- **Deploy it to the internet** (so it has its own URL anyone can
  reach) by following [deploy.md](deploy.md). That's optional — if
  you just want to use the tool yourself, running it locally is
  perfectly fine.
- **Customize.** The word lists live in
  [`analyzer/wordlists.py`](../analyzer/wordlists.py). The glossary
  definitions live in
  [`analyzer/glossary.py`](../analyzer/glossary.py). You can edit
  either without breaking the rest of the tool.

If you hit a problem this guide doesn't cover, open an issue at
<https://github.com/justalewis/Stylometric-Comparison-Tool/issues>.
