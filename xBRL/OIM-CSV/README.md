
$ pip3 install lxml pg8000 pymysql numpy rdflib isodate regex aniso8601 graphviz holidays openpyxl Pillow pycountry cherrypy cheroot python-dateutil pytz tornado pyparsing matplotlib pyodbc
$ python3 arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f whyOrWhyNot-metadata.json --saveOIMinstance whyOrWhyNot.xml

$ python arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f ../e-invoice/xBRL/oim/oim-example-metadata.json --saveOIMinstance ../e-invoice/xBRL/oim/oim-example-metadata.xml

(base) Nobu-Mac:Arelle pontsoleil$ python3
Python 3.6.1 (v3.6.1:69c0db5050, Mar 21 2017, 01:21:04) 
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
(base) Nobu-Mac:Arelle pontsoleil$ pip3 install lxml pg8000 pymysql numpy rdflib isodate regex aniso8601 graphviz holidays openpyxl Pillow pycountry cherrypy cheroot python-dateutil pytz tornado pyparsing matplotlib pyodbc
Collecting lxml
  Downloading https://files.pythonhosted.org/packages/19/2f/a987692a0b2bfe11db25392c115c94e139efa8d78f1c987d2e51d4d2fa82/lxml-4.6.2-cp36-cp36m-macosx_10_9_x86_64.whl (4.6MB)
     |████████████████████████████████| 4.6MB 2.6MB/s 
Collecting pg8000
  Downloading https://files.pythonhosted.org/packages/ed/d9/2a20d2f41d59b7b814f7cb30e8df9bbd288b000ad8a04dbc97d8c92df6df/pg8000-1.17.0-py3-none-any.whl
Collecting pymysql
  Downloading https://files.pythonhosted.org/packages/4f/52/a115fe175028b058df353c5a3d5290b71514a83f67078a6482cff24d6137/PyMySQL-1.0.2-py3-none-any.whl (43kB)
     |████████████████████████████████| 51kB 1.5MB/s 
Requirement already satisfied: numpy in /usr/local/lib/python3.6/site-packages (1.14.0)
Collecting rdflib
  Downloading https://files.pythonhosted.org/packages/d0/6b/6454aa1db753c0f8bc265a5bd5c10b5721a4bb24160fb4faf758cf6be8a1/rdflib-5.0.0-py3-none-any.whl (231kB)
     |████████████████████████████████| 235kB 7.6MB/s 
Collecting isodate
  Using cached https://files.pythonhosted.org/packages/9b/9f/b36f7774ff5ea8e428fdcfc4bb332c39ee5b9362ddd3d40d9516a55221b2/isodate-0.6.0-py2.py3-none-any.whl
Collecting regex
  Downloading https://files.pythonhosted.org/packages/4e/9e/b956e48125b2034705841f2040d07374748bec107c46de07555f6b97774a/regex-2020.11.13-cp36-cp36m-macosx_10_9_x86_64.whl (284kB)
     |████████████████████████████████| 286kB 5.8MB/s 
Collecting aniso8601
  Downloading https://files.pythonhosted.org/packages/ae/16/db3a1a970e0a7dc89204d07cff6401760380a9ab90a9dc399a8e7df3b430/aniso8601-9.0.0-py2.py3-none-any.whl (52kB)
     |████████████████████████████████| 61kB 1.5MB/s 
Collecting graphviz
  Downloading https://files.pythonhosted.org/packages/86/86/89ba50ba65928001d3161f23bfa03945ed18ea13a1d1d44a772ff1fa4e7a/graphviz-0.16-py2.py3-none-any.whl
Collecting holidays
  Downloading https://files.pythonhosted.org/packages/2a/da/3d54dac11dfb65799448ad1aebabf14f780d40203e5215ebd9517b42cb29/holidays-0.10.5.2.tar.gz (121kB)
     |████████████████████████████████| 122kB 4.1MB/s 
Collecting openpyxl
  Downloading https://files.pythonhosted.org/packages/d4/c5/1a5f82b3020bfb27f21b302f96c8ae6a34475070015d1b1e0b197a97e2af/openpyxl-3.0.6-py2.py3-none-any.whl (242kB)
     |████████████████████████████████| 245kB 3.2MB/s 
Requirement already satisfied: Pillow in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (5.0.0)
Collecting pycountry
  Downloading https://files.pythonhosted.org/packages/76/73/6f1a412f14f68c273feea29a6ea9b9f1e268177d32e0e69ad6790d306312/pycountry-20.7.3.tar.gz (10.1MB)
     |████████████████████████████████| 10.1MB 801kB/s 
Collecting cherrypy
  Downloading https://files.pythonhosted.org/packages/a8/f9/e11f893dcabe6bc222a1442bf5e14f0322a2d363c92910ed41947078a35a/CherryPy-18.6.0-py2.py3-none-any.whl (419kB)
     |████████████████████████████████| 419kB 1.9MB/s 
