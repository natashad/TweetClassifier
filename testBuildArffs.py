# Helper Script to build some specific arff files for testing

import subprocess
import sys

print "\nBuilding cnncbc.arff"
subprocess.call([sys.executable, 'buildarff.py',
    '-100',
    'cnn:twtts/cnn.twt',
    'cbc:twtts/CBCNews.twt',
    'arffs/cnncbc.arff'])


print "\nBuilding celebritypotpourri.arff:"
subprocess.call([sys.executable, 'buildarff.py',
    'Obama:twtts/BarackObama.twt',
    'Colbert:twtts/StephenAtHome.twt',
    'Ashton:twtts/aplusk.twt',
    'Kardashian:twtts/KimKardashian.twt',
    'NeilDT:twtts/neiltyson.twt',
    'Shakira:twtts/shakira.twt',
    'arffs/celebritypotpourri.arff'])


print "\nBuilding popstars.arff:"
subprocess.call([sys.executable, 'buildarff.py',
    'Britney:twtts/britneyspears.twt',
    'Bieber:twtts/justinbieber.twt',
    'KatyPerry:twtts/katyperry.twt',
    'Gaga:twtts/ladygaga.twt',
    'Rihanna:twtts/rihanna.twt',
    'TSwift:twtts/taylorswift13.twt',
    'arffs/popstars.arff'])

print "\nBuilding news.arff:"
subprocess.call([sys.executable, 'buildarff.py',
    'CBC:twtts/CBCNews.twt',
    'CNN:twtts/cnn.twt',
    'Star:twtts/torontostarnews.twt',
    'Reuters:twtts/Reuters.twt',
    'NYT:twtts/nytimes.twt',
    'Onion:twtts/TheOnion.twt',
    'arffs/news.arff'])

print "\nBuilding popvsnews.arff:"
subprocess.call([sys.executable, 'buildarff.py',
    'Popstars:twtts/britneyspears.twt+twtts/justinbieber.twt+twtts/katyperry.twt+twtts/ladygaga.twt+twtts/rihanna.twt+twtts/taylorswift13.twt',
    'News:twtts/CBCNews.twt+twtts/cnn.twt+twtts/torontostarnews.twt+twtts/Reuters.twt+twtts/nytimes.twt+twtts/TheOnion.twt',
    'arffs/popvsnews.arff'])