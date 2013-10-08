from distutils.core import setup

setup(
    name = "CernVM Online",
    version = "1.0",
    author = "CernVM",
    author_email = "cernvm.administrator@cern.ch",
    packages = ["cvmo"],
    scripts = ["manage.py"],
    description = "CernVM Online portal",
    long_description = open("README.txt").read(),
    requires = [
        "django (>=1.5.0)",
        "PIL",
        "Crypto (>=2.6)",
        "corsheaders",
        "Random"
    ]
)