Collecting cheroot
  Downloading https://files.pythonhosted.org/packages/46/95/86fe6480af78fea7b0e7e1bf02e6acd4cb9e561ea200bd6d6e1398fe5426/cheroot-8.5.2-py2.py3-none-any.whl (97kB)
     |████████████████████████████████| 102kB 2.1MB/s 
Requirement already satisfied: python-dateutil in /Users/pontsoleil/Library/Python/3.6/lib/python/site-packages (2.6.1)
Requirement already satisfied: pytz in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (2017.3)
Requirement already satisfied: tornado in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (6.0.3)
Requirement already satisfied: pyparsing in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (2.2.0)
Requirement already satisfied: matplotlib in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (2.1.2)
Collecting pyodbc
  Downloading https://files.pythonhosted.org/packages/4b/d1/daa492611cd542646f12614e88a44572c7972f38d1c6d0ce44da38f69e95/pyodbc-4.0.30-cp36-cp36m-macosx_10_9_x86_64.whl (64kB)
     |████████████████████████████████| 71kB 574kB/s 
Collecting scramp==1.2.0 (from pg8000)
  Downloading https://files.pythonhosted.org/packages/0a/86/7ef1b93e8f453f297303e98869451e544588e8d76f2dd73ad17e8dabc5fc/scramp-1.2.0-py3-none-any.whl
Requirement already satisfied: six in /Users/pontsoleil/Library/Python/3.6/lib/python/site-packages (from rdflib) (1.12.0)
Collecting convertdate>=2.3.0 (from holidays)
  Downloading https://files.pythonhosted.org/packages/33/d6/86703e7fd709cd1503c9ac84db816b9017bd2ef0720404f9e71bdaf4b34a/convertdate-2.3.1-py3-none-any.whl (45kB)
     |████████████████████████████████| 51kB 1.3MB/s 
Collecting korean_lunar_calendar (from holidays)
  Downloading https://files.pythonhosted.org/packages/15/41/aa426a4a9141afd8e7f5c8312bb59d5693274f3f7b34e73bdce4ee48b4c1/korean_lunar_calendar-0.2.1-py3-none-any.whl
Collecting hijri_converter (from holidays)
  Downloading https://files.pythonhosted.org/packages/3e/75/e6da96d4ea768c8e6fa9676cffce80e457b66c3beb5711189959582870d6/hijri_converter-2.1.1-py3-none-any.whl
Collecting et-xmlfile (from openpyxl)
  Downloading https://files.pythonhosted.org/packages/22/28/a99c42aea746e18382ad9fb36f64c1c1f04216f41797f2f0fa567da11388/et_xmlfile-1.0.1.tar.gz
Collecting jdcal (from openpyxl)
  Downloading https://files.pythonhosted.org/packages/f0/da/572cbc0bc582390480bbd7c4e93d14dc46079778ed915b505dc494b37c57/jdcal-1.4.1-py2.py3-none-any.whl
Collecting zc.lockfile (from cherrypy)
  Downloading https://files.pythonhosted.org/packages/6c/2a/268389776288f0f26c7272c70c36c96dcc0bdb88ab6216ea18e19df1fadd/zc.lockfile-2.0-py2.py3-none-any.whl
Collecting more-itertools (from cherrypy)
  Downloading https://files.pythonhosted.org/packages/05/47/514062a0798c2e9bdfd4514bacf9971fc8961b715f01487e4cfda3cc45a7/more_itertools-8.7.0-py3-none-any.whl (48kB)
     |████████████████████████████████| 51kB 2.6MB/s 
Collecting portend>=2.1.1 (from cherrypy)
  Downloading https://files.pythonhosted.org/packages/b8/a1/fd29409cced540facdd29abb986d988cb1f22c8170d10022ea73af77fa55/portend-2.7.1-py3-none-any.whl
Collecting jaraco.collections (from cherrypy)
  Downloading https://files.pythonhosted.org/packages/7c/38/2b10ed4e0fbd1e12e98e9acb1e2ab942087ec911cfeaf302c14b39fce4f0/jaraco.collections-3.2.0-py3-none-any.whl
Collecting jaraco.functools (from cheroot)
  Downloading https://files.pythonhosted.org/packages/44/de/f387dbe1a7738e97220e52934dd95fca9e2e7bc238cacd103de60c01a61f/jaraco.functools-3.2.1-py3-none-any.whl
Requirement already satisfied: cycler>=0.10 in /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages (from matplotlib) (0.10.0)
Collecting pymeeus!=0.3.8,<=1,>=0.3.6 (from convertdate>=2.3.0->holidays)
  Downloading https://files.pythonhosted.org/packages/e9/71/a459d9fea14e8a0a485f47a606b8cd93f50132852a942fcb3b23f5f4f3d6/PyMeeus-0.4.1.tar.gz (5.3MB)
     |████████████████████████████████| 5.3MB 1.7MB/s 
