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
# ID Category CommonRules JapanImplementation
cat suggested_rules.txt | awk -F'\t' 'BEGIN {
  OFS="\t";
}
{ if ($3 ~ /ib[tg]-[0-9]{2,3}/) {
    x=$3;
    gsub("[A-Za-z∑=., /“”\"]*[(]", "_", $3);
    gsub("[)][A-Za-z∑=., /“”\"]*", "", $3);
    gsub("(, | or )", "_", $3);
    gsub(" ", "", $3);
    print $1,$2,$3,x,$4;
  } else {
    print $1,$2,"",$3,$4; 
  }
}' > $Tmp-rules
# ID Category PINT_IDs CommonRules JapanImplementation
cat $Tmp-rules | awk -F'\t' 'BEGIN { n=0; }
{
  if (n>0 && $1!="" && $4!="") {
    print "$.data[" n "].num",n;
    print "$.data[" n "].Rule_ID",$1;
    print "$.data[" n "].Category",$2;
    sub(/_/,"",$3);
    gsub(/_/," ",$3);
    print "$.data[" n "].PINT_IDs",$3;
    print "$.data[" n "].CommonRules",$4;
    print "$.data[" n "].JapanImplementation",$5;
  }
  n=n+1;
}' > $Tmp-data
cat $Tmp-data | makrj.sh | sed "s/^\(\"[^\":,]*\":\),/\1null,/" > suggested_rules.json

# --------------------------------------------------------------------
rm $Tmp-*
rm log/${0##*/}.$$.*
exit 0
# suggested_rules.sh