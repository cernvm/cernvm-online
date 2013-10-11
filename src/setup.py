import os
from setuptools import setup

#
# Helpers
#

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def is_package(package_name, exclude):
    for pkg in exclude:
        if package_name.startswith(pkg):
            return False
    return True

def compile_packages_list(base_dir="cvmo", exclude=[]):
    """
    Compile the list of packages available, because distutils doesn't have
    an easy way to do this.
    """
    packages, package_data = [], {}
    root_dir = os.path.dirname(__file__)
    if root_dir != '':
        os.chdir(root_dir)
    for dirpath, dirnames, filenames in os.walk(base_dir):
        # Ignore PEP 3147 cache dirs and those whose names start with '.'
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
        parts = fullsplit(dirpath)
        package_name = '.'.join(parts)
        if '__init__.py' in filenames and is_package(package_name, exclude):
            packages.append(package_name)
        elif filenames:
            relative_path = []
            while '.'.join(parts) not in packages:
                relative_path.append(parts.pop())
            relative_path.reverse()
            path = os.path.join(*relative_path)
            package_files = package_data.setdefault('.'.join(parts), [])
            package_files.extend([os.path.join(path, f) for f in filenames])
    return packages, package_data


if __name__ == "__main__":
    # Compile the packages list
    packages, package_data = compile_packages_list()

    # Invoke setup
    setup(
        # Meta data
        name = "CernVM-Online",
        version = "1.0",
        author = "CernVM",
        author_email = "cernvm.administrator@cern.ch",
        description = "CernVM Online portal",
        url = "http://cernvm.cern.ch/",
        long_description = open("README.txt").read(),

        # Packages, modules and scripts
        packages = packages,
        package_data = package_data,
        scripts = ["manage.py"],

        # Dependencies
        install_requires = [
            "Django>=1.5.0",
            "PIL",
            "PyCrypto>=2.6",
            "django-cors-headers"
        ]
    )
