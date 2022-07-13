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
from distutils.debug import DEBUG
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
SEP = os.sep

shared_file = 'PINT_xBRL/semantic-model/main.yaml'
shared_file = shared_file.replace('/', SEP)
jp_pint_file = 'source/jp_pint.tsv'
# jp_pint_file = 'PINT_xBRL/source/jp_pint.txt'
jp_pint_file = jp_pint_file.replace('/', SEP)

xbrl_source = 'source/head/'
xbrl_source = xbrl_source.replace('/', SEP)
core_head = 'core-head.txt'

xbrl_base = 'taxonomy/pint/'
xbrl_base = xbrl_base.replace('/', SEP)
core_xsd = 'core.xsd'
core_label = 'core-label.xml'
core_presentation = 'core-presentation.xml'
core_definition = 'core-definition.xml'

shared_yaml = None

datatypeMap = {
  'Unit Price Amount': 'pint:unitPriceAmountItemType',
  'Code': 'pint:codeItemType',
  'Date': 'pint:dateItemType',
  'Binary object': 'pint:binaryObjectItemType',
  'Binary Object': 'pint:binaryObjectItemType',
  'Time': 'pint:timeItemType',
  'Identifier': 'pint:identifierItemType',
  'Quantity': 'pint:quantityItemType',
  'Amount': 'pint:amountItemType',
  'Document Reference': 'pint:documentReferenceItemType',
  'Text': 'pint:textItemType',
  'Percentage': 'pint:percentageItemType'
}

duplicateNames = set()
names = set()
# pintDict = {}


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

def defineHyperqube(taxCategory):
    global core_xsd
    global base_id
    global root_id
    global pint_id
    global hypercube
    global dimensions
    global child_count
    global lines

    URI = hypercube["URI"]
    line = f'    <link:definitionLink xlink:type="extended" xlink:role="http://www.xbrl.jp/peppol/invoice{URI}">\n'
    lines.append(line)
    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{root_id}" xlink:label="{root_id}" xlink:title="{root_id}"/>\n'
    lines.append(line)
    if base_id!=root_id:
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{root_id}" xlink:to="{base_id}" xlink:title="definition: ibg-00 to {base_id}" order="1.0"/>\n'
        lines.append(line)
    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{base_id}" xlink:label="{base_id}" xlink:title="{base_id}"/>\n'
    lines.append(line)

    if taxCategory:
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategoryCode" xlink:label="TaxCategoryCode" xlink:title="TaxCategoryCode"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_ConsumptionTax" xlink:label="TaxCategoryAbstract" xlink:title="TaxCategoryAbstract"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/dimension-domain" xlink:from="TaxCategoryCode" xlink:to="TaxCategoryAbstract" xlink:title="definition: TaxCategoryCode to TaxCategoryAbstract" order="1.0"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategory_S10" xlink:label="TaxCategory_S10" xlink:title="TaxCategory_S10"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="TaxCategoryAbstract" xlink:to="TaxCategory_S10" xlink:title="definition: TaxCategoryAbstract to TaxCategory_S10" order="1.0"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategory_AA8" xlink:label="TaxCategory_AA8" xlink:title="TaxCategory_AA8"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="TaxCategoryAbstract" xlink:to="TaxCategory_AA8" xlink:title="definition: TaxCategoryAbstract to TaxCategory_AA8" order="2.0"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategory_E0" xlink:label="TaxCategory_E0" xlink:title="TaxCategory_E0"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="TaxCategoryAbstract" xlink:to="TaxCategory_E0" xlink:title="definition: TaxCategoryAbstract to TaxCategory_E0" order="3.0"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategory_G0" xlink:label="TaxCategory_G0" xlink:title="TaxCategory_G0"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="TaxCategoryAbstract" xlink:to="TaxCategory_G0" xlink:title="definition: TaxCategoryAbstract to TaxCategory_G0" order="4.0"/>\n'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_TaxCategory_O0" xlink:label="TaxCategory_O0" xlink:title="TaxCategory_O0"/>\n'
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="TaxCategoryAbstract" xlink:to="TaxCategory_O0" xlink:title="definition: TaxCategoryAbstract to TaxCategory_O0" order="5.0"/>\n'

    child_count = {}
    base = pintDict[base_id]
    if 'children' in base and len(base['children']) > 0:
        for pint_id in base['children']:
            if base_id in repeatables and pint_id in repeatables[base_id]:
                continue
            parent_id = pintDict[pint_id]['parent'][-1]
            if parent_id != base_id:
                line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{parent_id}" xlink:label="{parent_id}" xlink:title="{parent_id}"/>\n'
                lines.append(line)
            line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{pint_id}" xlink:label="{pint_id}" xlink:title="{pint_id}"/>\n'
            lines.append(line)
            if not parent_id in child_count:
                child_count[parent_id] = 0
            count = 1 + child_count[parent_id]
            line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="{parent_id}" xlink:to="{pint_id}" xlink:title="definition: {parent_id} to {pint_id}" order="{count}.0"/>\n'
            lines.append(line)
    # all
    line = '        <!-- all -->\n'
    lines.append(line)
    if not base_id in child_count:
        child_count[base_id] = 0
    count = 1 + child_count[base_id]
    line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{hypercube["id"]}" xlink:label="{hypercube["label"]}" xlink:title="{hypercube["label"]}"/>\n'
    lines.append(line)
    line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/all" xlink:from="{base_id}" xlink:to="{hypercube["label"]}" xlink:title="definition: {base_id} to {hypercube["label"]}" order="{count}.0" xbrldt:closed="true" xbrldt:contextElement="scenario"/>\n'
    lines.append(line)
    if DEBUG:
        print(f'definition: {base_id} to {hypercube["label"]} all')
    # hypercube-dimension
    line = '        <!-- hypercube-dimension -->\n'
    lines.append(line)
    for dimension in dimensions:
        if not hypercube["label"] in child_count:
            child_count[hypercube["label"]] = 0
        count = 1 + child_count[hypercube["label"]]
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{dimension["id"]}" xlink:label="{dimension["label"]}" xlink:title="{dimension["label"]}"/>\n'
        lines.append(line)
        line = f'        <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:from="{hypercube["label"]}" xlink:to="{dimension["label"]}" xlink:title="definition: {hypercube["label"]} to {dimension["label"]}" order="{count}.0"/>\n'
        lines.append(line)
        if DEBUG:
            print(f'definition: {hypercube["label"]} to {dimension["label"]} hypercube-dimension')
    line = '    </link:definitionLink>\n'
    lines.append(line)


