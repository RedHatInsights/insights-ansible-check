""" A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='insights-policy-check',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.6',

    description='Conformance as an Ansible Playbook',
    long_description=long_description,

    url='https://github.com/redhatinsights/insights-policy-check.git',

    author='Gavin Romig-Koch',
    author_email='gavin@redhat.com',

    license='GPLv3+',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
    ],

    install_requires=['ansible', 'requests'],
    extras_require={
        'develop': ['pytest'],
        },

    data_files=[
	('bin', ['bin/insights-policy-check']),
	('share/insights-policy-check/plugins/action_plugins', ['share/insights-policy-check/plugins/action_plugins/check.py']),
	('share/insights-policy-check/plugins/callback_plugins', ['share/insights-policy-check/plugins/callback_plugins/notify_insights.py']),
	('share/insights-policy-check/plugins/library', ['share/insights-policy-check/plugins/library/check.py']),
    ],

    scripts=[
        'bin/insights-policy-check',
    ],
)
