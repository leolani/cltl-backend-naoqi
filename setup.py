from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cltl.template',
    version='0.0.dev1',
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*']),
    url="https://github.com/leolani/cltl-demo",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Template Communication Robot Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    install_requires=['cltl.combot'],
)
