"""
Download all episodes of mp3 files for a series of podcasts as listed
on instantwatcher.com
chris@amow.com
"""

import sys
import lxml
import lxml.html
import requests
import urlparse
import urllib
import unidecode        # not python3 yet
import collections


def download_podcasts(url):
    """
    Download the mp3 files in the podcasts in the list on the url
    They will be named based on the title in the subpage
    """
    #initial page list of episodes
    r = requests.get(url)   
    #eg 'http://instantwatcher.com/podcasts/episodes?feed=1800&sort=pubdate%20desc')
    doc = lxml.html.fromstring(r.text)
    podlinks = doc.xpath("//a")
    playlinks = [l for l in podlinks if l.get("href").endswith('play')]

    #each subpage has a relative link to the mp3
    count, total = 1, len(playlinks)
    for plink in playlinks:
        play = requests.get('http://instantwatcher.com' + plink.get("href"))
        doc = lxml.html.fromstring(play.text)
        links = doc.xpath("//a")
        mp3link = [l.get("href") for l in links if '.mp3' in l.get("href")] 
            #can't just check endswith(), may have more in url
        if len(mp3link) < 1:
            raise ValueException('No mp3 links found. Expected scraping format may be broken')
        firstmp3 = mp3link[0]   #first one good enough

        #make local filename
        title = doc.xpath("//title")
        fname = title[0].text
        if isinstance(fname, unicode):  #unicode problems with filenames
            fname = unidecode.unidecode(fname)
        fname += '.mp3'

        #abbreviations - shorten up the name, some redundant naming
        a = collections.OrderedDict()  
            #if out of order some small subst will mess up bigger ones
        a['instantwatcher podcasts - '] = ''
        a[' - instantwatcher.com/podcasts'] = ''
        a[' '] = '_'
        a[':'] = '-'    #so no windows issues
        a['_-_'] = '-'
        for key in a:
            fname = fname.replace(key,a[key])

        print('{0} of {1} downloading {2}'.format(count, total, fname))
        urllib.urlretrieve(firstmp3, fname)
        count += 1

if __name__ == '__main__':
    download_podcasts(sys.argv[1])

