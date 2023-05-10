# Getting Started

CIF is a model, .. it's a toy. While it's used in a number of large scale environments, it's meant to be a teaching tool. It enables you as an operator to learn from years of operational, institutional knowledge. The default, out of the box configuration is geared 100% towards getting you up and running  as quickly as possible (5min or less) so you can LEARN from our experience. 

The default, CIF/Docker configuration is NOT meant to be deployed in large scale operations. That's your job. Taking what you've learned and the components we've given you, then creating your own master piece with them. Better yet- because of them.

**python 3.6+ is required (eg: Ubuntu 18 LTS or higher)**

## Docker
### Up and Running

```bash
$ export CSIRTG_TOKEN=1234  # sign up at csirtg.io
$ export MAXMIND_USERID=1234  # sign up at maxmind.com to leverage geo location data
$ export MAXMIND_LIC=1234

$ git clone https://github.com/csirtgadgets/cif-v5.git
$ mkdir data  # shared data directory for containers
$ cp cif-v5/docker-compose.yml ./
$ mkdir -p data/rules  # copy any local custom rules here
$ # cp my_custom_rule.yml data/rules/
$ chmod 755 data/rules
$ docker-compose pull
$ docker-compose up -d
```

### Status
```bash
$ docker-compose logs -f
Attaching to cif-router, cif-httpd, cif-enrichers, csirtg-fm
cif-httpd       | [2020-03-14 15:05:29 +0000] [7] [INFO] Starting gunicorn 19.10.0
cif-httpd       | [2020-03-14 15:05:29 +0000] [7] [INFO] Listening at: http://0.0.0.0:5000 (7)
cif-httpd       | [2020-03-14 15:05:29 +0000] [7] [INFO] Using worker: gevent
cif-httpd       | [2020-03-14 15:05:29 +0000] [10] [INFO] Booting worker with pid: 10
cif-httpd       | [2020-03-14 15:05:29 +0000] [11] [INFO] Booting worker with pid: 11
cif-httpd       | [2020-03-14 15:05:29 +0000] [12] [INFO] Booting worker with pid: 12
cif-httpd       | [2020-03-14 15:05:29 +0000] [13] [INFO] Booting worker with pid: 13
csirtg-fm       | 2020-03-14 15:05:30,107 - INFO - csirtg_fm.cli[316] - random delay is 1.0
csirtg-fm       | 2020-03-14 15:05:30,107 - INFO - csirtg_fm.cli[317] - running every 60 after that  # <--- data will start coming in after this 60 delay
csirtg-fm       | 2020-03-14 15:06:30,184 - INFO - csirtg_fm.cli[85] - starting run...
csirtg-fm       | 2020-03-14 15:06:30,261 - INFO - csirtg_fm.cli[157] - processing: openphish.yml - urls
csirtg-fm       | 2020-03-14 15:06:38,681 - INFO - csirtg_fm.cli[157] - processing: abuse_ch.yml - urlhaus
csirtg-fm       | 2020-03-14 15:07:01,407 - INFO - csirtg_fm[125] - sending: 6
csirtg-fm       | 2020-03-14 15:07:01,598 - INFO - csirtg_fm.cli[157] - processing: abuse_ch.yml - feodo_malware
csirtg-fm       | 2020-03-14 15:07:20,339 - INFO - csirtg_fm.cli[157] - processing: abuse_ch.yml - feodo_botnet
csirtg-fm       | 2020-03-14 15:07:32,947 - INFO - csirtg_fm[125] - sending: 31
csirtg-fm       | 2020-03-14 15:07:33,745 - INFO - csirtg_fm.cli[157] - processing: alexa.yml - top-1000
csirtg-fm       | 2020-03-14 15:07:36,896 - INFO - csirtg_fm[125] - sending: 500
csirtg-fm       | 2020-03-14 15:07:45,937 - INFO - csirtg_fm[125] - sending: 500
```

## Testing
```bash
# this requires python3.6 or higher (eg: ubuntu 18 LTS..)

$ pip3 install geoip2 'cifsdk>=5.0b1,<6.0'

$ export CIF_REMOTE='http://localhost:5000'
$ cif -nq example.com
$ cif --itype url --tags malware  # may have to wait 5-10 after starting as data flows in
```

## Where Next?

* [Review the wiki](https://github.com/csirtgadgets/cif-v5/wiki)
* [Working with csirtg-fm to parse threat intel](https://github.com/csirtgadgets/csirtg-fm-v2/wiki)
* [Working with the SDK](https://github.com/csirtgadgets/cifsdk-v5-py/wiki)
* [Working with the API](https://github.com/csirtgadgets/cif-v5/wiki/REST-API)
* [Working with custom threat feeds](https://github.com/csirtgadgets/cif-v5/wiki/Custom-threat-feeds)
* [Integrating into your infrastructure](https://github.com/csirtgadgets/cif-v5/wiki/Where-do-I-start-with-Integrations)
* [Navigate to the LOCAL API](http://localhost:5000)

# What's Changed?

* Less. Stuff. 
* Abstracted a lot of the technical pieces into separate libraries (eg: csirtg-geo, csirtg-peers, etc)
* Codebase has been significantly simplified
* **NO TOKENS**, YOU ARE RESPONSIBLE FOR PROTECTING YOUR NODES!!!
* Pipelines and better Plugin support for "external enrichment"
* Docker Compose is the first class citizen, feel free to customize from there
* Docker containers are now split up, not running as supervisord anymore
* cif-httpd is significantly simpler to interact with, improved REST doc (openapi)
* New threat intel rules
* Python 3.7+ support

# Building Locally
```bash
$ git clone https://github.com/csirtgadgets/cif-v5.git
$ cd cif-v5/
$ make docker
$ make docker-tag
$ docker-compose up -d
$ docker-compose logs -f
```

## Architecture

```
                                                              cif-enricher
                                                               ^        +
                                                               |        |
                                                               +        v
csirtg-fm +--> cifsdk  +--------->  cif-httpd +------------> cif-router +-----> cif-store +-----> sqlite
                                                               +
                                           ^                   |        ^
                                           |                   |        |
                                           |                   v        +
                                           |                   cif-hunter
                                           +

                                        cifsdk
```

# Getting Involved
There are many ways to get involved with the project. If you have a new and exciting feature, or even a simple bugfix, simply [fork the repo](https://help.github.com/articles/fork-a-repo), create some simple test cases, [generate a pull-request](https://help.github.com/articles/using-pull-requests) and give yourself credit!

If you've never worked on a GitHub project, [this is a good piece](https://guides.github.com/activities/contributing-to-open-source) for getting started.

* [How To Contribute](contributing.md)  
* [Project Page](http://csirtgadgets.com/collective-intelligence-framework/)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YZPQXDLNYZZ3W)

# COPYRIGHT AND LICENSE

Copyright (C) 2020 [the CSIRT Gadgets](http://csirtgadgets.com)

Free use of this software is granted under the terms of the [Mozilla Public License (MPLv2)](https://www.mozilla.org/en-US/MPL/2.0/).
