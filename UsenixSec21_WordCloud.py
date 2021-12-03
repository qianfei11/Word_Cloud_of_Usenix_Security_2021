#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import numpy as np
from wordcloud import WordCloud
import json
import os

JSON_FILE = 'UsenixSecurity21.json'
FONT = './Comic Sans MS.ttf'

urls = [
    'https://www.usenix.org/conference/usenixsecurity21/technical-sessions', 
]

papers = {}

banner = '''
 _       __               __   ________                __         ____                         
| |     / ____  _________/ /  / ____/ ____  __  ______/ /  ____  / __/                         
| | /| / / __ \/ ___/ __  /  / /   / / __ \/ / / / __  /  / __ \/ /_                           
| |/ |/ / /_/ / /  / /_/ /  / /___/ / /_/ / /_/ / /_/ /  / /_/ / __/                           
|____________/_/   \__,_/_  \____/_______/\__,_/\__,_/   \________           ___  ____ ___  ___
  / / / ________  ____  (__  __   / ___/___  _______  _______(_/ /___  __   |__ \/ __ |__ \<  /
 / / / / ___/ _ \/ __ \/ | |/_/   \__ \/ _ \/ ___/ / / / ___/ / __/ / / /   __/ / / / __/ // / 
/ /_/ (__  /  __/ / / / _>  <    ___/ /  __/ /__/ /_/ / /  / / /_/ /_/ /   / __/ /_/ / __// /  
\____/____/\___/_/ /_/_/_/|_|   /____/\___/\___/\__,_/_/  /_/\__/\__, /   /____\____/____/_/   
                                                                /____/                         

                                                                        Author: B3ale
'''

print banner

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'rb') as f:
        papers = json.loads(f.read())
else:
    for url in urls:
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, 'html.parser')
        sections = soup.select('div[class="field field-name-field-sessions-ref field-type-entityreference field-label-hidden"]')
        for section in sections:
            article_dict = {}
            section_name = section.div.div.article.h2.get_text()
            if section_name == 'Keynote Address':
                continue
            #print '[+] section_name = ' + section_name
            titles = section.div.div.article.div.find_all('h2', attrs={'class':'node-title'})
            abstracts = section.div.div.article.div.find_all('div', attrs={'class':'field field-name-field-paper-description-long field-type-text-long field-label-hidden'})
            assert len(titles) == len(abstracts)
            l = len(titles)
            #print '[+] sizeof(article_dict) = ' + str(l)
            for i in range(l):
                title = titles[i].a.get_text()
                abstract = abstracts[i].get_text()
                article_dict[title] = abstract
            papers[section_name] = article_dict
    with open(JSON_FILE, 'wb') as f:
        f.write(json.dumps(papers))

#print papers
#print papers.keys()

title_text = ''
abstract_text = ''
for section, paper in papers.items():
    for title, p in paper.items():
        try:
            title_text += title.encode() + ' '
            abstract_text += p.encode() + ' '
        except UnicodeEncodeError:
            continue

x, y = np.ogrid[:300, :300]
mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
mask = 255 * mask.astype(int)

title_wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
title_wc.generate(title_text)
title_wc.to_file('./title_cloud.png')

abstract_wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
abstract_wc.generate(abstract_text)
abstract_wc.to_file('./abstract_cloud.png')

def draw_section_cloud(section_name):
    text = ''
    for title, p in papers[section_name].items():
        try:
            text += title.encode() + ' '
            text += p.encode() + ' '
        except UnicodeEncodeError:
            continue
    wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
    wc.generate(text)
    section_name = section_name.replace(' ', '_').replace(':', '').replace(';', '').replace(',', '')
    wc.to_file(section_name + '_cloud.png')

draw_section_cloud('Attacks')
draw_section_cloud('Fuzzing')
draw_section_cloud('Malware and Program Analysis 1')
draw_section_cloud('Cryptography: Attacks')
draw_section_cloud('Cryptography and the Cloud')
draw_section_cloud('Automated Security Analysis of Source Code and Binaries')
draw_section_cloud('IoT; Specialty Networking')
draw_section_cloud('Program Analysis')

