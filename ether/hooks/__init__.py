"""Module __init__."""

class EtherHookError(Exception):
    """Custom exception."""
    pass

def get_repo_url(paths, config):
    """
    Get repo url from the list of paths.
    :param paths: list of changed paths
    :ptype paths: list
    :param config: configuration object which maps repository paths to urls
    :ptype config: list of tuples (<path>, <url>)
    :returns: repository url
    :rtype: string
    """

    result = None
    for path in paths:
        for upath, url in config:
            if path.startswith(upath):
                if result and result != url:
                    raise EtherHookError("get_repo_url got 2 different results: "
                                        "%s and %s" % (result, url))
                if not result:
                    result = url
                break
    if not result:
        raise EtherHookError("get_repo_url: Can't get repo url from %s" \
                           % str(paths))
    return result
