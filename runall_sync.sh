#!

# gsutil rsync gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/abigail-mccleary-2023-06-04-WINDOW--1-1.jpg abigail-mccleary/
mkdir -p names/abigail-mccleary
gsutil cp gs://citytri-marketing.appspot.com/brooklyn-beach-half-marathon-10k-5k-2023-june-04/abigail-mccleary-2023-06-04-WINDOW--1-1.jpg names/abigail-mccleary
python -m   smugcli.smugcli sync  names/abigail-mccleary /names
