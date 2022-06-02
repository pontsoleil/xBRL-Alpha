
# from jsonschema import validate
import json
import yaml
import sys
import csv
import re
import hashlib
import datetime

shared_file = 'JP_PINT/semantic-model/main.yaml'
jp_pint_file = 'JP_PINT/source/jp_pint.tsv'

xbrl_source = 'JP_PINT/source/head/'
xbrl_pint_head = 'xBRL-PINT-head.txt'
xbrl_pint_definition_head = 'xBRL-PINT-definition-head.txt'

xbrl_base = 'JP_PINT/taxonomy/pint/'
xbrl_pint_xsd = 'xBRL-pint-2022-12-31.xsd'
xbrl_pint_label_en = 'xBRL-pint-2022-12-31-label-en.xml'
xbrl_pint_label_ja = 'xBRL-pint-2022-12-31-label-ja.xml'
xbrl_pint_presentation = 'xBRL-pint-2022-12-31-presentation.xml'
xbrl_pint_definition = 'xBRL-pint-2022-12-31-definition.xml'

shared_yaml = None

datatypeMap = {
  'Unit Price Amount':'pint:unitPriceAmountItemType',
  'Code':'pint:codeItemType',
  'Date':'pint:dateItemType',
  'Binary object':'pint:binaryObjectItemType',
  'Time':'pint:timeItemType',
  'Identifier':'pint:identifierItemType',
  'Quantity':'pint:quantityItemType',
  'Amount':'pint:amountItemType',
  'Document Reference':'pint:documentReferenceItemType',
  'Text':'pint:textItemType',
  'Percentage':'pint:percentageItemType'
}

duplicateNames = set()
names = set()
pintDict = {}

def LC3(term):
  if not term:
    return ''
  terms = term.split(' ')
  name = ''
  for i in range(len(terms)):
    if i == 0:
      if 'TAX'==terms[i]:
        name += terms[i].lower()
      else:
        name += terms[i][0].lower() + terms[i][1:]
    else:
      name += terms[i][0].upper() + terms[i][1:]
  return name

def C3(term):
  if not term:
    return ''
  terms = term.split(' ')
  name = '_'.join(terms)
  return name

