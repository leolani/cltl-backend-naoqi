from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name='cltl.backend-naoqi',
    version=version,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    data_files=[('VERSION', ['VERSION'])],
    url="https://github.com/leolani/cltl-backend-naoqi",
    license='MIT License',
    author='CLTL',
    author_email='t.baier@vu.nl',
    description='Backend for Pepper robot',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=2.7.0,<=3.0.0',
    install_requires=["numpy",
                      "flask",
                      "click",
                      "enum34",
                      "jinja2",
                      "flask",
                      "MarkupSafe",
                      "itsdangerous"
                      ]
)
