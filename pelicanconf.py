#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Camille Scott'
SITENAME = u'At the Mountains of Madness'
SITESUBTITLE =u'a blog on the perils and wonders of bioinformatics'
SITEURL = 'http://camillescott.github.io/blog'

OUTPUT_PATH = u'blog/'

TIMEZONE = 'US/Eastern'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None


# Theme related stuff
THEME = 'elegant'
#PLUGINS = ['sitemap', 'extract_toc', 'tipue_search']
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra', 'headerid', 'toc']
DIRECT_TEMPLATES = (('index', 'tags', 'categories','archives', 'search', '404'))
STATIC_PATHS = ['theme/images', 'images']
TAG_SAVE_AS = ''
CATEGORY_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
DISQUS_SITENAME = 'camillescott'
GOOGLE_ANALYTICS = 'UA-52937341-1'

# Blogroll
LINKS =  (('DIB Lab', 'http://ivory.idyll.org/lab'), ('Titus Brown', 'http://ivory.idyll.org/blog/'))
#DISPLAY_CATEGORIES_ON_MENU = True
# Social widget
SOCIAL = (()) #)(('You can', '#'),
          #('Another social link', '#'),)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

LANDING_PAGE_ABOUT = {'title': 'The Woman out of Space', 'details':
'''
<p>
You've come across, or for reasons unknown, deliberately visited, the site of
Camille Scott. I'm a graduate student at UC Davis pursuing a PhD in 
Computer Science. I work under -- or stumble after -- 
<a href='http://ivory.idyll.org/blog'>Titus Brown</a>, in the 
<a href='http://ivory.idyll.org/lab'>Lab for Data Intensive Biology</a>.
</p>

<p>
Our lab mostly works with next gen sequence analysis, with a focus on 
metagenomic and transcriptomic assembly, de Bruijn graph algorithms, 
<a href='https://github.com/ged-lab/khmer'>k-mer counting</a>, 
<a href='https://khmer-protocols.readthedocs.org/'>protocol development</a>, 
and teaching. I like graphs -- big graphs, small graphs, dense graphs, and 
sparse graphs! -- and my recent work has focused on sparse de Bruijn graph 
labeling. I also play with the lamprey transcriptome, help out with the 
protocol development, help teach our 
<a href='http://ged.msu.edu/angus/'>bioinformatics</a> 
<a href='http://2013-caltech-workshop.readthedocs.org/en/latest/'>courses</a>, 
and occasionally, study digital evolution with <a href='http://avida.devosoft.org/'>avida</a>.
</p>
<p>
Out in the (gasp!) real world, I make music, watch too much Star Trek, rant 
about gender identity and transfeminism, and play cat-mom. I also have a love of Lovecraft.
</p>
<p>
I occasionally <a href='http://twitter.com/camille_codon'> tweet </a>, and I 
have a moderately active <a href='https://github.com/camillescott'>github</a> 
account. Feel free to <a href='mailto:camille.scott.w@gmail.com'>email</a> me!
</p>
'''}

PROJECTS = [{'name': 'Lamprey RNA-Seq Project',
                'url': 'https://github.com/camillescott/2013-lamprey',
                'description': 'Pipelines and analysis for the Petromyzon marinus de novo transcriptome assembly project'},
            {'name': 'peasoup',
                'url': 'https://github.com/camillescott/peasoup',
                'description': 'Collection of pydoit tasks and utility and analysis scripts and functions for sequencing pipelines'},
            {'name': 'OARR Compendium',
                'url': 'http://camillescott.github.io/oarr-compendium',
                'description': 'Collection of links to philosophies and practices in open access and reproducible research'},
            {'name': 'My CV',
                'url': 'http://camillescott.github.io/resume',
                'description': 'My CV! (pdf)'},
            {'name': 'khmer',
                'url': 'https://github.com/ged-lab/khmer',
                'description': '[contributor] In-memory nucleotide sequence k-mer counting, filtering, graph traversal and more'},
            ]
