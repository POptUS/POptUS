import os
import platform
import subprocess as sbp

import numpy as np


def get_python_environment():
    """
    .. todo::
        * Add in all other Python env vars?
        * Strip out information for packages installed in editable mode.  See if
          we can get the hash and clean/dirty status.
        * Other information?

    :return: Information related to the current Python environment that might be
        useful for recording along with data created with this environment
    """
    # ----- CREATE STRUCTURE & SET PYTHON INFO
    _, build_date = platform.python_build()

    env = {}
    env["Python"] = {
        "version": platform.python_version(),
        "compiler": platform.python_compiler(),
        "build": build_date
    }
    env["Packages"] = None
    env["EnvironmentVariables"] = {}

    # ----- GET LIST OF INSTALLED PACKAGES & SANITY CHECK
    result = sbp.run(["pip", "list"], shell=False, check=True,
                     capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("Unable to obtain list of packages with 'pip list'")

    lines_all = [e for e in result.stdout.decode().split("\n") if e != ""]

    header = lines_all[0].split()
    if not {"Package", "Version"}.issubset(set(header)):
        raise RuntimeError(f"Invalid pip list header ({header})")
    package = header[0].lower().strip()
    version = header[1].lower().strip()
    if (package != "package") or (version != "version"):
        raise RuntimeError(f"Invalid pip list header ({header})")

    divider = lines_all[1].split()
    if len(divider) < 2:
        raise RuntimeError(f"Invalid pip list divider ({divider})")
    for each in divider:
        unique = list(set(each))
        if (len(unique) != 1) or (unique[0] != "-"):
            raise RuntimeError(f"Invalid pip list divider ({divider})")

    # ----- STORE PACKAGE INFORMATION FOR IMMEDIATE WRITING WITH HDF5
    packages_all = {}
    for line in lines_all[2:]:
        tmp = line.split()
        assert len(tmp) >= 2
        package = tmp[0].strip()
        assert package not in packages_all
        packages_all[package] = tmp[1].strip()

    packages_arr = np.array(sorted(packages_all.keys()), dtype="S")
    versions_arr = [packages_all[key.decode()] for key in packages_arr]
    versions_arr = np.array(versions_arr, dtype="S")
    dtype = [("package", packages_arr.dtype), ("version", versions_arr.dtype)]
    env["Packages"] = np.rec.fromarrays((packages_arr, versions_arr), dtype)

    # ----- STORE ALL PYTHON ENV VARS
    env_vars = ["PYTHONHOME", "PYTHONPATH"]
    for key in env_vars:
        value = os.environ[key] if key in os.environ else ""
        assert key not in env["EnvironmentVariables"]
        env["EnvironmentVariables"][key] = value

    return env
