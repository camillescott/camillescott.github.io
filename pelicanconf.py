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

# Blogroll
LINKS =  (('GED Lab', 'http://ged.msu.edu/'), ('Titus Brown', 'http://ivory.idyll.org/blog/'))
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
You've come across, or for reasons unknown, deliberately visited, the site of Camille Scott. I'm a graduate student at Michigan State University, currently pursuing a PhD in Computer Science. I work under -- or stumble after -- <a href='http://ivory.idyll.org/blog'>Titus Brown</a>, in the <a href='http://ged.msu.edu'>Lab for Genomics, Evolution, and Development (GED)</a>.
</p>
<p>
Our lab mostly works with next gen sequence analysis, with a focus on metagenomics and transcriptomics assembly, de Bruijn graph algorithms, <a href='https://github.com/ged-lab/khmer'>k-mer counting</a>, <a href='https://khmer-protocols.readthedocs.org/'>protocol development</a>, and teaching. I like graphs -- big graphs, small graphs, dense graphs, and sparse graphs! -- and my recent work has focused on sparse de Bruijn graph labeling. I also play with the lamprey transcriptome, help out with the protocol development, help teach our <a href='http://ged.msu.edu/angus/'>bioinformatics</a> <a href='http://2013-caltech-workshop.readthedocs.org/en/latest/'>courses</a>, and occasionally, study digital evolution with <a href='http://avida.devosoft.org/'>avida</a>.
</p>
<p>
Out in the (gasp!) real world, I make music, watch too much Star Trek, rant about gender identity and transfeminism, and play cat-mom. I also have a love of Lovecraft.
</p>
<p>
I occasionally <a href='http://twitter.com/camille_codon'> tweet </a>, and I have a moderately active <a href='https://github.com/camillescott'>github</a> account. Feel free to <a href='mailto:camille.scott.w@gmail.com'>email</a> me!
</p>
'''}
