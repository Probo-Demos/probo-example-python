"""Reads the container environment the way a Probo build sees it.

The original PHP page ran behind Apache + mod_php, so it mirrored the filter in
probo-ubuntu/<image>/files/envvars-swap.sh. A Python app (like the .NET one)
runs as its own process behind an nginx reverse proxy, so it simply inherits the
container environment; there is no Apache filter to mirror. To keep the page
meaningful we instead drop the Python/system runtime noise so only the variables
Probo actually injected remain visible.
"""

import os

# Documented Probo build variables. Any of these present in the environment are
# shown (described) in the first table, in this order.
KNOWN_DESCRIPTIONS = [
    ("PROBO_ENVIRONMENT", "Set to <code>TRUE</code> when running inside a Probo build container."),
    ("BUILD_ID", "Unique identifier for the current build."),
    ("BUILD_DOMAIN", "Domain where this build's site is accessible."),
    ("BRANCH_NAME", "Name of the git branch being built."),
    ("BRANCH_LINK", "URL to the branch on the VCS provider (GitHub, Bitbucket, etc.)."),
    ("COMMIT_REF", "Full commit hash/reference being built."),
    ("COMMIT_LINK", "URL to the commit on the VCS provider."),
    ("PULL_REQUEST_NAME", "Title of the pull request that triggered this build."),
    ("PULL_REQUEST_LINK", "URL to the pull request on the VCS provider."),
    ("SRC_DIR", "Path to the source code directory inside the container."),
    ("ASSET_DIR", "Path to the assets directory inside the container."),
]

# Exact names that are container/shell/runtime plumbing rather than build input.
_EXACT_EXCLUDE = {
    "HOME", "PATH", "PWD", "OLDPWD", "SHLVL", "TERM", "LANG", "LANGUAGE",
    "LC_ALL", "LS_COLORS", "HOSTNAME", "USER", "LOGNAME", "MAIL", "SHELL",
    "_", "DEBIAN_FRONTEND", "GATEWAY_INTERFACE", "SERVER_SOFTWARE", "PS1",
    "VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "PYTHONUNBUFFERED",
    "PYTHONDONTWRITEBYTECODE",
}

# Name prefixes owned by the runtime/toolchain.
_PREFIX_EXCLUDE = ("APACHE_", "GUNICORN_", "WERKZEUG_", "NVM_", "SUDO_", "XDG_", "LC_")


def visible_environment():
    """Return the injected environment, name-sorted, with runtime noise removed."""
    visible = {}
    for name, value in os.environ.items():
        if name in _EXACT_EXCLUDE:
            continue
        if any(name.startswith(prefix) for prefix in _PREFIX_EXCLUDE):
            continue
        visible[name] = value
    return dict(sorted(visible.items()))


def snapshot():
    """Partition the visible environment into the documented build-variable
    catalog and everything else Probo injected (secrets and custom vars).

    Returns a (build_vars, other_vars) tuple of lists of dicts.
    """
    visible = visible_environment()

    # First table: the documented catalog, in catalog order, so the page still
    # documents the full set with live values where present.
    build_vars = []
    for name, description in KNOWN_DESCRIPTIONS:
        present = name in visible
        build_vars.append({
            "name": name,
            "value": visible.get(name),
            "present": present,
            "description": description,
        })
        visible.pop(name, None)

    # Second table: everything else — organization/project secrets and any
    # custom variables. Discovered dynamically; there is no fixed list.
    other_vars = [{"name": name, "value": value} for name, value in sorted(visible.items())]

    return build_vars, other_vars
