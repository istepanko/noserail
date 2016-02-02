from setuptools import setup

setup(
    name='test-rail-nose-plugin',
    version='0.1.0',
    description='Nose plugin to report test results into TestRail',
    author='Ilya Stepanko',
    author_email='ilya.email@icloud.com',
    entry_points={
        'nose.plugins.0.10': [
            'nose_testrail = nose_testrail.plugin:NoseTestRail'
        ]
    },
)