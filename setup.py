from setuptools import setup, find_packages


def contents(file_name):
    with open(file_name, encoding='UTF-8') as f:
        txt = f.read().strip()
    return txt


def contents_list(file_name):
    with open(file_name, encoding='UTF-8') as f:
        ls = list(map(str.rstrip, f.readlines()))
    return ls


VERSION = contents('VERSION')
long_description = contents('README.rst')

requirements = contents_list('requirements.txt')
requirements_test = contents_list('requirements.test.txt')

setup(
    name='apisports',
    url='https://github.com/MikeSmithEU/apisports/',
    version=VERSION,
    author='MikeSmithEU',
    author_email='projects@mikesmith.eu',
    descriptiona='Library for querying API-Sports.io',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'apisports': ['data/*.yaml']},
    install_requires=requirements,
    extras_require={
        'test': requirements_test,
    },
    platforms='any'
)
