import platform


def get_platform_information():
    """
    .. todo::
        * How to get platform name?  What about clusters, etc.?
        * Does this need to be handled in an OS-specific way?  For example,
          there might be extra information available for macOS.

    :return: Information related to platform that might be useful for recording
        along with data created on this platform
    """
    return {
        "Machine": platform.machine(),
        "OS": platform.system(),
        "OSVersion": platform.release(),
        "Platform": platform.platform(),
        "PlatformVersion": platform.version()
    }
