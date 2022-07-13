#!/usr/bin/env python3
# coding: utf-8
#
# generate Open Peoopl e-Invoice (xBRL) Taxonomy fron CSV file and header files
#
# designed by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
# written by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
#
# MIT License
#
# (c) 2022 SAMBUICHI Nobuyuki (Sambuichi Professional Engineers Office)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# from jsonschema import validate
from cgi import print_directory
# from distutils.debug import DEBUG
import json
# from pyrsistent import b
import os
import yaml
import sys
import csv
import re
import hashlib
import datetime

DEBUG = True
VERBOSE = True
SEP = os.sep

xbrl_gl_file = 'xbrl-gl.csv'
xbrl_gl_file = xbrl_gl_file.replace('/', SEP)
datatype_file = 'datatype.csv'
datatype_file = datatype_file.replace('/', SEP)

xbrl_gl_file2 = 'xbrl-gl-2.csv'
xbrl_gl_file2 = xbrl_gl_file2.replace('/', SEP)

xbrl_source = '../source/head/'
xbrl_source = xbrl_source.replace('/', SEP)
core_head = 'gl-cor-head.txt'

xbrl_base = '../taxonomy/xBRL-GD/'
xbrl_base = xbrl_base.replace('/', SEP)
core_xsd = 'gl-cor.xsd'
core_label = 'gl-cor-lbl'
core_presentation = 'gl-cor-pre'
core_definition = 'gl-cor-def'

shared_yaml = None

datatypeMap = {
    'Unit Price Amount': 'gd:unitPriceAmountItemType',
    'Code': 'gd:codeItemType',
    'Date': 'gd:dateItemType',
    'Binary object': 'gd:binaryObjectItemType',
    'Binary Object': 'gd:binaryObjectItemType',
    'Time': 'gd:timeItemType',
    'Identifier': 'gd:identifierItemType',
    'Quantity': 'gd:quantityItemType',
    'Amount': 'gd:amountItemType',
    'Document Reference': 'gd:documentReferenceItemType',
    'Text': 'gd:textItemType',
    'Percentage': 'gd:percentageItemType',
    'Exchange Rate': 'gd:numericItemType'
}
roles = []
roleURIs = {}
gdMap = {
    'busG-01': 'entityPhoneNumber',
    'busG-02': 'entityFaxNumberStructure',
    'busG-03': 'entityEmailAddressStructure',
    'busG-04': 'organizationIdentifiers',
    'busG-05': 'organizationAddress',
    'busG-06': 'entityWebSite',
    'busG-07': 'contactInformation',
    'busG-08': 'contactPhone',
    'busG-09': 'contactFax',
    'busG-10': 'contactEMail',
    'busG-11': 'organizationAccountingMethodStructure',
    'busG-12': 'accountantInformation',
    'busG-13': 'accountantAddress',
    'busG-14': 'accountantContactInformation',
    'busG-15': 'accountantContactPhone',
    'busG-16': 'accountantContactFax',
    'busG-17': 'accountantContactEmail',
    'busG-18': 'reportingCalendar',
    'busG-19': 'reportingCalendarPeriod',
    'busG-20': 'identifierAddress',
    'busG-21': 'measurable',
    'busG-22': 'jobInfo',
    'busG-23': 'depreciationMortgage',
    'corG-01': 'accountingEntries',
    'corG-02': 'documentInfo',
    'corG-03': 'entityInformation',
    'corG-04': 'entryHeader',
    'corG-05': 'entryDetail',
    'corG-06': 'account',
    'corG-07': 'accountSub',
    'corG-08': 'segmentParentTuple',
    'corG-09': 'identifierReference',
    'corG-10': 'identifierExternalReference',
    'corG-11': 'identifierEMail',
    'corG-12': 'identifierPhoneNumber',
    'corG-13': 'identifierFaxNumber',
    'corG-14': 'identifierContactInformationStructure',
    'corG-15': 'identifierContactPhone',
    'corG-16': 'identifierContactFax',
    'corG-17': 'identifierContactEmail',
    'corG-18': 'xbrlInfo',
    'corG-19': 'taxes',
    'busG-01': 'entityPhoneNumber',
    'busG-02': 'entityFaxNumberStructure',
    'busG-03': 'entityEmailAddressStructure',
    'busG-04': 'organizationIdentifiers',
    'busG-05': 'organizationAddress',
    'busG-06': 'entityWebSite',
    'busG-07': 'contactInformation',
    'busG-08': 'contactPhone',
    'busG-09': 'contactFax',
    'busG-10': 'contactEMail',
    'busG-11': 'organizationAccountingMethodStructure',
    'busG-12': 'accountantInformation',
    'busG-13': 'accountantAddress',
    'busG-14': 'accountantContactInformation',
    'busG-15': 'accountantContactPhone',
    'busG-16': 'accountantContactFax',
    'busG-17': 'accountantContactEmail',
    'busG-18': 'reportingCalendar',
    'busG-19': 'reportingCalendarPeriod',
    'busG-20': 'identifierAddress',
    'busG-21': 'measurable',
    'busG-22': 'jobInfo',
    'busG-23': 'depreciationMortgage',
    'ehmG-01': 'serialLot',
    'mucG-01': 'multicurrencyDetail',
    'tafG-01': 'originatingDocumentStructure'
    # 'srcdG-01': 'summaryReportingTaxonomies',
    # 'srcdG-02': 'summaryPrecisionDecimals',
    # 'srcdG-03': 'summaryContext',
    # 'srcdG-04': 'summaryEntity',
    # 'srcdG-05': 'summarySegment',
    # 'srcdG-06': 'segmentExplicit',
    # 'srcdG-07': 'segmentTyped',
    # 'srcdG-08': 'segmentSimpleElement',
    # 'srcdG-09': 'summaryPeriod',
    # 'srcdG-10': 'summaryScenario',
    # 'srcdG-11': 'senarioExplicit',
    # 'srcdG-12': 'senarioTyped',
    # 'srcdG-13': 'senarioSimpleElement',
    # 'srcdG-14': 'summaryUnit',
    # 'srcdG-15': 'richTextComment',
}

