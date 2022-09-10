# Post classifier

Simple tool using neural network to classify short texts by pre-defined topics.
All-in-one solution

Use Python 3.8 to run

## How to get token

## How to set proxy
Use any VPN service. In Ubuntu, use such commands to redirect VK traffic to VPN:

&#35; route add -net 95.142.0.0 netmask 255.255.0.0 gw 10.66.24.80 dev vpn0

&#35; route add -net 93.186.0.0 netmask 255.255.0.0 gw 10.66.24.80 dev vpn0

&#35; route add -net 87.240.0.0 netmask 255.255.0.0 gw 10.66.24.80 dev vpn0

## Sample datasets

`short_corpus.txt` - smallest possible list of sources with diverse content and access issues

`corpus_groups.txt` - about 60 groups and 7 classes, quite ready for production usage

## Training pipeline

Included `db_tiny.json` as sample dataset. It includes 3 classes of text: films, 
music and food. Demo script `e2e.py` trains network on it for a few minutes and 
classsify several texts from test set as example. 