from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md', 'r').read()

REQUIREMENTS = [
    'dateparser==1.0.0',
    'ecdsa==0.16.0',
    'eth_keys',
    'eth-account>=0.4.0,<0.6.0',
    'mpmath==1.0.0',
    'pytest>=4.4.0,<5.0.0',
    'requests-mock==1.6.0',
    'requests>=2.22.0,<3.0.0',
    'setuptools==50.3.2',
    'sympy==1.6',
    'tox==3.13.2',
    'web3>=5.0.0,<6.0.0',
]

setup(
    name='dydx-v3-python',
    version='1.5.4',
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
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