if __name__ == '__main__':
  try:
    with open(shared_file) as file:
      shared_yaml = yaml.safe_load(file)
      # print(shared_yaml)
  except Exception as e:
    print('Exception occurred while loading YAML...', file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(1)

  # ====================================================================
  # 1. jp_pint.tsv -> schema
  # SemSort,PINT_ID,Section,PINT_Card,Aligned,AlignedCard,Level,BT,BT_ja,DT,Desc,Desc_ja,Exp,Exp_ja,Example,SyntSort,element,UBLdatatype,XPath,selectors,CodeList,Occurrence,CardinalityAlignment
  records = []
  with open(jp_pint_file, encoding='utf_8', newline='') as f:
    reader = csv.reader(f, delimiter='\t')
    header = next(reader)
    header[0] = 'SemSort'
    for cols in reader:
      record = {}
      for i in range(len(cols)):
        col = cols[i]
        record[header[i]] = col.strip()
      pint_id = record['ID']
      if not pint_id:
        continue
      term = record['BT']
      if 'ibt'==pint_id[:3].lower():
        name = LC3(term)
      else:
        name = C3(term)
      type = record['DT']
      if type in datatypeMap:
        type = datatypeMap[type]
      else:
        type = 'xbrli:stringItemType'
      name = re.sub(r'[\'\(\)]','',name)
      if name in names:
        duplicateNames.add(name)
      else:
        names.add(name)
      record['name'] = name
      record['type'] = type
      record['pint_id'] = pint_id
      records.append(record)

  records = sorted(records,key=lambda x: x['SemSort'])

  for record in records:
    name = record['name']
    pint_id = record['pint_id']
    if name in duplicateNames:
      record['name'] = f'{name}_{pint_id}'
    pintDict[pint_id] = record

  lines = []
  with open(f'{xbrl_source}{xbrl_pint_head}', encoding='utf_8', newline='') as f:
    lines = f.readlines()

  for record in records:
    pint_id = record['pint_id']
    name = record['name']
    type = record['type']
    if name in duplicateNames:
      id = f'{name}{pint_id}'
    else:
      id = name
    line = f'  <element name="{pint_id}" id="{id}" type="{type}" substitutionGroup="xbrli:item" nillable="false" xbrli:periodType="instant"/>\n'
    lines.append(line)
  lines.append('</schema>')

  with open(f'{xbrl_base}{xbrl_pint_xsd}','w',encoding='utf_8', newline='') as f:
    f.writelines(lines)

  parentDict = {}
  parent = ['ibg-00']
  level = 0
  for record in records:
    pint_id = record['pint_id']
    name = record['name']
    parentDict[pint_id] = {'name':name, 'level':'', 'parent':''}
    if record['Level'] == level:
      parentDict[pint_id]['parent'] = parent[level-1]
      parent[level] = record['pint_id']
    elif record['Level'] == level+1:
      parentDict[pint_id]['parent'] = parent[level]
      level = record['level']
      if level == len(parent):
        parent.append(None)
      parent[level] = record['pint_id']
    else:
      level = int(record['Level'])
      parentDict[pint_id]['parent'] = parent[level-1]
      if level > len(parent) - 1:
        while level > len(parent) - 1:
          parent.append('')
      parent_id = record['pint_id']
      # if 'ibg'==parent_id[:3].lower():
      parent[level] = record['pint_id']
      for i in range(len(parent)):
        if i > level:
          parent[i] = None

  # labelLink EN
  lines = ['<?xml version="1.0" encoding="UTF-8"?>\n',
    '<!--  (c) 2022 XBRL Japan  inc. -->\n',
    '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
    '  <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n']
  for record in records:
    pint_id = record['pint_id']
    name = record['name']
    BT = record['BT']
    Desc = record['Desc']
    line = f'  <!-- {pint_id} {name} -->\n'
    lines.append(line)
    dt_now = datetime.datetime.now()
    hash = hashlib.sha1(dt_now.isoformat().encode()).hexdigest()
    line = f'    <link:loc xlink:type="locator" xlink:href="{xbrl_pint_xsd}#{name}" xlink:label="{name}_{hash}"/>\n'
    lines.append(line)
    line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{name}_{hash}" xlink:to="lbl_{pint_id}-en_{hash}"/>\n'
    lines.append(line)
    line = f'    <link:label xlink:type="resource" xlink:label="lbl_{pint_id}-en_{hash}" xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="en">{BT}</link:label>\n'
    lines.append(line)
    line = f'    <link:label xlink:type="resource" xlink:label="lbl_{pint_id}-en_{hash}" xlink:role="http://www.xbrl.org/2003/role/documentation" xml:lang="en">{Desc}</link:label>\n'
    lines.append(line)
  lines.append('  </link:labelLink>\n')
  lines.append('</link:linkbase>\n')
  
  with open(f'{xbrl_base}{xbrl_pint_label_en}','w',encoding='utf_8', newline='') as f:
    f.writelines(lines)

  # labelLink JA
  lines = ['<?xml version="1.0" encoding="UTF-8"?>\n',
    '<!--  (c) 2022 XBRL Japan  inc. -->\n',
    '<link:linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
    '  <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">']
  for record in records:
    pint_id = record['pint_id']
    name = record['name']
    BT = record['BT_ja']
    Desc = record['Desc_ja']
    line = f'  <!-- {pint_id} {name} -->\n'
    lines.append(line)
    dt_now = datetime.datetime.now()
    hash = hashlib.sha1(dt_now.isoformat().encode()).hexdigest()
    line = f'    <link:loc xlink:type="locator" xlink:href="{xbrl_pint_xsd}#{name}" xlink:label="{name}_{hash}"/>\n'
    lines.append(line)
    line = f'    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="{name}_{hash}" xlink:to="lbl_{pint_id}-ja_{hash}"/>\n'
    lines.append(line)
    line = f'    <link:label xlink:type="resource" xlink:label="lbl_{pint_id}-ja_{hash}" xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="ja">{BT}</link:label>\n'
    lines.append(line)
    line = f'    <link:label xlink:type="resource" xlink:label="lbl_{pint_id}-ja_{hash}" xlink:role="http://www.xbrl.org/2003/role/documentation" xml:lang="ja">{Desc}</link:label>\n'
    lines.append(line)
  lines.append('  </link:labelLink>\n')
  lines.append('</link:linkbase>\n')
  with open(f'{xbrl_base}{xbrl_pint_label_ja}','w',encoding='utf_8', newline='') as f:
    f.writelines(lines)

  #  presentationLink
  lines = ['<?xml version="1.0" encoding="UTF-8"?>\n',
    '<!--  (c) 2022 XBRL Japan  inc. -->\n',
    '<linkbase xmlns="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n',
    '<presentationLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">\n']
  for record in records:
    pint_id = record['pint_id']
    if 'ibg-00'==pint_id:
      continue
    name = record['name']
    if 'hash' in parentDict[pint_id]:
      hash = parentDict[pint_id]['hash']
    else:
      dt_now = datetime.datetime.now()
      hash = hashlib.sha1(dt_now.isoformat().encode()).hexdigest()
      line = f'    <loc xlink:type="locator" xlink:href="{xbrl_pint_xsd}#{name}" xlink:label="{name}_{hash}" xlink:title="presentation parent: {name}"/>\n'
      lines.append(line)
    parent_id = parentDict[pint_id]['parent']
    if parent_id in parentDict:
      if 'name' in parentDict[parent_id]:
        parent_name = parentDict[parent_id]['name']
      else:
        print(parent_id)
    else:
      print(parent_id)
    if not 'hash' in parentDict[parent_id]:
      dt_now = datetime.datetime.now()
      parent_hash = hashlib.sha1(dt_now.isoformat().encode()).hexdigest()
      line = f'    <loc xlink:type="locator" xlink:href="{xbrl_pint_xsd}#{parent_name}" xlink:label="{parent_name}_{parent_hash}" xlink:title="presentation parent: {parent_name}"/>\n'
      lines.append(line)
    else:
      parent_hash = parentDict[parent_id]['hash']
    line = f'    <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="{parent_name}_{parent_hash}" xlink:to="{name}_{hash}" priority="1" xlink:title="presentation: {parent_name} to {name}" use="optional"/>\n'
    lines.append(line)
  lines.append('  </presentationLink>\n')
  lines.append('</linkbase>\n')
  with open(f'{xbrl_base}{xbrl_pint_presentation}','w',encoding='utf_8', newline='') as f:
    f.writelines(lines)

  lines = []
  with open(f'{xbrl_source}{xbrl_pint_definition_head}', encoding='utf_8', newline='') as f:
    lines = f.readlines()
  # <!-- vatCategoryCode -->
  # <link:loc xlink:type="locator" xlink:href="../../cen/gl-cen-2020-12-31.xsd#gl-cen_vatCategoryCode" xlink:label="gl-cen_vatCategoryCode" xlink:title="gl-cen_vatCategoryCode"/>
  # <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="gl-cor_accountingEntries" xlink:to="gl-cen_vatCategoryCode" xlink:title="definition: gl-cor_accountingEntries to gl-cen_vatCategoryCode" order="0"/>
  for record in records:
    pint_id = record['pint_id']
    name = record['name']
    type = record['type']
    if name in duplicateNames:
      id = f'{name}{pint_id}'
    else:
      id = name
    lines.append(f'    <!-- {name} -->\n')
    line = f'    <link:loc xlink:type="locator" xlink:href="{xbrl_pint_xsd}#{name}" xlink:label="{name}" xlink:title="{name}e"/>\n'
    lines.append(line)
    line = f'    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="Invoice" xlink:to="{name}" xlink:title="definition: Invoice to {name}" order="0"/>\n'
    lines.append(line)
  lines.append('  </link:definitionLink>\n')
  lines.append('</link:linkbase>\n')
  with open(f'{xbrl_base}{xbrl_pint_definition}','w',encoding='utf_8', newline='') as f:
    f.writelines(lines)

  print('end')