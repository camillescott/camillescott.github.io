---
layout: post
title: SciPy 2016 Retrospective
---

This week, I attended my first SciPy conference in Austin. I've been to the past three PyCons in Montreal and Portland,
and aside from my excitement to learn more about the great scientific Python community, I was curious to see how it
compared to the general conference I've come to know and love.

SciPy, by my accounting, is a curious microcosm of the academic open source community as a whole. It is filled with great
people doing amazing work, releasing incredible tools, and pushing the frontiers of features and accessibility in scientific
software. It is also is marked by some of the same problems as the larger community: a stark lack of gender (and other) diversity and a
surprisingly lack of consciousness of the problem. I'll start by going over some of the cool projects I learned about,
and then move in to some thoughts on the gender issue.

## Cool Stuff

### nbflow

Several new projects were announced, and several existing projects were given some needed visibility. The first I'll talk about is
[nbflow](https://github.com/jhamrick/nbflow). This is Jessica Hamrick's system for "one-button button reproducible workflows with the
Jupyter notebook and scons." In short, you can link up notebooks in build system via two special variables in the first cells of a
collection of notebooks -- `__depends__` and `__dest__` -- which contain lists of source and target filenames and
are parsed out of the JSON to automagically generate build tasks. Jessica's implementation is clean and can be pretty easily grokked with only
a few minutes of reading the code, and it's intuitive and relatively well tested. She delivered a great presentation with excellent slides and
nice demos (which all worked ;)). 

