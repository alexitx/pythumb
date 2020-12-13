from setuptools import setup


def read(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()

metadata = {}
exec(read('pythumb/_version.py'), metadata)

long_description = read('README.md')

setup(
    name=metadata['__title__'],
    version=metadata['__version__'],
    description='Command line utility & API for downloading YouTube thumbnails',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    license=metadata['__license__'],
    url=metadata['__url__'],
    project_urls={
        'Source': 'https://github.com/alexitx/pythumb',
        'Issues': 'https://github.com/alexitx/pythumb/issues'
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'pythumb = pythumb.cli:main',
        ],
    },
    include_package_data=True,
    packages=[
        'pythumb'
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.0,<3'
    ]
)
