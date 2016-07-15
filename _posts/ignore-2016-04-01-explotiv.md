---
layout: post
title: experimenting with a new visualization method&#58; explotiv!
---

## Intro

Every day, I get google scholar alerts regarding de novo transcriptome projects. The paper titles
are usually along the lines of "de novo assembly of the *Crittery critterus* transcriptome enables
insights into some genes." They gather some RNA-seq, assemby it with Trinity or SOAP or whatever
assembler their tech (or grad student) prefers, annotate with homology searches, find ORFs, generate
some tables and venn diagrams, and off it goes. There's nothing particularly wrong with this sort of
paper -- I'm all for gathering sequence data and making more transcriptomes available -- but as someone
interested in sequence data, assemblers, annotators, and just what pops out of them, it can be
difficult for me to really grasp just what is in a transcriptome as a whole and how they compare to each other.
I think part of this is the lack of a canonical visualization; I can't open up one of these papers and
find a succinct representation of the *entire* transcriptome. Perhaps such a thing isn't actually needed;
perhaps such a thing isn't even possible. Trying to do so seemed interesting though, so I ran with it.

With some help from my friend [Russell](https://github.com/ryneches) while we quaffed some fermented 
science-juice at the Davis Beer Shoppe, I sketched out a potential method. The basic idea was to take a 
really big protein database and a really big phylogenetic tree, find the set of all protein matches in the
database for each transcript, and then score each node in the tree by the quality of the matches to its 
proteins. I like data and unrealistic expectations, so ideally, this tree would be *the*
tree (the entire tree of life), and the protein database would be *the* database (ie all of them). If the 
transciptome were "good," one should be able to easily guess the source species just by observing the scores;
if the transcriptome were "bad" (or contaminated), the scores would be homogenous, or even highlight the
wrong clade on the tree of life. Assign colors to the scores,
plot the tree nicely (perhaps as a sunburst!), and bang, you get a plot which is certainly pretty and
maybe even useful.

This spring, I went ahead and implemented a prototype. Keeping with my tradition
of not taking software names [too](https://github.com/camillescott/dammit) 
[seriously](https://github.com/camillescott/barf), I named it 
[explotiv](https://github.com/camillescott/explotiv) -- it's dammit's companion
and consumes its output. Without further ado, here's an example generated from a fish
transcriptome {% cite dryad_7sj8s %} I pulled from data dryad.

{% figure Squalius_pyrenaicus svg 'Example generated from the *Squalius pyrenaicus* transcriptome' %}

Huzzah, it's a fish! During normal use this plot is interactive, and hovering over a cell in the 
sunburst shows the taxonomic name and score. The tree has one leaf node for each species represented 
in the database, and the internal structure corresponds to the tree induced by the 
NCBI Taxonomic Database {% cite sayers_database_2009 %}. 

## Details

### Scoring

For the initial prototype, I'm using [OrthoDB v8](http://orthodb.org/) 
{% cite kriventseva_orthodb_2015 %}, which is a hierarchical catelogue of orthologs; it is reasonably sized,
and has well-curated proteins from 400 species. The tree was generated from the NCBI Taxonomy using
[this](http://phylot.biobyte.de/) nifty tool to take the subset induced by the species present in OrthoDB,
and can be found in JSON format 
[here](https://raw.githubusercontent.com/camillescott/explotiv/master/static/odb8_tree.json). No doubt
some phylogenetics dweeb just sniffed the air and said, "JSON? Tourist bioinformatician scum!" followed
quickly by, "that's not a phylogeny, that's a taxonomy! To the stake with her!" To address
these two concerns: 1) JSON does nicely, thanks, and 2) I'm aware, and future versions will work
with a real phylogenetic tree. 

Calculating the scores works as follows: first, align the transcripts to the database with 
LAST {% cite kielbasa_adaptive_2011 sheetlin_frameshift_2014 %}. Transform the alignment e-values
to P-values ($$P = e^{-E}$$), which are easier to work with. Then, for each transcript, take the
set of alignments and assign the alignment
score to the node corresponding to the subject, which will be a leaf. These scores are then propogated up the
tree, with the score of an internal node being the sum of its descendents' scores divided by the sum of
its descendants branch lengths (with the prototype base tree, these are all 1; ie, the internal nodes
score is the mean of its descendants' scores). The score from the transcript is added to the node's list
of scores from all transcripts, and when the process is complete, each node has a "probability mass" of
sorts (currently it's not actually a probability, which will be ammended in the future). In other words,
for $$N$$ transcripts and $$M$$ nodes in our tree, we get an $$N \times M$$ matrix of scores $$M_s$$ to do
things with like make pretty plots or take on dates (or whatever it is mathematicians do with matrices
all the time). 

### Web Stuff

The visualization generated using D3 and plot.ly, with data munging done in the background 
via a simple flask server. As a side note, I found that it's quite easy to use HDF5 and
[pandas](http://pandas.pydata.org/) as a simple, super high performance "database" with flask,
which I may write up a separate post about. Insert a standard complaint about Javascript being
transdimensional language clusterfuck (but at least its fast!).

## Demo

This would be silly without a live demo, so I have one running [here]() on an AWS instance. This
is just a micro, so please be kind to it.

## Thoughts


## References

Credit where credit is due.

{% bibliography -f explotiv --cited %} 