duplicateNames = set()
names = set()
glDict = {}
locsDefined = {}
locsDefined['def'] = {}
repeatableBG = None

def file_path(pathname):
    if SEP == pathname[0:1]:
        return pathname
    else:
        dir = os.path.dirname(__file__)
        new_path = os.path.join(dir, pathname)
        return new_path

def LC3(term):
    if not term:
        return ''
    terms = term.split(' ')
    name = ''
    for i in range(len(terms)):
        if i == 0:
            if 'TAX' == terms[i]:
                name += terms[i].lower()
            else:
                name += terms[i][0].lower() + terms[i][1:]
        else:
            name += terms[i][0].upper() + terms[i][1:]
    return name

def SC(term):
    if not term:
        return ''
    terms = term.split(' ')
    name = '_'.join(terms)
    return name

def formatID(id):
    if len(id) < 3:
        return id
    num = id[id.find('-')+1:]
    if 'G'==id[id.find('-')-1]:
        if 1==len(num):
            id = f"{id[:id.find('-')+1]}0{num}"
    else:
        if 1==len(num):
            id = f"{id[:id.find('-')+1]}00{num}"
        elif 2==len(num):
            id = f"{id[:id.find('-')+1]}0{num}"
    return id

def defineHypercube(hypercube_id):
    global core_xsd
    global base_id
    global root_id
    global id
    global hypercube
    global dimensions
    global child_count
    global locsDefined
    global lines

    if not hypercube_id in locsDefined['def']:
        locsDefined['def'][hypercube_id] = []

    URI = hypercube["URI"]
    line = f'    <link:definitionLink xlink:type="extended" xlink:role="http://www.xbrl.jp/gd{URI}">\n'
    lines.append(line)
    if not root_id in locsDefined['def'][hypercube_id]:
        locsDefined['def'][hypercube_id].append(root_id)
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{root_id}" xlink:label="{root_id}" xlink:title="{root_id}"/>\n'
        lines.append(line)
    if base_id != root_id:
        if not root_id in child_count:
            child_count[root_id] = 0
        child_count[root_id] += 1 
        count = child_count[root_id]
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{root_id}" xlink:to="{base_id}" xlink:title="definition: {root_id} to {base_id}" order="{count}"/>\n'
        lines.append(line)
    if root_id != base_id:
        if not base_id in locsDefined['def'][hypercube_id]:
            locsDefined['def'][hypercube_id].append(base_id)
            line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{base_id}" xlink:label="{base_id}" xlink:title="{base_id}"/>\n'
            lines.append(line)

    child_count = {}
    base = glDict[base_id]
    if 'children' in base and len(base['children']) > 0:
        for id in base['children']:
            if base_id in repeatables and id in repeatables[base_id]:
                # targetRole
                role = f'http://www.xbrl.jp/gd{roleURIs[gdMap[id]]}'
                line = f'        <!-- targetRole {role} -->\n'
                lines.append(line)
                line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{id}" xlink:label="{id}" xlink:title="{id}"/>\n'
                lines.append(line)

                if not base_id in child_count:
                    child_count[base_id] = 0
                child_count[base_id] += 1 
                count = child_count[base_id]
                line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xbrldt:targetRole="{role}" xlink:from="{base_id}" xlink:to="{id}"  xlink:title="definition: {base_id} to {id}" order="{count}"/>\n'
                lines.append(line)
                continue
            parent_id = glDict[id]['parent'][-1]
            if parent_id in repeatableBGs:
                continue
            if parent_id != base_id:
                if not parent_id in locsDefined['def'][hypercube_id]:
                    locsDefined['def'][hypercube_id].append(parent_id)
                    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{parent_id}" xlink:label="{parent_id}" xlink:title="{parent_id}"/>\n'
                    lines.append(line)
                    if not base_id in child_count:
                        child_count[base_id] = 0
                    child_count[base_id] += 1 
                    count = child_count[base_id]
                    line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{base_id}" xlink:to="{parent_id}" xlink:title="definition: {base_id} to {parent_id}" order="{count}"/>\n'
                    lines.append(line)
            if not id in locsDefined['def'][hypercube_id]:
                locsDefined['def'][hypercube_id].append(id)
                line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{id}" xlink:label="{id}" xlink:title="{id}"/>\n'
                lines.append(line)
            if not parent_id in child_count:
                child_count[parent_id] = 0
            child_count[parent_id] += 1
            count = child_count[parent_id]
            line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{parent_id}" xlink:to="{id}" xlink:title="definition: {parent_id} to {id}" order="{count}"/>\n'
            lines.append(line)

    # all
    line = '        <!-- all -->\n'
    lines.append(line)
    if not base_id in child_count:
        child_count[base_id] = 0
    child_count[base_id] += 1
    count = child_count[base_id]
    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{hypercube["id"]}" xlink:label="{hypercube["label"]}" xlink:title="{hypercube["label"]}"/>\n'
    lines.append(line)
    line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/all" xlink:from="{base_id}" xlink:to="{hypercube["label"]}" xlink:title="definition: {base_id} to {hypercube["label"]}" order="{count}" xbrldt:closed="true" xbrldt:contextElement="scenario"/>\n'
    lines.append(line)
    if DEBUG:
        print(f'definition: {base_id} to {hypercube["label"]} all')
    # hypercube-dimension
    line = '        <!-- hypercube-dimension -->\n'
    lines.append(line)
    for dimension in dimensions:
        if not hypercube["label"] in child_count:
            child_count[hypercube["label"]] = 0
        child_count[hypercube["label"]] += 1
        count = child_count[hypercube["label"]]
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{dimension["id"]}" xlink:label="{dimension["label"]}" xlink:title="{dimension["label"]}"/>\n'
        lines.append(line)
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:from="{hypercube["label"]}" xlink:to="{dimension["label"]}" xlink:title="definition: {hypercube["label"]} to {dimension["label"]}" order="{count}"/>\n'
        lines.append(line)
        if DEBUG:
            print(f'definition: {hypercube["label"]} to {dimension["label"]} hypercube-dimension')

    line = '    </link:definitionLink>\n'
    lines.append(line)

