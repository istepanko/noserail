from setuptools import find_packages, setup

setup(
    name='noserail',
    version='0.2.0',
    description='Nose plugin to report test results into TestRail',
    author='Ilya Stepanko',
    author_email='ilya.email@icloud.com',
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'nose.plugins.0.10': [
            'noserail = noserail.plugin:NoseTestRail'
        ]
    },
)
