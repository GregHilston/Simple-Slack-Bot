from distutils.core import setup


setup(
    name = "simple_slack_bot",
    packages = ["simple_slack_bot"], # this must be the same as the name above
    version = "0.1",
    description = "Simple Slack Bot makes writing your next Slack bot incredibly easy. By factoring out common functionality all Slack Bots require, you can focus on writing your business logic.",
    author = "Greg Hilston",
    author_email = "Gregory.Hilston@gmail.com",
    url = "https://github.com/GregHilston/Simple-Slack-Bot", # use the URL to the github repo
    download_url = "https://github.com/GregHilston/Simple-Slack-Bot/tarball/0.1",
    keywords = ["slack", "bot", "chat", "simple"], # arbitrary keywords
    classifiers = [],
)
