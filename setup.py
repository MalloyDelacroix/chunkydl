from setuptools import setup, find_packages

setup(
    name='chunkydl',
    version='0.1.0',
    author='Kyle Hickey',
    author_email='malloydelacroix@gmail.com',
    description='A user friendly file download framework.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/MalloyDelacroix/chunkydl',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.5',
    install_requires=[
        'requests',
    ],
)
