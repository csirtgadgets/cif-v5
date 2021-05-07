import os
from setuptools import setup, find_packages
import versioneer
import sys

ENABLE_INSTALL = os.getenv('CIF_ENABLE_INSTALL')

if sys.argv[-1] == 'install' and not ENABLE_INSTALL:
    print('')
    print('CIFv5 Should NOT be installed using traditional install methods')
    print('Checkout the Docker instructions in the wiki')
    print('')
    print('https://github.com/csirtgadgets/cif-v5/wiki')
    print('')
    raise SystemError


# https://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'test':
    test_requirements = [
        'pytest',
        'coverage',
        'pytest_cov',
    ]
    try:
        modules = map(__import__, test_requirements)
    except ImportError as e:
        err_msg = e.message.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirements." % err_msg
        raise ImportError(msg)

    r = os.system('pytest test -sv --cov=cif --cov-fail-under=50 && '
                  'xenon -b C -m B -a B -e "cif/_version*,cif/store/sqlite/filters.py" cif')

    if r == 0:
        sys.exit()
    else:
        raise RuntimeError('tests failed')

setup(
    name="cif",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CIFv5",
    long_description="",
    url="https://github.com/csirtgadgets/cif-v5",
    license='MPL2',
    classifiers=[
        "LICENSE :: OSI APPROVED :: MOZILLA PUBLIC LICENSE 2.0 (MPL 2.0)"
        "Topic :: System :: Networking",
        "Topic :: System :: Security",
        "Programming Language :: Python",
    ],
    keywords=['security', 'threat', 'intelligence', 'platform', 'tips'],
    author="Wes Young",
    author_email="wes@csirtgadgets.com",
    packages=find_packages(exclude='test'),
    python_requires='>=3.6, <3.8', # Software only validated on python 3.7
    install_requires=[
        'SQLAlchemy',
        'SQLAlchemy-Utils',
        'werkzeug',
        'Flask',
        'flask-cors',
        'flask-compress',
        'flask-restplus',
        'gunicorn',
        'gevent',
        'maxminddb',
        'geoip2',
        'pytricia',
        'csirtg-geo',
        'csirtg-hunter',
        'csirtg-enrichment',
        'csirtg-dnsdb',
        'cifsdk>=5.0a0,<6.0',
        'csirtg-fm>=2.0b0,<3.0'
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            'cif-router=cif.router:main',
            'cif-httpd=cif.http.app:main',
            'cif-store=cif.store:main',
            'cif-enricher=cif.enricher:main',
            'cif-hunter=cif.hunter:main'
        ]
    },
)
