
def plus_or_dot(pieces):
    """Return a + if we don't already have one, else return a ."""
    if "+" in pieces.get("closest-tag", ""):
        return "."
    return "+"


def render_pep440(pieces):
    """Build up version string, with post-release "local version identifier".

    Our goal: TAG[+DISTANCE.gHEX[.dirty]] . Note that if you
    get a tagged build and then dirty it, you'll get TAG+0.gHEX.dirty

    Exceptions:
    1: no tags. git_describe was just HEX. 0+untagged.DISTANCE.gHEX[.dirty]
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"] or pieces["dirty"]:
            rendered += plus_or_dot(pieces)
            rendered += "%d.g%s" % (pieces["distance"], pieces["short"])
            if pieces["dirty"]:
                rendered += ".dirty"
    else:
        # exception #1
        rendered = "0+untagged.%d.g%s" % (pieces["distance"],
                                          pieces["short"])
        if pieces["dirty"]:
            rendered += ".dirty"
    return rendered


def render_pep440_tag(pieces):
    """TAG[[.postDISTANCE].dev0+gHEX] -- Just the tag if not dirty, else more info

    Useful for projects that want commit based tracking on some branches
    but have the master branch only report tags, to allow for commits that
    do not modify actual code (e.g. to .github/* or docs).

    Exceptions:
    1: no tags. 0.postDISTANCE[.dev0]+gHEX
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["dirty"]:
            rendered += ".post%d" % pieces["distance"]
            rendered += ".dev0"
            rendered += "+g%s" % pieces["short"]
    else:
        # exception #1
        rendered = "0.post%d" % pieces["distance"]
        if pieces["dirty"]:
            rendered += ".dev0"
        rendered += "+g%s" % pieces["short"]
    return rendered


def render_pep440_pre(pieces):
    """TAG[.post.devDISTANCE] -- No -dirty.

    Exceptions:
    1: no tags. 0.post.devDISTANCE
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"]:
            rendered += ".post.dev%d" % pieces["distance"]
    else:
        # exception #1
        rendered = "0.post.dev%d" % pieces["distance"]
    return rendered


def render_pep440_post(pieces):
    """TAG[.postDISTANCE[.dev0]+gHEX] .

    The ".dev0" means dirty. Note that .dev0 sorts backwards
    (a dirty tree will appear "older" than the corresponding clean one),
    but you shouldn't be releasing software with -dirty anyways.

    Exceptions:
    1: no tags. 0.postDISTANCE[.dev0]
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"] or pieces["dirty"]:
            rendered += ".post%d" % pieces["distance"]
            if pieces["dirty"]:
                rendered += ".dev0"
            rendered += plus_or_dot(pieces)
            rendered += "g%s" % pieces["short"]
    else:
        # exception #1
        rendered = "0.post%d" % pieces["distance"]
        if pieces["dirty"]:
            rendered += ".dev0"
        rendered += "+g%s" % pieces["short"]
    return rendered


def render_pep440_dev(pieces):
    """TAG[.devDISTANCE]+gHEX[.dirty] .

    Exceptions:
    1: no tags. 0.devDISTANCE+gHEX[.dirty]
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"]:
            rendered += ".dev%d" % pieces["distance"]
        rendered += plus_or_dot(pieces)
    else:
        # exception #1
        rendered = "0.dev%d" % pieces["distance"]
        rendered += "+"
    rendered += "g%s" % pieces["short"]
    if pieces["dirty"]:
        rendered += ".dirty"
    return rendered


def render_pep440_old(pieces):
    """TAG[.postDISTANCE[.dev0]] .

    The ".dev0" means dirty.

    Eexceptions:
    1: no tags. 0.postDISTANCE[.dev0]
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"] or pieces["dirty"]:
            rendered += ".post%d" % pieces["distance"]
            if pieces["dirty"]:
                rendered += ".dev0"
    else:
        # exception #1
        rendered = "0.post%d" % pieces["distance"]
        if pieces["dirty"]:
            rendered += ".dev0"
    return rendered


def render_git_describe(pieces):
    """TAG[-DISTANCE-gHEX][-dirty].

    Like 'git describe --tags --dirty --always'.

    Exceptions:
    1: no tags. HEX[-dirty]  (note: no 'g' prefix)
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        if pieces["distance"]:
            rendered += "-%d-g%s" % (pieces["distance"], pieces["short"])
    else:
        # exception #1
        rendered = pieces["short"]
    if pieces["dirty"]:
        rendered += "-dirty"
    return rendered


def render_git_describe_long(pieces):
    """TAG-DISTANCE-gHEX[-dirty].

    Like 'git describe --tags --dirty --always -long'.
    The distance/hash is unconditional.

    Exceptions:
    1: no tags. HEX[-dirty]  (note: no 'g' prefix)
    """
    if pieces["closest-tag"]:
        rendered = pieces["closest-tag"]
        rendered += "-%d-g%s" % (pieces["distance"], pieces["short"])
    else:
        # exception #1
        rendered = pieces["short"]
    if pieces["dirty"]:
        rendered += "-dirty"
    return rendered


def render(pieces, style):
    """Render the given version pieces into the requested style."""
    if pieces["error"]:
        return {"version": "unknown",
                "full-revisionid": pieces.get("long"),
                "dirty": None,
                "error": pieces["error"]}

    if "render" in pieces and pieces["render"] is not None:
        style = pieces["render"]

    if not style or style == "default":
        style = "pep440"  # the default

    if style == "pep440":
        rendered = render_pep440(pieces)
    elif style == "pep440-pre":
        rendered = render_pep440_pre(pieces)
    elif style == "pep440-post":
        rendered = render_pep440_post(pieces)
    elif style == "pep440-old":
        rendered = render_pep440_old(pieces)
    elif style == "pep440-dev":
        rendered = render_pep440_dev(pieces)
    elif style == "pep440-tag":
        rendered = render_pep440_tag(pieces)
    elif style == "git-describe":
        rendered = render_git_describe(pieces)
    elif style == "git-describe-long":
        rendered = render_git_describe_long(pieces)
    else:
        raise ValueError("unknown style '%s'" % style)

    result = {"version": rendered, "full-revisionid": pieces["long"],
              "dirty": pieces["dirty"], "error": None}
    if "branch" in pieces and pieces["branch"] is not None:
        result["branch"] = pieces["branch"]
    return result

