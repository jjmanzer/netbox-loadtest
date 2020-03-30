from setuptools import setup

setup(
    name='netbox-loadtest',
    version='1.0.0',
    url='https://github.com/jjmanzer/netbox-loadtest/',
    author='Jarrod Manzer',
    author_email='jarrod.manzer@gmail.com',
    license='Apache',
    description='A load test script for the netbox IPAM solution',
    include_package_data=True,
    scripts=['bin/netbox-loadtest.py'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    zip_safe=False,
    setup_requires=[],
    tests_require=[],
)
