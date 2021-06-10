from setuptools import setup, find_packages

with open('VERSION') as f:
    VERSION = f.read().strip()

with open('README.rst') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = list(map(str.rstrip, f.readlines()))

with open('requirements.test.txt') as f:
    requirements_test = list(map(str.rstrip, f.readlines()))

setup(
    name='apisports',
    url='https://github.com/MikeSmithEU/apisports/',
    version=VERSION,
    author='MikeSmithEU',
    author_email='projects@mikesmith.eu',
    descriptiona='Library for querying APISports.io',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.4',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'apisports': ['data/*.yaml']},
    install_requires=requirements,
    extras_require={
        'test': requirements_test,
    },
    platforms='any'
)