The only downside is that it uses [scons](https://bitbucket.org/scons), which isn't Python 3 compatible and isn't what *I* use, which must mean
it's bad or something. However, this turned out to be a non-issue due to the earlier point about the clean codebase: I was able to quickly
build a [pydoit](pydoit.org) module with her extractor, and she's been responsive [to the PR](https://github.com/jhamrick/nbflow/pull/5/) (thanks!).
It would be pretty easy to build modules for any number of build systems -- it only requires about 50 lines of code. I'm definitely looking forward
to using nbflow in future projects.

## JupyterLab

The Jupyter folks made a big splash with [JupyterLab](http://jupyter.org/jupyterlab/_, which is currently in alpha.. 
They've built an awesome extension API
that makes adding new functionality dead simple, and it appears they've removed many of the warts from the current Jupyter client. State is seamlessly
and quickly shipped around the system, making all the components fully live and interactive. They're calling it an IDE -- an *Interactive* Development
Environment -- and it will likely improve greatly upon the current Python data exploration workflow. It's reminiscent of Rstudio in a lot of ways,
which I think is a Good Thing; intuitive and simple interfaces are important to getting new users up and running with the language, and particularly
helpful in the classroom. They're shooting to have a 1.0 release out by next year's SciPy, emphasizing that they'll require a 1.0 to be squeaky clean.
I'll be anxiously awaiting its arrival!

## Binder

[Binder](http://mybinder.org/) might be oldish news to many people at this point, but it was great to see it represented. For those not in the know,
it allows you to spin up Jupyter notebooks on-demand from a github repo, specifying dependencies with Docker, PyPI, and Conda. This is a great boon
for reproducibility, executable papers, classrooms, and the like. 

## Altair

The first keynote of the conference was yet another plotting library, [Altair](https://github.com/ellisonbg/altair). I must admit that I was somewhat skeptical going in: the lament
and motivation behind Altair was how users have too many plotting libraries to choose from and too much complexity, and solving this problem
by introducing a new library invokes the obligatory xkcd. However, in the end, I think the move here is needed.

Altair a python interface to [vega-lite](https://github.com/vega/vega-lite): the API is a straight-forward plotting interface which spits out a vega-lite
spec to be rendered by whatever vega-compatible graphics frontend the user might like. This is a massive improvement over
the traditional way of using vega-lite, which is "simply write raw JSON(!)" It looks to have sane defaults and produce nice looking
plots with the default frontend. More important, however, is the paradigm shift they are trying to initiate: that plotting should be
driven by a declarative grammar, with the implementation details left up to the individual libraries. This shifts much of the
programming burden off the users (and on to the library developers), and would be a major step toward improving the state of Python
data visualization.

Imperative (hah!) to this shift is the library developers all agreeing to use the same grammar. Several of the major libraries (bokeh and plot.ly?)
already use bespoke internal grammars, and according to the talk, looking to adopt vega. Altair has taken the aggressive approach: the tactic seems to be
to firmly plant the graphics grammar flag and force the existing tools to adopt before they have a chance to pollute the waters with competing standards.
Somebody needed to do it, and I think it's better that vega does.

There are certainly deficiencies though. vega-lite is relatively spartan at this point -- as one questioner in the audience highlighted, it can't
even put error bars on plots. This sort of obvious feature vacuum will need to be rapidly addressed if the authors expect the spec to be adopted wholeheartedly
by the scientific python community. Given the chops behind it, I fully expect these issues to be addressed.

## Gender Stuff

I've focused on the cool stuff at the conference so far, but not everything was so rosy. Let's talk about diversity -- of the gender sort, but the complaint
applies to race, ability, and so forth.

There's no way to state this other than frankly: it was abysmal. I immediately noticed the sea of male faces, and
a friend of mine had at least one conversation with a fellow conference attendee while he had a conversation with her boobs. The Code of Conduct was
not clearly stated at the beginning of the conference, which makes a CoC almost entirely useless: it shows potential violators that the organizers don't
really prioritize the CoC and probably won't enforce it, and it signals the same to the minority groups that the conference ostensibly wants to engage
with. As an example, while [Chris Calloway](http://pydata.org/carolinas2016/about/organizers/) gave a great lightening talk about how PyData North Carolina is working through the aftermath of HB2, several older men
directly behind me giggled amongst themselves at the mention of gender neutral bathrooms. They probably didn't consider that there was a trans person sitting
right in front of them, and they certainly didn't consider the CoC, given that it was hardly mentioned. This sort of shit gives all the wrong signals 
for folks like myself. At PyCon the previous two years, I felt comfortable enough to create a #QueerTransPycon
BoF, which was well attended; although the more focused nature of SciPy makes such an event less appropriate, I would not have felt comfortable trying
regardless.

The stats are [equally bad](https://gist.github.com/jiffyclub/c1c75641b50a9370bb144f5623e177c4): 12 out of 124 speakers, 8 out of 52 poster presenters,
and 4 out of 37 tutorial presenters were women, and the stats are much worse for people of color. The lack of consciousness of the problem was highlighted
by some presenters noting the great diversity of the conference (maybe they were talking about topics?), and in one case, by the words of an otherwise well meaning man that I had a conversation
with: when the 9% speaker rate for women was pointed out to him, he pondered the number and said that it "sounded pretty good." It isn't! He further pressed
as to whether we would be satisfied once it hit 50%; [somehow the "when is enough enough?" question always comes up](https://youtu.be/SmkFX0myYU4?t=11). What's clear is
that "enough" is a lot more than 9%. This state of things isn't new -- [several](https://wrightaprilm.github.io/posts/lonely.html) folks have [written](

There are some steps that can be taken here -- organizers could look toward the PSF's successful efforts to improve the gender situation at PyCon, where funding was sought
for a paid chair (as opposed to SciPy's unpaid position). The Code of Conduct should be clearly highlighted and emphasized at the beginning of the conference.
For my part, I plan to submit a tutorial and a talk for next year.

I don't want to only focus on the bad; the diversity luncheon was well attended, there was a diversity panel, and a group has been actively discussing the issues in a dedicated channel on the
conference Slack team. These things signal that there is some will to address this. I also don't want to give any indication that things are okay -- they aren't,
and there's a ton of work to be done. 

## Closing

I'm grateful to my adviser [Titus](http://ivory.idyll.org/blog/) for paying for the trip, and generally supporting my attending events like this and rabble rousing. I'm
also grateful to the conference organizers for putting together an all-in-all good conference, and to all the funders present who make all this scientific Python software
that much more viable and robust.
For anyone reading this and thinking, "I'm doing thing X to combat the gender problem, why don't you help out?" feel free to contact me on [twitter](https://twitter.com/camille_codon).
