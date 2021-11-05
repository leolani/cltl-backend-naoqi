from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name='cltl.backend-naoqi',
    version=version,
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*'], where='src'),
    data_files=[('VERSION', ['VERSION'])],
    url="https://github.com/leolani/cltl-backend-naoqi",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='NaoQI Backend for Pepper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='==2.7.10',
    install_requires=[]
)

