import os, sys, re # --STRIP DURING BUILD
def register_vcs_handler(*args): # --STRIP DURING BUILD
    def nil(f): # --STRIP DURING BUILD
        return f # --STRIP DURING BUILD
    return nil # --STRIP DURING BUILD
def run_command(): pass # --STRIP DURING BUILD
class NotThisMethod(Exception): pass  # --STRIP DURING BUILD

@register_vcs_handler("git", "parse_lookup_file")
def git_parse_lookup_file(path):
    """Parse a versioneer lookup file.

    This file allows definition of branch specific data like virtual tags or
    custom styles to use for version rendering.
    """
    if not os.path.exists(path):
        return []

    import re
    lookup = []
    with open(path, "r") as f:
        for line in f:
            if '#' in line:
                line = line[:line.index("#")]
            line = line.strip()
            if not line:
                continue

            try:
                split_line = map(lambda x: x.strip(), line.split())
                if not len(split_line):
                    continue

                matcher = re.compile(split_line[0])

                if len(split_line) == 1:
                    entry = [matcher, None, None, None]
                elif len(split_line) == 2:
                    render = split_line[1]
                    entry = [matcher, render, None, None]
                elif len(split_line) == 3:
                    tag, ref_commit = split_line[1:]
                    entry = [matcher, None, tag, ref_commit]
                elif len(split_line) == 4:
                    tag, ref_commit, render = split_line[1:]
                    entry = [matcher, render, tag, ref_commit]
                else:
                    continue

                lookup.append(entry)
            except:
                break
    return lookup


@register_vcs_handler("git", "pieces_from_lookup")
def git_pieces_from_lookup(lookup, root, verbose, run_command=run_command):
    """Extract version information based on provided lookup data."""
    GITS = ["git"]
    if sys.platform == "win32":
        GITS = ["git.cmd", "git.exe"]

    stdout = run_command(GITS, ["rev-parse", "--abbrev-ref", "HEAD"],
                         cwd=root)
    if stdout is None:
        raise NotThisMethod("git rev-parse --abbrev-ref HEAD failed")

    current_branch = stdout.strip()
    for matcher, render, tag, ref_commit in lookup:
        if matcher.match(current_branch):
            if tag is None or ref_commit is None:
                raise NotThisMethod("tag or ref_commit is unset for "
                                    "this branch")

            stdout = run_command(GITS,
                                 ["rev-list", "%s..HEAD" % ref_commit,
                                  "--count"],
                                 cwd=root)
            if stdout is None:
                raise NotThisMethod("git rev-list %s..HEAD "
                                    "--count failed" % ref_commit)
            try:
                num_commits = int(stdout.strip())
            except ValueError:
                raise NotThisMethod("git rev-list %s..HEAD --count didn't "
                                    "return a valid number" % ref_commit)

            stdout = run_command(GITS,
                                 ["rev-parse", "--short", "HEAD"],
                                 cwd=root)
            if stdout is None:
                raise NotThisMethod("git describe rev-parse "
                                    "--short HEAD failed")
            short_hash = stdout.strip()

            stdout = run_command(GITS,
                                 ["describe", "--tags",
                                  "--dirty", "--always"],
                                 cwd=root)
            if stdout is None:
                raise NotThisMethod("git describe --tags --dirty "
                                    "--always failed")
            dirty = stdout.strip().endswith("-dirty")

            stdout = run_command(GITS, ["rev-parse", "HEAD"], cwd=root)
            if stdout is None:
                raise NotThisMethod("git rev-parse HEAD failed")
            full = stdout.strip()

            return {
                "long": full,
                "short": short_hash,
                "dirty": dirty,
                "branch": current_branch,
                "closest-tag": tag,
                "distance": num_commits,
                "error": None,
                "render": render
            }

    raise NotThisMethod("no matching lookup definition found")