Requirement already satisfied: setuptools in /Users/pontsoleil/Library/Python/3.6/lib/python/site-packages (from zc.lockfile->cherrypy) (39.0.1)
Collecting tempora>=1.8 (from portend>=2.1.1->cherrypy)
  Downloading https://files.pythonhosted.org/packages/06/e0/b2a0c95bebd29c757b332a2a373e8cc0debcaba801ae5dc5b7d03db1979f/tempora-4.0.1-py3-none-any.whl
Collecting jaraco.text (from jaraco.collections->cherrypy)
  Downloading https://files.pythonhosted.org/packages/c1/74/2a3c4835c079df16db8a9c50263eebb0125849fee5b16de353a059b7545d/jaraco.text-3.5.0-py3-none-any.whl
Collecting jaraco.classes (from jaraco.collections->cherrypy)
  Downloading https://files.pythonhosted.org/packages/b8/74/bee5fc11594974746535117546404678fc7b899476e769c3c55bc0cfaa02/jaraco.classes-3.2.1-py3-none-any.whl
Collecting importlib-resources; python_version < "3.7" (from jaraco.text->jaraco.collections->cherrypy)
  Downloading https://files.pythonhosted.org/packages/82/70/7bf5f275a738629a7252c30c8461502d3658a75363db9f4f88ddbeb9eeac/importlib_resources-5.1.0-py3-none-any.whl
Collecting zipp>=0.4; python_version < "3.8" (from importlib-resources; python_version < "3.7"->jaraco.text->jaraco.collections->cherrypy)
  Downloading https://files.pythonhosted.org/packages/41/ad/6a4f1a124b325618a7fb758b885b68ff7b058eec47d9220a12ab38d90b1f/zipp-3.4.0-py3-none-any.whl
Building wheels for collected packages: holidays, pycountry, et-xmlfile, pymeeus
  Building wheel for holidays (setup.py) ... done
  Stored in directory: /Users/pontsoleil/Library/Caches/pip/wheels/e7/62/d6/f5bee2a6cc5427fdec38dd2bea41d3703d543ab42f0197e9b1
  Building wheel for pycountry (setup.py) ... done
  Stored in directory: /Users/pontsoleil/Library/Caches/pip/wheels/33/4e/a6/be297e6b83567e537bed9df4a93f8590ec01c1acfbcd405348
  Building wheel for et-xmlfile (setup.py) ... done
  Stored in directory: /Users/pontsoleil/Library/Caches/pip/wheels/2a/77/35/0da0965a057698121fc7d8c5a7a9955cdbfb3cc4e2423cad39
  Building wheel for pymeeus (setup.py) ... done
  Stored in directory: /Users/pontsoleil/Library/Caches/pip/wheels/2b/d4/07/610bd9299d25383b1e86de991b2c43626164a2cbde87e032ca
Successfully built holidays pycountry et-xmlfile pymeeus
Installing collected packages: lxml, scramp, pg8000, pymysql, isodate, rdflib, regex, aniso8601, graphviz, pymeeus, convertdate, korean-lunar-calendar, hijri-converter, holidays, et-xmlfile, jdcal, openpyxl, pycountry, zc.lockfile, more-itertools, jaraco.functools, cheroot, tempora, portend, zipp, importlib-resources, jaraco.text, jaraco.classes, jaraco.collections, cherrypy, pyodbc

Successfully installed aniso8601-9.0.0 cheroot-8.5.2 cherrypy-18.6.0 convertdate-2.3.1 et-xmlfile-1.0.1 graphviz-0.16 hijri-converter-2.1.1 holidays-0.10.5.2 importlib-resources-5.1.0 isodate-0.6.0 jaraco.classes-3.2.1 jaraco.collections-3.2.0 jaraco.functools-3.2.1 jaraco.text-3.5.0 jdcal-1.4.1 korean-lunar-calendar-0.2.1 lxml-4.6.2 more-itertools-8.7.0 openpyxl-3.0.6 pg8000-1.17.0 portend-2.7.1 pycountry-20.7.3 pymeeus-0.4.1 pymysql-1.0.2 pyodbc-4.0.30 rdflib-5.0.0 regex-2020.11.13 scramp-1.2.0 tempora-4.0.1 zc.lockfile-2.0 zipp-3.4.0
WARNING: You are using pip version 19.1.1, however version 21.0.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
(base) Nobu-Mac:Arelle pontsoleil$ 
(base) Nobu-Mac:Arelle pontsoleil$ 

(base) Nobu-Mac:Arelle-master pontsoleil$ python3 arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f whyOrWhyNot-metadata.json --saveOIMinstance whyOrWhyNot.xml
[info] Activation of plug-in Load From OIM successful, version 1.2. - loadFromOIM 
[info] Activation of plug-in Save Loadable OIM successful, version 1.2. - saveLoadableOIM 
[oimce:unsupportedDocumentType] Unrecognized /documentInfo/docType: https://xbrl.org/CR/2021-02-02/xbrl-csv - whyOrWhyNot-metadata.json 
(base) Nobu-Mac:Arelle-master pontsoleil$ 