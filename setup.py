from setuptools import setup

setup(
    name='noserail',
    version='0.1.0',
    description='Nose plugin to report test results into TestRail',
    py_modules=['plugin'],
    author='Ilya Stepanko',
    author_email='ilya.email@icloud.com',
    entry_points={
        'nose.plugins.0.10': [
            'noserail = noserail.plugin:NoseTestRail'
        ]
    },
)
