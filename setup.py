from distutils.core import setup

setup(
    name="simple_slack_bot",
    packages=["simple_slack_bot"],  # this must be the same as the name above
    version="0.4.1",
    description="Simple Slack Bot makes writing your next Slack bot incredibly easy",
    long_description="Simple Slack Bot makes writing your next Slack bot incredibly easy. By factoring out common functionality all Slack Bots require, you can focus on writing your business logic by simply registering for Slack Events defined by the Slack API",
    author="Greg Hilston",
    author_email="Gregory.Hilston@gmail.com",
    url="https://github.com/GregHilston/Simple-Slack-Bot",  # use the URL to the github repo
    download_url="https://github.com/GregHilston/Simple-Slack-Bot/tarball/v0.4.0-alpha",
    keywords=["slack", "bot", "chat", "simple"],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        "slacker",
        "slacksocket",
        "pyyaml",
    ],
)
