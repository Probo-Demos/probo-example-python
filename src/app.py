"""Probo environment demo — Flask edition.

Displays the environment variables a Probo CI build injects into a container,
split into a documented "build variables" catalog and everything else injected
(secrets and custom variables). Converted from the original PHP page.

Run locally:
    python app.py                # dev server on http://0.0.0.0:8000
Or, as Probo's proposed Python plugin would:
    gunicorn --bind 127.0.0.1:8000 app:app
"""

import datetime
import os
import platform
import sys

from flask import Flask, render_template

import probo_env

app = Flask(__name__)


@app.route("/")
def index():
    build_vars, other_vars = probo_env.snapshot()
    version = sys.version_info

    return render_template(
        "index.html",
        build_vars=build_vars,
        other_vars=other_vars,
        in_probo=os.environ.get("PROBO_ENVIRONMENT") == "TRUE",
        py_version="{0}.{1}.{2}".format(version.major, version.minor, version.micro),
        py_major_minor="{0}.{1}".format(version.major, version.minor),
        py_full="{0} ({1})".format(platform.python_version(), platform.python_implementation()),
        year=datetime.datetime.now().year,
    )


if __name__ == "__main__":
    # nginx in the Probo container reverse-proxies to 127.0.0.1:8000; binding
    # 0.0.0.0 covers that and local access. Override with PORT if needed.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
