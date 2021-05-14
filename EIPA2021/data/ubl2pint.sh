#!/bin/sh
# === Initialize shell environment ===================================
set -euvx
# -e  Exit immediately if a command exits with a non-zero status.
# -u  Treat unset variables as an error when substituting.
# -v  Print shell input lines as they are read.
# -x  Print commands and their arguments as they are executed.
export LC_ALL=C
type command >/dev/null 2>&1 && type getconf >/dev/null 2>&1 &&
export PATH=".:./bin:$(command -p getconf PATH)${PATH+:}${PATH-}"
export UNIX_STD=2003  # to make HP-UX conform to POSIX
# === temporary file prefix ==========================================
Tmp=/tmp/${0##*/}.$$
# === Log ============================================================
exec 2>log/${0##*/}.$$.log
# --------------------------------------------------------------------
# seq Sem_Sort parent ID Level BT Definition Card DT Section BIS_extension Synt_Sort xPath Attrib Rules
# 1   2        3      4  5     6  7          8    9  10      11            12        13    14     15
cat pint.txt | awk -F'\t' 'BEGIN {
  OFS="\t";
  n=0;
}
{
  if (n>0 && $13!="") {
    sub(/[\n\r]/,"",$15);
    print $12,$13,$4,$5,$6,$7,$8,$9,$10,$11,$14,$15;
  }
  n=n+1;
}
' | sort > $Tmp-ubl2pint

# # Sem_Sort parent ID Level BT Definition Card DT Section BIS_extension Synt_Sort xPath Attrib Rules
# 1 2        3      4  5     6  7          8    9  10      11            12        13    14     15
# $12,      $13,  $4,$5,   $6,$7,        $8,  $9,$10,    $11,          $14,   $15;
# Synt_Sort xPath ID Level BT Definition Card DT Section BIS_extension Attrib Rules
# 1         2     3  4     5  6          7    8  9       10            11     12
# Synt_Sort xPath PINT_ID PINT_Level PINT_BT PINT_Desc PINT_Card PINT_DT Section BIS_diff Attrib Rules
# 1         2     3       4          5       6         7         8       9       10       11     12
cat $Tmp-ubl2pint | awk -F'\t' 'BEGIN { n=0; }
{
  if (n>0 && $1!="") {
    print "$.data[" n "].num",n;
    print "$.data[" n "].Path",$2;
    print "$.data[" n "].PINT_ID",$3;
    print "$.data[" n "].PINT_Level",$4;
    print "$.data[" n "].PINT_BT",$5;
    gsub(/\\n/,"<br>",$6);
    gsub(/\"/,"",$6);
    print "$.data[" n "].PINT_Desc",$6;
    print "$.data[" n "].PINT_Card",$7;
    print "$.data[" n "].PINT_DT",$8;
    sub(/[\n\r]/,"",$9);
    print "$.data[" n "].Section",$9;
    sub(/[\n\r]/,"",$10);
    print "$.data[" n "].BIS_diff",$10;
    sub(/[\n\r]/,"",$11);
    gsub(/\\n/,"<br>",$11);
    print "$.data[" n "].Attrib",$11;
    sub(/[\n\r]/,"",$12);
    gsub(/\\n/,"<br>",$12);
    print "$.data[" n "].Rules",$12;
  }
  n=n+1;
}' > $Tmp-data

cat $Tmp-data | makrj.sh | sed "s/^\(\"[^\":,]*\":\),/\1null,/" > ubl2pint.json
# --------------------------------------------------------------------
rm $Tmp-*
rm log/${0##*/}.$$.*
exit 0
# ubl2pint.sh
