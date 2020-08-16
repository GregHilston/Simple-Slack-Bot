from setuptools import setup
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple_slack_bot",
    packages=["simple_slack_bot"],  # this must be the same as the name above
    version="1.3.3",
    description="Simple Slack Bot makes writing your next Slack bot incredibly easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Greg Hilston",
    author_email="Gregory.Hilston@gmail.com",
    url="https://github.com/GregHilston/Simple-Slack-Bot",  # use the URL to the github repo
    download_url="https://github.com/GregHilston/Simple-Slack-Bot/tarball/v1.1.0",
    keywords=["slack", "bot", "chat", "simple"],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        "slacker==0.14.0",
        "slacksocket>=0.7,!=0.8,<=0.9",
        "pyyaml",
        "websocket-client==0.48", # required to define as our dependency has a dependency which broke backwards compatibility
    ],
)
