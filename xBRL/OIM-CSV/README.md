
# Installation memo
```
$ pip3 install lxml pg8000 pymysql numpy rdflib isodate regex aniso8601 graphviz holidays openpyxl Pillow pycountry cherrypy cheroot python-dateutil pytz tornado pyparsing matplotlib pyodbc
$ python3 arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f whyOrWhyNot-metadata.json --saveOIMinstance whyOrWhyNot.xml
$ python arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f ../e-invoice/xBRL/oim/oim-example-metadata.json --saveOIMinstance ../e-invoice/xBRL/oim/oim-example-metadata.xml
```
# OIM-CSV

_ | file name
-- | --
metadata | [example_1-metadata.json](./example_1-metadata.json)
taxonomy | [../taxonomy/pint/core.xsd](../taxonomy/pint/core.xsd)
source CSV | [example_1-oim.csv](./example_1-oim.csv)
converted XML | [example_1.xml](./example_1.xml)

command log on Windows 10
```
> python arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f ../xBRL-Alpha/xBRL/OIM-CSV/example_1-metadata.json --saveOIMinstance ../xBRL-Alpha/xBRL/OIM-CSV/example_1.xml
[info] Activation of plug-in Load From OIM successful, version 1.2. - loadFromOIM
[info] Activation of plug-in Save Loadable OIM successful, version 1.2. - saveLoadableOIM
[info] loaded in 0.71 secs at 2022-07-14T07:51:05 - C:\Users\nobuy\OneDrive\ドキュメント\GitHub\xBRL-Alpha\xBRL\OIM-CSV\example_1-metadata.json
>
```

Dimension is defined under segment in context  
```
    <context id="c-01">
        <entity>
            <identifier scheme="http://www.example.com">Example co.</identifier>
            <segment>
                <xbrldi:typedMember dimension="pint:_380">
                    <pint:_v>12345678</pint:_v>
                </xbrldi:typedMember>
            </segment>
        </entity>
        <period>
            <instant>2023-11-30</instant>
        </period>
    </context>
```