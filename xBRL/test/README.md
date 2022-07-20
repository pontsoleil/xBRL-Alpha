# XBRL Dimensions 1.0
参考：  
[2.6 Domain-member relations and inheritance](http://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html#sec-domain-member-relations-inheritance)
## 2.6.1 Processing of multiple has-hypercube arcs
### EXAMPLE 11
example11.xsd及びexample11-def.xmlで定義したタクソノミでは、一部が仕様のように解釈されずエラーとなる箇所がある。  
example11aの組み合わせでlink1,link2,link3に分割すると仕様のように解釈された。

### EXAMPLE 12
例の中では記述されていないが、explicit memberでは、primary item (nonnum:domainItemType)1が必要である。  
`<element name="Region_abstract" id="Region_abstract" substitutionGroup="xbrli:item" nillable="false" abstract="true" type="nonnum:domainItemType" xbrli:periodType="duration"/>`  
`<element name="Prod_abstract" id="Prod_abstract" substitutionGroup="xbrli:item" nillable="false" abstract="true" type="nonnum:domainItemType" xbrli:periodType="duration"/>`  
example12.xmlの検証メッセージは、  
* XWand
[example12_xWand_message.txt](./example12_xWand_messages.txt)  
[WARNING] fje:ConsecutiveRelationshipNotFoundWarning : The consecutive arc does not exist in the extended link indicated in the xbrldt:targetRole attribute. : targetRole = http://example.com/role/prod1, role = http://example.com/role/cube3, source element = {http://example.com/dimensions}Region_abstract, target element = {http://example.com/dimensions}Region_A の警告がある  
* Arelle
[example12_Arelle_message.txt](./example12_Arelle_message.txt)  
* XML Spy
[example12_XML_Spy_message.txt](./example12_XML_Spy_message.txt)  

