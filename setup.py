from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md', 'r').read()

REQUIREMENTS = [
    'aiohttp>=3.8.1',
    'cytoolz==0.12.1',
    'dateparser==1.0.0',
    'ecdsa>=0.16.0',
    'eth_keys',
    'eth-account>=0.4.0,<0.6.0',
    'mpmath==1.0.0',
    'requests>=2.22.0,<3.0.0',
    'sympy==1.6',
    'web3>=5.0.0,<6.0.0',
]

setup(
    name='dydx-v3-python',
    version='2.1.0',
    packages=find_packages(),
    package_data={
        'dydx3': [
            'abi/*.json',
            'starkex/starkex_resources/*.json',
        ],
    },
    description='dYdX Python REST API for Limit Orders',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/dydxprotocol/dydx-v3-python',
    author='dYdX Trading Inc.',
    license='Apache 2.0',
    author_email='contact@dydx.exchange',
    install_requires=REQUIREMENTS,
    keywords='dydx exchange rest api defi ethereum eth',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
