from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version.txt", "r") as fh:
    version = fh.read()

setup(
    name='cltl.demo-component',
    version=version,
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*']),
    package_data={'': ['version.txt']},
    include_package_data=True,
    url="https://github.com/leolani/cltl-demo",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Demo component for Communication Robot Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    install_requires=['cltl.combot'],
)
