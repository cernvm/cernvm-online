from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        # Meta data
        name="CernVM-Online",
        version="1.2.2",
        author="CernVM",
        author_email="cernvm.administrator@cern.ch",
        description="CernVM Online portal",
        url="http://cernvm.cern.ch/",

        # Packages
        packages=find_packages(exclude=["tests"]),
        include_package_data=True,          # reads the MANIFEST.in file
        zip_safe=False,                     # does not produce the EGG file
        scripts=["bin/cvmo-manage"],

        # Dependencies
        install_requires=[
            "Django>=1.5.0",
            "MySQL-python>=1.2.0",
            "Pillow>=2.0.0",
            "PyCrypto>=2.6",
            "django-cors-headers>=0.10",
            "passlib>=1.6.0",
            "South>=0.8",
            "django-json-field>=0.5"
        ]
    )