if __name__ == '__main__':
    for id,name in gdMap.items():
        Name = f"{name[0].upper()}{name[1:]}"
        # if 'corG-01'==id:
        #     roles.append({'URI':'/root','id':Name})
        #     roleURIs[name] = '/root'
        # else:
        roles.append({'URI':f'/{Name}','id':Name})
        roleURIs[name] = f'/{Name}'
    # ====================================================================
    # 0. datatype.csv -> datatype
    datatype = {}
    datatype['_'] = ''
    datatype_file = file_path(datatype_file)
    with open(datatype_file, encoding='utf-8', newline='') as f:
        reader = csv.reader(f) #, delimiter='\t')
        header = next(reader)
        for cols in reader:
            record = {}
            for i in range(len(cols)):
                col = cols[i]
                record[header[i]] = col.strip()
            datatype[record['name']] = record['datatype']
    # ====================================================================
    # 1. xbrl_gl.csv -> schema
    records = []
    xbrl_gl_file = file_path(xbrl_gl_file)
    with open(xbrl_gl_file, encoding='utf-8', newline='') as f:
        reader = csv.reader(f) #, delimiter='\t')
        header = next(reader)
        header = ['seq','module','id','level','parent','name','card','type','label','description','label_ja','description_ja']
        for cols in reader:
            record = {}
            for i in range(len(cols)):
                col = cols[i]
                record[header[i]] = col.strip()
            id = record['id']
            if not id or 'srcd'==id[:4]:
                continue
            id = formatID(id)
            record['id'] = id
            parent = record['parent']
            parent = formatID(parent)
            record['parent'] = parent
            level = record['level']
            if not level:
                record['level'] = 0
            else:
                record['level'] = int(level) - 1
            if not record['card']:
                record['card'] = '1..1'
            name = record['name']
            type = record['type']
            record['name'] = name
            if type in datatype:
                record['type'] = datatype[type]
            else:
                print(f'{id} {name} {type}')
                record['type'] = 'xbrli:stringItemType'
            record['id'] = id
            records.append(record)
            glDict[id] = record

    records = sorted(records, key=lambda x: x['seq'])

    xbrl_gl_file2 = file_path(xbrl_gl_file2)
    with open(xbrl_gl_file2, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    parent = ['corG-01']
    level = 0
    for id, record in glDict.items():
        if 'corG-01'==id:
            continue
        level = record['level']
        if level > len(parent) - 1:
            parent.append('')
        for i in range(len(parent)):
            if i > level:
                parent.pop(-1)
        parent[level] = id
        if 'corG-01'!=id and glDict[id]['parent'] != parent[-2]:
            print(f"{id} {glDict[id]['parent']} != {parent[-2]}")
            record['parent'] = parent[-2]
        glDict[id]['parent'] = parent[:-1]
        glDict[id]['level'] = level
    # if DEBUG:
    #     print(f"{id} parent:{glDict[id]['parent']}")

    repeatables = {}
    for id, record in glDict.items():
        if 'card' in record and len(record['parent']) > 0 and 'n' == record['card'][-1]:
            parent_id = record['parent'][-1]
            if DEBUG: print(f"{id} {record['card']} parent:{parent_id}")
            if not parent_id in repeatables:
                repeatables[parent_id] = [id]
            else:
                repeatables[parent_id].append(id)
    if DEBUG:
        print(repeatables)

    repeatableBGs = []
    for k, v in repeatables.items():
        for id in v:
            repeatableBGs.append(id)

    for k, v in glDict.items():
        if 'parent' in v:
            if len(v['parent']) > 0:
                for parent_id in v['parent']:
                    if len(parent_id) < 3:
                        continue
                    # parent_id = v['parent'][-1]
                    if not 'children' in glDict[parent_id]:
                        glDict[parent_id]['children'] = [k]
                    elif not k in glDict[parent_id]['children']:
                        glDict[parent_id]['children'].append(k)

    # Schema
    lines = []
    head_file = file_path(f'{xbrl_source}{core_head}')
    with open(head_file, encoding='utf_8', newline='') as f:
        lines = f.readlines()

    line = f'    <annotation>\n'
    lines.append(line)
    line = f'        <appinfo>\n'
    lines.append(line)
    line = f'            <link:roleType id="none" roleURI="http://www.xbrl.jp/gd/none">\n'
    lines.append(line)
    line = f'                <link:definition>None</link:definition>\n'
    lines.append(line)
    line = f'                <link:usedOn>link:presentationLink</link:usedOn>\n'
    lines.append(line)
    line = f'                <link:usedOn>link:definitionLink</link:usedOn>\n'
    lines.append(line)
    line = f'            </link:roleType>\n'
    lines.append(line)
    for id,name in gdMap.items():
        Name = f"{name[0].upper()}{name[1:]}"
        line = f'            <link:roleType id="{Name}" roleURI="http://www.xbrl.jp/gd/{Name}">\n'
        lines.append(line)
        line = f'                <link:definition>{Name}</link:definition>\n'
        lines.append(line)
        line = f'                <link:usedOn>link:presentationLink</link:usedOn>\n'
        lines.append(line)
        line = f'                <link:usedOn>link:definitionLink</link:usedOn>\n'
        lines.append(line)
        line = f'            </link:roleType>\n'
        lines.append(line)
    line = f'        </appinfo>\n'
    lines.append(line)
    line = f'    </annotation>\n'
    lines.append(line)
    line = f'    <!-- Hypercube -->\n'
    lines.append(line)
    line = f'    <element name="H_none" id="gd_H_none" substitutionGroup="xbrldt:hypercubeItem" nillable="true" abstract="true" type="xbrli:stringItemType" xbrli:periodType="instant"/>\n'
    lines.append(line)
    for id,name in gdMap.items():
        Name = f"{name[0].upper()}{name[1:]}"
        line = f'    <element name="H_{Name}" id="gd_H_{Name}" substitutionGroup="xbrldt:hypercubeItem" nillable="true" abstract="true" type="xbrli:stringItemType" xbrli:periodType="instant"/>\n'
        lines.append(line)
    line = f'    <!-- Dimension -->\n'
    lines.append(line)
    line = f'    <element name="dimProhibited" id="gd_dimProhibited" substitutionGroup="xbrldt:dimensionItem" nillable="true" abstract="true" type="xbrli:stringItemType" xbrli:periodType="instant" xbrldt:typedDomainRef="#_v"/>\n'
    lines.append(line)
    for id,name in gdMap.items():
        Name = f"{name[0].upper()}{name[1:]}"
        line = f'    <element name="{Name}" id="gd_{Name}" substitutionGroup="xbrldt:dimensionItem" nillable="true" abstract="true" type="xbrli:stringItemType" xbrli:periodType="instant" xbrldt:typedDomainRef="#_v"/>\n'
        lines.append(line)
    line = f'    <!-- element -->\n'
    lines.append(line)
    for record in records:
        id = record['id']
        name = record['name']
        type = record['type']
        if 'G-' in id:
            line = f'    <element name="{id}" id="gd_{id}" type="xbrli:stringItemType" nillable="true" abstract="true" substitutionGroup="xbrli:item" xbrli:periodType="instant"/>\n'
        else:
            line = f'    <element name="{id}" id="gd_{id}" type="{type}" nillable="false" substitutionGroup="xbrli:item" xbrli:periodType="instant"/>\n'
        lines.append(line)

    line = '</schema>'
    lines.append(line)

    gd_xsd_file = file_path(f'{xbrl_base}{core_xsd}')
    with open(gd_xsd_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if VERBOSE:
        print(f'-- {gd_xsd_file}')

    #
    # labelLink en
    #
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--  (c) 2022 XBRL Japan inc. -->\n',
        '<link:linkbase\n',
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n',
        '    xmlns:link="http://www.xbrl.org/2003/linkbase"\n',
        '    xmlns:xlink="http://www.w3.org/1999/xlink"\n',
        '    xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
        '    <link:roleRef roleURI="http://www.xbrl.jp/gd/role/description" xlink:type="simple" xlink:href="gl-cor.xsd#description"/>\n',
        '    <link:arcroleRef arcroleURI="http://www.xbrl.jp/gd/arcrole/concept-description" xlink:type="simple" xlink:href="gl-cor.xsd#concept-description"/>\n',
        '    <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n'
    ]
    for record in records:
        id = record['id']
        name = record['name']
        label = record['label']
        label_ja = record['label_ja']
        description = record['description']
        description_ja = record['description_ja']
        line = f'        <!-- {id} {name} -->\n'
        lines.append(line)
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{id}" xlink:label="{id}" xlink:title="{id}"/>\n'
        lines.append(line)
        # label
        line = f'        <link:label xlink:type="resource" xlink:label="label_{id}" xlink:title="label_{id}" id="label_{id}" xml:lang="en" xlink:role="http://www.xbrl.org/2003/role/label">{label}</link:label>\n'
        lines.append(line)
        line = f'        <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{id}" xlink:to="label_{id}" xlink:title="label: {id} to label_{id}"/>\n'
        lines.append(line)
        # description
        if label != description:
            line = f'        <link:label xlink:type="resource" xlink:label="description_{id}" xlink:title="description_{id}" id="description_{id}" xml:lang="en" xlink:role="http://www.xbrl.jp/gd/role/description">{description}</link:label>\n'
            lines.append(line)
            line = f'        <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.jp/gd/arcrole/concept-description" xlink:from="{id}" xlink:to="description_{id}" xlink:title="label: {id} to label_{id}"/>\n'
            lines.append(line)

    lines.append('  </link:labelLink>\n')
    lines.append('</link:linkbase>\n')

    gd_label_file = file_path(f'{xbrl_base}{core_label}-en.xml')
    with open(gd_label_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)

    if VERBOSE:
        print(f'-- {gd_label_file}')

    #
    # labelLink ja
    #
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--  (c) 2022 XBRL Japan inc. -->\n',
        '<link:linkbase\n',
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n',
        '    xmlns:link="http://www.xbrl.org/2003/linkbase"\n',
        '    xmlns:xlink="http://www.w3.org/1999/xlink"\n',
        '    xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
        '    <link:roleRef roleURI="http://www.xbrl.jp/gd/role/description" xlink:type="simple" xlink:href="gl-cor.xsd#description"/>\n',
        '    <link:arcroleRef arcroleURI="http://www.xbrl.jp/gd/arcrole/concept-description" xlink:type="simple" xlink:href="gl-cor.xsd#concept-description"/>\n',
        '    <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n'
    ]
    for record in records:
        id = record['id']
        name = record['name']
        label = record['label']
        label_ja = record['label_ja']
        description = record['description']
        description_ja = record['description_ja']
        line = f'        <!-- {id} {name} -->\n'
        lines.append(line)
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{id}" xlink:label="{id}" xlink:title="{id}"/>\n'
        lines.append(line)
        # label_ja
        line = f'        <link:label xlink:type="resource" xlink:label="label_{id}" xlink:title="label_{id}" id="label_{id}" xml:lang="ja" xlink:role="http://www.xbrl.org/2003/role/label">{label_ja}</link:label>\n'
        lines.append(line)
        line = f'        <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{id}" xlink:to="label_{id}" xlink:title="label: {id} to label_{id}"/>\n'
        lines.append(line)
        # description_ja
        if label_ja != description_ja:
            line = f'        <link:label xlink:type="resource" xlink:label="description_{id}" xlink:title="description_{id}" id="description_{id}" xml:lang="ja" xlink:role="http://www.xbrl.jp/gd/role/description">{description_ja}</link:label>\n'
            lines.append(line)
            line = f'        <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.jp/gd/arcrole/concept-description" xlink:from="{id}" xlink:to="description_{id}" xlink:title="label: {id} to label_{id}"/>\n'
            lines.append(line)

    lines.append('  </link:labelLink>\n')
    lines.append('</link:linkbase>\n')

    gd_label_file = file_path(f'{xbrl_base}{core_label}-ja.xml')
    with open(gd_label_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)

    if VERBOSE:
        print(f'-- {gd_label_file}')

    #
    #   presentationLink
    #
    child_count = {}
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--  (c) 2022 XBRL Japan inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">\n',
        '  <link:roleRef roleURI="http://www.xbrl.jp/gd/AccountingEntries" xlink:type="simple" xlink:href="gl-cor.xsd#AccountingEntries"/>\n',
        '  <link:presentationLink xlink:type="extended" xlink:role="http://www.xbrl.jp/gd/AccountingEntries">\n',
    ]
    definedLocs = []
    for record in records:
        id = record['id']
        if 'ibg-00' == id:
            continue
        if not id in definedLocs:
            definedLocs.append(id)
            name = record['name']
            line = f'        <!-- {id} {name} -->\n'
            lines.append(line)
            line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{id}" xlink:label="{id}" xlink:title="presentation: {id} {name}"/>\n'
            lines.append(line)
        parent_id = record['parent']
        if parent_id:
            parent_id = parent_id[-1]
        if parent_id and parent_id in glDict:
            parent = glDict[parent_id]
        else:
            print(id)
        if parent:
            if 'name' in parent:
                parent_name = parent['name']
                if not parent_id in definedLocs:
                    definedLocs.append(parent_id)
                    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#gd_{parent_id}" xlink:label="{parent_id}" xlink:title="presentation parent: {parent_id} {parent_name}"/>\n'
                    lines.append(line)
                if not parent_id in child_count:
                    child_count[parent_id] = 0
                child_count[parent_id] += 1
                count = child_count[parent_id]
                line = f'        <link:presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="{parent_id}" xlink:to="{id}" order="{count}" xlink:title="presentation:  {parent_id} {parent_name} to {id} {name}"/>\n'
                lines.append(line)

    lines.append('  </link:presentationLink>\n')
    lines.append('</link:linkbase>\n')

    gd_presentation_file = file_path(f'{xbrl_base}{core_presentation}.xml')
    with open(gd_presentation_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if VERBOSE:
        print(f'-- {gd_presentation_file}')

    #
    # definitionLink
    #
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--(c) 2022 XBRL Japan inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldt="http://xbrl.org/2005/xbrldt" xmlns:xlink="http://www.w3.org/1999/xlink">\n',
    ]
    for role in roles:
        URI = role["URI"]
        id = role["id"]
        line = f'        <link:roleRef roleURI="http://www.xbrl.jp/gd{URI}" xlink:type="simple" xlink:href="{core_xsd}#{id}"/>\n'
        lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/all" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#all"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/domain-member" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#domain-member"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#hypercube-dimension"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/dimension-domain" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#dimension-domain"/>\n'
    lines.append(line)

    for group_id in repeatableBGs:
        if 'corG-01'==group_id:
            continue
        group = glDict[group_id]
        print(f"{group_id} {group['parent']}")
        name = group['name']
        Name = f"{name[0].upper()}{name[1:]}"
        hypercube = {'id': f'H_{Name}', 'label': Name, 'URI': roleURIs[name]}
        dimensions = []
        parent = group['parent']
        for parent_id in parent:
            name = glDict[parent_id]['name']
            Name = f"{name[0].upper()}{name[1:]}" 
            dimensions.append({'id': Name, 'label': Name})
        base_id = group_id
        root_id = 'corG-01'
        defineHypercube(hypercube['id'])

    lines.append('</link:linkbase>\n')

    gd_definition_file = file_path(f'{xbrl_base}{core_definition}.xml')
    with open(gd_definition_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if VERBOSE:
        print(f'-- {gd_definition_file}')

    # Aligned
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--(c) 2022 XBRL Japan inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldt="http://xbrl.org/2005/xbrldt" xmlns:xlink="http://www.w3.org/1999/xlink">\n',
    ]
    for role in roles:
        URI = role["URI"]
        id = role["id"]
        line = f'        <link:roleRef roleURI="http://www.xbrl.jp/gd{URI}" xlink:type="simple" xlink:href="{core_xsd}#{id}"/>\n'
        lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/all" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#all"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/domain-member" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#domain-member"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#hypercube-dimension"/>\n'
    lines.append(line)
    line = f'        <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/dimension-domain" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#dimension-domain"/>\n'
    lines.append(line)

    # # Prohibited
    # line = f'    <link:definitionLink xlink:type="extended" xlink:role="http://example.com/role/link" id="link">\n'
    # lines.append(line)
    # line = f'        <!-- all -->\n'
    # lines.append(line)
    # line = f'        <link:loc xlink:type="locator" xlink:href="eg.xsd#hc_Zero" xlink:label="hc_Zero" xlink:title="hc_Zero"/>\n'
    # lines.append(line)
    # line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/all" xlink:from="" xlink:to="hc_Zero" xlink:title="definition: FourthChild to hc_Zero" order="1" xbrldt:closed="true" xbrldt:contextElement="scenario"/>\n'
    # lines.append(line)
    # line = f'        <!-- hypercube-dimension -->\n'
    # lines.append(line)
    # line = f'        <link:loc xlink:type="locator" xlink:href="eg.xsd#dimProhibited" xlink:label="dimProhibited" xlink:title="dimProhibited"/>\n'
    # lines.append(line)
    # line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:from="hc_Zero" xlink:to="dimProhibited" xlink:title="definition: dimProhibited to dimOne" order="1"/>\n'
    # lines.append(line)
    # line = f'    </link:definitionLink>\n'
    # lines.append(line)
    
    print('-- END --')
