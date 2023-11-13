#!

# gsutil rsync gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/abigail-mccleary-2023-06-04-WINDOW--1-1.jpg abigail-mccleary/

# mkdir -p names/abigail-mccleary
# gsutil cp gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/abigail-mccleary-2023-06-04-WINDOW--1-1.jpg names/abigail-mccleary



# gsutil ls gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/** |grep WINDOW |awk -F/ '{dest=$NF; gsub("-2023.*","",dest); printf "mkdir -p \"names/%s\"\ngsutil cp \"gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/%s\" \"names/%s\"\n",dest,$NF,dest}'  | tee x |bash
# bash

# python -m   smugcli.smugcli sync  names/abigail-mccleary /names

gsutil  -m rsync  -r names/ gs://citytri-marketing.appspot.com/names/
#  python -m smugcli.smugcli  sync names/aaron-epp /names/aaron-epp --folder_threads=1 --file_threads=1 --upload_threads=1
#  python -m smugcli.smugcli  sync names/ /names --folder_threads=1 --file_threads=1 --upload_threads=1

