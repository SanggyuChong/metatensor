import os
import subprocess
import sys
import uuid

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg


ROOT = os.path.realpath(os.path.dirname(__file__))
EQUISTORE_CORE = os.path.realpath(os.path.join(ROOT, "..", "equistore-core"))


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install performing setuptools' default easy_install,
    which it should never ever do.
    """

    def run(self):
        sys.exit(
            "Aborting implicit building of eggs. "
            + "Use `pip install .` or `python setup.py bdist_wheel && pip "
            + "uninstall equistore -y && pip install dist/equistore-*.whl` "
            + "to install from source."
        )


def git_extra_version():
    """
    If git is available, it is used to check if we are installing a development
    version or a released version (by checking how many commits happened since
    the last tag).
    """

    # Add pre-release info the version
    try:
        tags_list = subprocess.run(
            ["git", "tag"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
        )
        tags_list = tags_list.stdout.decode("utf8").strip()

        if tags_list == "":
            first_commit = subprocess.run(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                check=True,
            )
            reference = first_commit.stdout.decode("utf8").strip()

        else:
            last_tag = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                check=True,
            )

            reference = last_tag.stdout.decode("utf8").strip()

    except Exception:
        reference = ""
        pass

    try:
        n_commits_since_tag = subprocess.run(
            ["git", "rev-list", f"{reference}..HEAD", "--count"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
        )
        n_commits_since_tag = n_commits_since_tag.stdout.decode("utf8").strip()

        if n_commits_since_tag != 0:
            return ".dev" + n_commits_since_tag
    except Exception:
        pass

    return ""


if __name__ == "__main__":
    with open(os.path.join(ROOT, "AUTHORS")) as fd:
        authors = fd.read().splitlines()

    if authors[0].startswith(".."):
        # handle "raw" symlink files (on Windows or from full repo tarball)
        with open(os.path.join(ROOT, authors[0])) as fd:
            authors = fd.read().splitlines()

    version = "0.1.0" + git_extra_version()

    install_requires = []
    if os.path.exists(EQUISTORE_CORE):
        # we are building from a git checkout or full repo archive

        # add a random uuid to the file url to prevent pip from using a cached
        # wheel for equistore-core, and force it to re-build from scratch
        uuid = uuid.uuid4()
        install_requires.append(f"equistore-core @ file://{EQUISTORE_CORE}?{uuid}")
    else:
        # we are building from a sdist/installing from a wheel
        install_requires.append("equistore-core ==0.1.0")

    setup(
        version=version,
        author=", ".join(authors),
        install_requires=install_requires,
        cmdclass={
            "bdist_egg": bdist_egg if "bdist_egg" in sys.argv else bdist_egg_disabled,
        },
    )