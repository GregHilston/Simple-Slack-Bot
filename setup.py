import os
import subprocess
import sys

from os import path

from setuptools import setup
from setuptools.command.install import install


VERSION = "2.0.2"
VERSION_WITH_LEADING_V = f"v{VERSION}"


def readme_to_string() -> str:
    """read the contents of the README file"""
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
        return f.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        self.create_matching_git_tag()
        latest_git_tag = subprocess.run(['git', 'describe', '--abbrev=0', '--tags'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").rstrip('\n')

        if latest_git_tag != VERSION_WITH_LEADING_V:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                latest_git_tag, VERSION_WITH_LEADING_V
            )
            sys.exit(info)

    def create_matching_git_tag(self):
        subprocess.run(["git", "tag", VERSION_WITH_LEADING_V])
        subprocess.run(["git", "push", "--tags"])


setup(
    name="simple_slack_bot",
    packages=["simple_slack_bot"],  # this must be the same as the name above
    version=VERSION,
    description="Simple Slack Bot makes writing your next Slack bot incredibly easy",
    long_description=readme_to_string(),
    long_description_content_type="text/markdown",
    author="Greg Hilston",
    author_email="Gregory.Hilston@gmail.com",
    license="MIT",
    url="https://github.com/GregHilston/Simple-Slack-Bot",  # use the URL to the github repo
    download_url=f"https://github.com/GregHilston/Simple-Slack-Bot/tarball/v{VERSION}",
    keywords=["slack", "bot", "chat", "simple"],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        "slacker==0.14.0",
        "slacksocket>=0.7,!=0.8,<=0.9",
        "slackclient==2.8.0",
        "pyyaml",
        "wheel",
        "websocket-client==0.48",  # required to define as our dependency has a dependency which broke backwards compatibility
    ],
    python_requires='>=3.7',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
