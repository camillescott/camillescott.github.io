#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'CS Welcher'
SITENAME = u'At the Mountains of Madness'
SITESUBTITLE =u'a blog on the perils and wonders of bioinformatics'
SITEURL = 'http://miskatonic.ged.msu.edu'

STATIC_PATHS = ['images']

THEME = '/home/chris/pelican-chunk'

TIMEZONE = 'US/Eastern'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('GED Lab', 'http://ged.msu.edu/'), ('Titus Brown', 'http://ivory.idyll.org/blog/'))
DISPLAY_CATEGORIES_ON_MENU = True
# Social widget
SOCIAL = (()) #)(('You can', '#'),
          #('Another social link', '#'),)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