if __name__ == '__main__':
    try:
        shared_file = file_path(shared_file)
        with open(shared_file) as file:
            shared_yaml = yaml.safe_load(file)
            # print(shared_yaml)
    except Exception as e:
        print('Exception occurred while loading YAML...', file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    # ====================================================================
    # 1. jp_pint.txt -> schema
    # SemSort,PINT_ID,Section,PINT_Card,Aligned,AlignedCard,Level,BT,BT_ja,DT,Desc,Desc_ja,Exp,Exp_ja,Example,SyntSort,element,UBLdatatype,XPath,selectors,CodeList,Occurrence,CardinalityAlignment
    records = []
    jp_pint_file = file_path(jp_pint_file)
    with open(jp_pint_file, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        header = ['SemSort', 'ID', 'Section', 'PINTCard', 'Aligned', 'AlignedCard', 'level', 'BT', 'BT_ja', 'DT', 'Desc', 'L', 'Desc_ja', 'N', 'Example',
            'SyntSort', 'element', 'UBLdatatype', 'XPath', 'selectors', 'Codelist', 'UBLOcc', 'CAR', 'AlignedRule', 'SharedRule', 'CodelistRule', 'PooledRule', 'AC']
        for cols in reader:
            record = {}
            for i in range(len(cols)):
                col = cols[i]
                record[header[i]] = col.strip()
            pint_id = record['ID']
            if not pint_id:
                continue
            #     pint_id = 'ibg-00'
            #     record['ID'] = pint_id
            if not record['level']: record['level'] = 0
            if not record['PINTCard']: record['PINTCard'] = '1..1'
            if not record['AlignedCard']: record['AlignedCard'] = '1..1'
            if not record['UBLOcc']: record['UBLOcc'] = '1..1'
            term = record['BT']
            if 'ibt' == pint_id[:3].lower():
                name = LC3(term)
            else:
                name = SC(term)
            type = record['DT']
            if type in datatypeMap:
                type = datatypeMap[type]
            else:
                type = 'xbrli:stringItemType'
            name = re.sub(r'[\'\(\)]', '', name)
            if name in names:
                duplicateNames.add(name)
            else:
                names.add(name)
            record['name'] = name
            record['type'] = type
            record['pint_id'] = pint_id
            records.append(record)

    records = sorted(records, key=lambda x: x['SemSort'])

    pintDict = {}
    for record in records:
        name = record['name']
        pint_id = record['ID']
        record['level'] = int(record['level'])
        if name in duplicateNames:
            record['name'] = f'{name}_{pint_id}'
        pintDict[pint_id] = record

    parent = ['ibg-00']
    level = 0
    for pint_id, record in pintDict.items():
        level = record['level']
        if level > len(parent) - 1:
            parent.append('')
        for i in range(len(parent)):
            if i > level:
                parent.pop(-1)
        parent[level] = pint_id
        pintDict[pint_id]['parent'] = parent[:-1]
        pintDict[pint_id]['level'] = level
    if DEBUG:
        print(f"{pint_id} parent:{pintDict[pint_id]['parent']}")

    # pintDict['ibg-00'] = {'SemSort':'1000','ID':'ibg-00','BT':'Invoice','BT_ja':'請求書','SynSort':'1000','element':'ubl:Invoice','XPath':'/ubl:Invoice'}

    for k, v in pintDict.items():
        if 'parent' in v:
            if len(v['parent']) > 1:
                parent_id = v['parent'][-2]
                if not 'children' in pintDict[parent_id]:
                    pintDict[parent_id]['children'] = [k]
                else:
                    pintDict[parent_id]['children'].append(k)

    repeatables = {}
    for pint_id, record in pintDict.items():
        if 'AlignedCard' in record and 'n' == record['AlignedCard'][-1]:
            parent_id = record['parent'][-1]
            if DEBUG:
                print(f"{pint_id} {record['AlignedCard']} parent:{parent_id}")
            if not parent_id in repeatables:
                repeatables[parent_id] = [pint_id]
            else:
                repeatables[parent_id].append(pint_id)
    if DEBUG:
        print(repeatables)

    lines = []
    head_file = file_path(f'{xbrl_source}{core_head}')
    with open(head_file, encoding='utf_8', newline='') as f:
        lines = f.readlines()

    for record in records:
        pint_id = record['pint_id']
        name = record['name']
        type = record['type']
        if 'ibg' in pint_id:
            line = f'    <element name="{pint_id}" id="pint_{pint_id}" type="xbrli:stringItemType" nillable="true" abstract="true" substitutionGroup="xbrli:item" xbrli:periodType="instant"/>\n'
        else:
            line = f'    <element name="{pint_id}" id="pint_{pint_id}" type="{type}" nillable="false" substitutionGroup="xbrli:item" xbrli:periodType="instant"/>\n'
        lines.append(line)

    line = '</schema>'
    lines.append(line)

    pint_xsd_file = file_path(f'{xbrl_base}{core_xsd}')
    with open(pint_xsd_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if DEBUG:
        print(f'-- {pint_xsd_file}')

    #
    # labelLink
    #
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--  (c) 2022 XBRL Japan  inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
        '  <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n'
    ]
    for record in records:
        pint_id = record['pint_id']
        name = record['name']
        BT = record['BT']
        BT_ja = record['BT_ja']
        Desc = record['Desc']
        Desc_ja = record['Desc_ja']
        line = f'  <!-- {pint_id} {name} -->\n'
        lines.append(line)
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{pint_id}" xlink:label="{pint_id}" xlink:title="{pint_id}"/>\n'
        lines.append(line)
        # BT
        line = f'    <link:label xlink:type="resource" xlink:label="label_{pint_id}" xlink:title="label_{pint_id}" id="label_{pint_id}" xml:lang="en" xlink:role="http://www.xbrl.org/2003/role/label">{BT}</link:label>\n'
        lines.append(line)
        line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{pint_id}" xlink:to="label_{pint_id}" xlink:title="label: {pint_id} to label_{pint_id}"/>\n'
        lines.append(line)
        # BT_ja
        line = f'    <link:label xlink:type="resource" xlink:label="label_{pint_id}_2" xlink:title="label_{pint_id}" id="label_{pint_id}_2" xml:lang="ja" xlink:role="http://www.xbrl.org/2003/role/label">{BT_ja}</link:label>\n'
        lines.append(line)
        line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{pint_id}" xlink:to="label_{pint_id}_2" xlink:title="label: {pint_id} to label_{pint_id}"/>\n'
        lines.append(line)
        # Desc
        if BT!=Desc:
            line = f'    <link:label xlink:type="resource" xlink:label="label_{pint_id}_3" xlink:title="label_{pint_id}" id="label_{pint_id}_3" xml:lang="en" xlink:role="http://www.xbrl.org/2003/role/label">{Desc}</link:label>\n'
            lines.append(line)
            line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{pint_id}" xlink:to="label_{pint_id}_3" xlink:title="label: {pint_id} to label_{pint_id}"/>\n'
            lines.append(line)
        # Desc_ja
        if BT_ja!=Desc_ja:
            line = f'    <link:label xlink:type="resource" xlink:label="label_{pint_id}_4" xlink:title="label_{pint_id}" id="label_{pint_id}_4" xml:lang="ja" xlink:role="http://www.xbrl.org/2003/role/label">{Desc_ja}</link:label>\n'
            lines.append(line)
            line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{pint_id}" xlink:to="label_{pint_id}_4" xlink:title="label: {pint_id} to label_{pint_id}"/>\n'
            lines.append(line)

    lines.append('  </link:labelLink>\n')
    lines.append('</link:linkbase>\n')

    pint_label_file = file_path(f'{xbrl_base}{core_label}')
    with open(pint_label_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if DEBUG:
        print(f'-- {pint_label_file}')

    #
    #   presentationLink
    #
    child_count = {}
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--  (c) 2022 XBRL Japan  inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">\n',
        '  <link:roleRef roleURI="http://www.xbrl.jp/peppol/invoice" xlink:type="simple" xlink:href="core.xsd#invoice"/>\n',
        '  <link:presentationLink xlink:type="extended" xlink:role="http://www.xbrl.jp/peppol/invoice">\n',
        '        <link:loc xlink:type="locator" xlink:href="core.xsd#pint_ibg-00" xlink:label="pint_ibg-00"/>\n'
    ]
    for record in records:
        pint_id = record['pint_id']
        if 'ibg-00' == pint_id:
            continue
        name = record['name']
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{pint_id}" xlink:label="{pint_id}" xlink:title="presentation: {pint_id} {name}"/>\n'
        lines.append(line)
        parent_id = record['parent']
        if parent_id:
            parent_id = parent_id[-1]
        if parent_id and parent_id in pintDict:
            parent = pintDict[parent_id]
        else:
            print(pint_id)
        if parent:
            if 'name' in parent:
                parent_name = parent['name']
            else:
                parent_name = 'Invoice'
        line = f'        <link:loc xlink:type="locator" xlink:href="{core_xsd}#pint_{parent_id}" xlink:label="{parent_id}" xlink:title="presentation parent: {parent_id} {parent_name}"/>\n'
        lines.append(line)
        if not parent_id in child_count:
            child_count[parent_id] = 0
        count = 1 + child_count[parent_id]
        line = f'    <link:presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="{parent_id}" xlink:to="{pint_id}" order="{count}.0" xlink:title="presentation:  {parent_id} {parent_name} to {pint_id} {name}"/>\n'
        lines.append(line)

    lines.append('  </link:presentationLink>\n')
    lines.append('</link:linkbase>\n')

    pint_presentation_file = file_path(f'{xbrl_base}{core_presentation}')
    with open(pint_presentation_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if DEBUG:
        print(f'-- {pint_presentation_file}')

    #
    # definitionLink
    #uris
    roles = [
        {'URI':'','id':'invoice'},
        {'URI':'/Line','id':'invoiceLine'},
        {'URI':'/taxCategory','id':'invoiceTaxCategory'},
        {'URI':'/additionalSupportingDocuments','id':'additionalSupportingDocument'},
        {'URI':'/documentAllowance','id':'documentAllowance'},
        {'URI':'/documentCharge','id':'documentCharge'},
        {'URI':'/invoiceTerm','id':'invoiceTerm'},
        {'URI':'/lineAllowance','id':'lineAllowance'},
        {'URI':'/lineCharge','id':'lineCharfge'},
        {'URI':'/paidAmount','id':'paidAmount'},
        {'URI':'/preceedingInvoiceReference','id':'preceedingInvoiceReference'},
        {'URI':'/itemAttribute','id':'itemAttribute'},
        {'URI':'/paymentInstruction','id':'paymentInstruction'}
    ]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!--(c) 2022 XBRL Japan  inc. -->\n',
        '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldt="http://xbrl.org/2005/xbrldt" xmlns:xlink="http://www.w3.org/1999/xlink">\n',
    ]
    for role in roles:
        URI = role["URI"]
        id = role["id"]
        line = f'  <link:roleRef roleURI="http://www.xbrl.jp/peppol/invoice{URI}" xlink:type="simple" xlink:href="{core_xsd}#{id}"/>\n'
        lines.append(line)

    line = f'  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/all" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#all"/>\n'
    lines.append(line)
    line = f'  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/domain-member" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#domain-member"/>\n'
    lines.append(line)
    line = f'  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#hypercube-dimension"/>\n'
    lines.append(line)
    line = f'  <link:arcroleRef arcroleURI="http://xbrl.org/int/dim/arcrole/dimension-domain" xlink:type="simple" xlink:href="http://www.xbrl.org/2005/xbrldt-2005.xsd#dimension-domain"/>\n'
    lines.append(line)

    URIs = {
        'invoice':'',
        'invoiceLine':'/Line',
        'invoiceTaxCategory':'/taxCategory',
        'additionalSupportingDocument':'/additionalSupportingDocuments',
        'documentAllowance':'/documentAllowance',
        'documentCharge':'/documentCharge',
        'invoiceTerm':'/invoiceTerm',
        'lineAllowance':'/lineAllowance',
        'lineCharge':'/lineCharge',
        'paidAmount':'/paidAmount',
        'preceedingInvoiceReference':'/preceedingInvoiceReference',
        'itemAttribute':'/itemAttribute',
        'paymentInstruction':'/paymentInstruction'
    }
    # Invoice
    hypercube = {'id': 'H_invoice', 'label': 'invoice', 'URI': URIs['invoice']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'}
    ]
    base_id = 'ibg-00'
    root_id = 'ibg-00'
    taxCategory = False
    defineHyperqube(taxCategory)

    # InvoiceLine
    hypercube = {'id': 'H_invoiceLine', 'label': 'invoiceLine', 'URI': URIs['invoiceLine']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'},
        {'id': 'InvoiceLineID', 'label': 'InvoiceLineID'},
        {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-25'
    root_id = 'ibg-25'
    taxCategory = True
    defineHyperqube(taxCategory)

    # taxBreakdown
    hypercube = {'id': 'H_taxBreakdown', 'label': 'taxBreakdown', 'URI': URIs['invoiceTaxCategory']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'},
        {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-23'
    root_id = 'ibg-00'
    taxCategory = True
    defineHyperqube(taxCategory)

    # invoiceAllowance
    hypercube = {'id': 'H_invoiceAllowance', 'label': 'invoiceAllowance', 'URI': URIs['documentAllowance']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'},
        {'id': 'DocumentAllowance', 'label': 'DocumentAllowance'},
        {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-20'
    root_id = 'ibg-00'
    taxCategory = True
    defineHyperqube(taxCategory)

    # invoiceCharge
    hypercube = {'id': 'H_invoiceCharge', 'label': 'invoiceCharge', 'URI': URIs['documentCharge']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'},
        {'id': 'DocumentCharge', 'label': 'DocumentCharge'},
        {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-21'
    root_id = 'ibg-00'
    taxCategory = True
    defineHyperqube(taxCategory)

    # lineAllowance
    hypercube = {'id': 'H_lineAllowance', 'label': 'lineAllowance', 'URI': URIs['lineAllowance']}
    dimensions = [
        {'id': 'InvoiceLineID', 'label': 'InvoiceLineID'},
        {'id': 'LineAllowance', 'label': 'LineAllowance'}
        # {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-28'
    root_id = 'ibg-25'
    taxCategory = False
    defineHyperqube(taxCategory)

    # lineCharge
    hypercube = {'id': 'H_lineCharge', 'label': 'lineCharge', 'URI': URIs['lineCharge']}
    dimensions = [
        {'id': 'InvoiceLineID', 'label': 'InvoiceLineID'},
        {'id': 'LineCharge', 'label': 'LineCharge'}
        # {'id': 'TaxCategoryCode', 'label': 'TaxCategoryCode'}
    ]
    base_id = 'ibg-27'
    root_id = 'ibg-25'
    taxCategory = False
    defineHyperqube(taxCategory)

    # paymentInstruction
    hypercube = {'id': 'H_paymentInstruction', 'label': 'paymentInstruction', 'URI': URIs['paymentInstruction']}
    dimensions = [
        {'id': 'InvoiceID', 'label': 'InvoiceID'},
        {'id': 'PaymentInstruction', 'label': 'PaymentInstruction'}
    ]
    base_id = 'ibg-16'
    root_id = 'ibg-00'
    taxCategory = True
    defineHyperqube(taxCategory)

    # lines.append('  </link:definitionLink>\n')
    lines.append('</link:linkbase>\n')

    pint_definition_file = file_path(f'{xbrl_base}{core_definition}')
    with open(pint_definition_file, 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)
    if DEBUG:
        print(f'-- {pint_definition_file}')

    print('end')
