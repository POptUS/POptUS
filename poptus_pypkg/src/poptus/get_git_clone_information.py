import os

import subprocess as sbp

from pathlib import Path


def get_git_clone_information(filename):
    """
    :return: String that contains relevant information regarding the commit and
        status of the git clone in which the given file lives.  A git clone is
        dirty if there are

            * modified files in the working tree or
            * staged files.

        Otherwise, it is clean.
    """
    fname = Path(filename).resolve()
    if not fname.is_file():
        raise ValueError(f'{fname} does not exist or is not a file')

    cwd = Path.cwd()
    os.chdir(fname.parent)

    # https://stackoverflow.com/questions/949314/
    #        how-to-retrieve-the-hash-for-the-current-commit-in-git
    cmd = ['git', 'rev-parse', '--short', 'HEAD']
    response = sbp.run(cmd, shell=False, check=True, capture_output=True)
    git_hash = response.stdout.decode().rstrip('\n')

    # https://stackoverflow.com/questions/3882838/
    #          whats-an-easy-way-to-detect-modified-files-in-a-git-workspace
    cmd = ['git', 'diff-index', '--quiet', 'HEAD']
    response = sbp.run(cmd, shell=False, check=False, capture_output=True)
    state = 'clean' if response.returncode == 0 else 'dirty'

    os.chdir(cwd)

    return f'{git_hash} ({state})'
