---
layout: post
title: Function-level fixture parametrization (or, some pytest magic)
mathjax: true
---

In my work my more recent work with de Bruijn graphs, I've been making heavy use of py.test fixtures
and parametrization to generate sequence graphs of a particular structure.
[Fixtures](https://docs.pytest.org/en/latest/fixture.html) are a wonderful bit of magic for
performing test setup and dependency injection, and their cascading nature (fixtures using
fixtures!) means a few can be recombined in myriad ways. This post will assume you've already bowed
to the wonder of fixtures and have some close familiarity with them; if not, it will appear to you
as cosmic horror -- which maybe it is, but cosmic horror never felt so good.

### The Problem

I've got a bunch of fixtures, heavily parametrized, which are all composed. For example, I have one
for generating varying flavors of our de Bruijn Graph (dBG) objects:

{% highlight py %}

@pytest.fixture(params=[khmer.Nodegraph, khmer.Countgraph],
                ids=['(Type=Nodegraph)', '(Type=Countgraph)'])
def graph(request, ksize):
    ''' Instantiate a dBG with the parametrized
    underlying dBG type.
    ''' 
    num_kmers = 50000
    target_fp = 0.00001
    args = optimal_fp(num_kmers, target_fp)

    return request.param(ksize, args.htable_size,
                         args.num_htables) 

{% endhighlight %}

For those not familiar with the dBG, for our purposes it is a graph where the nodes are sequences of length $$K$$ for some
alphabet $$\Sigma$$ (in our case, $$\Sigma = \{A, C, G, T\}$$). We draw an edge $$e_i = v_j \rightarrow v_k$$ if the
length $$K-1$$ suffix of $$v_j$$ matches the length $$K-1$$ prefix of $$v_k$$. This turns out to be highly useful when we want
take a pile of highly redundant short random samples of an underlying sequence and try to extract something close
to the underlying sequence. A more in-depth discussion of dBGs is, uh, left as an exercise to the reader -- what we
really care about here is $$K$$. It seems to be showing up often: as an argument to our dBG objects, as a way to prevent
loops and overlaps in our randomly generated sequences, and, as it turns out, all over our tests for various indexing
operations.

And so, there's also fixture for generating random nucleotide sequences that don't overlap
in a dBG of order $$K$$:

{% highlight py %}

@pytest.fixture(params=list(range(500, 1600, 500)),
                ids=lambda val: '(L={0})'.format(val))
def random_sequence(request, ksize):
    global_seen = set()
    def get(exclude=None):
        # note that the definition of get random sequence
        # is also left as an exercise to the reader
        sequence = get_random_sequence(request.param,
                                       ksize,
                                       exclude=exclude,
                                       seen=global_seen)         
        for i in range(len(sequence)-ksize):      
            global_seen.add(sequence[i:i+ksize-1])
            global_seen.add(revcomp(sequence[i:i+ksize-1]))
        return sequence

    return get

{% endhighlight %}

...and naturally, one to compose them:

{% highlight py %}
@pytest.fixture
def linear_structure(request, graph, ksize, random_sequence):
    '''Sets up a simple linear path graph structure.

    sequence
    [0]→o→o~~o→o→[-K]
    '''
    sequence = random_sequence()
    graph.consume(sequence)

    # Check for false positive neighbors in our graph:
    # this linear path should have no "high degree nodes"
    # Mark as an expected failure if any are found
    if hdn_counts(sequence, graph):
        request.applymarker(pytest.mark.xfail)

    return graph, sequence
{% endhighlight %}

You might notice a few things about these fixtures:


1. OMG you're testing with random data. Yes I am! But, the space for that data is highly constrained, it seems to be doing the job well, and I can always introspect unexpected failures.
2. The `random_sequence` fixture returns a function! This is a trick to share some state at function scope: we keep track of the global set of seen k-mers, and the resulting function can generate many sequences.
3. There's an undefined parameter or fixture: `ksize`.

The last bit is the interesting part.

So, of course, it seems we should just write a fixture for $$K$$! The simplest approach might be:

{% highlight py %}

@pytest.fixture
def ksize():
    return 21

{% endhighlight %}

This sets one default $$K$$ for each fixture and test using it. This kinda sucks though: we should be testing different
$$K$$ sizes! So...

{% highlight py %}

@pytest.fixture(params=[21, 25, 29])
def ksize(request):
    return request.param

{% endhighlight %}

Slightly better! We test three values for $$K$$ instead of one. Unfortunately, it still doesn't quite cut it: for some tests
we want more a more trivial dBG ( say with $$K=4$$), or we might not want or need to have three instances of every single test.
We need individual tests to be able to set their own $$K$$, and importantly, it still needs to trickle down to all the
fixtures the test depends on. I'd also like this to be somewhat clear and concise: turns out that what I've done here
can more or less be achieved with indirect parametrization, but I find that interface clunky (and not very well documented)
, and besides, this taught me a bit more about pytest.

### The Solution

My first thought was that it'd be nice to just set a variable within a test function and reach through the `request`
object to pull it out with `getattr`, which would produce tests something like:

{% highlight py %}

def test_something(graph, linear_structure):
    ksize = 5
    # stuff
    assert condition == True

{% endhighlight %}

Turns out this doesn't work properly with test collection and Python's scoping rules, and just feels icky to boot. We need
a way to pass some information to the fixture, while also making it clear that it's a property of the test itself and not
some detail of the test's implementation. Then I realized: decorators!

So, I came up with this:

{% highlight py %}

def using_ksize(K):
    '''A decorator to set the _ksize 
    attribute for individual tests.
    '''
    def wrap(func):                                      
        setattr(func, '_ksize', K)
        return func                                      
    return wrap

{% endhighlight %}

Pretty straightforward: all it does is add an attribute called `_ksize` to the test function. However, we need to tell
pytest and our fixtures about it. Turns out that the pytest API already has a hook for more granular control over
parametrization, called `pytest_generate_tests`. This lets us grab the fixtures being used
by whatever function pytest is currently setting up and poke at their generation in various ways. For example, in my
case...

{% highlight py %}

# goes in conftest.py

def pytest_generate_tests(metafunc):
    if 'ksize' in metafunc.fixturenames:
        ksize = getattr(metafunc.function, '_ksize', None)
        if ksize is None:
            ksize = [21]
        if isinstance(ksize, int):
            ksize = [ksize]
        metafunc.parametrize('ksize', ksize,  
                             ids=lambda k: 'K={0}'.format(k))
{% endhighlight %}

So what is this nonsense? We look at the `metafunc`, which contains the requesting context, and into its list of 
fixture names. If we find one called `ksize`, we check the calling function in `metafunc.function` for
the `_ksize` attribute; if we don't find it, we set a default value, and if we do, we just use it.

Now, we can write a couple different sorts of tests:

{% highlight py %}

def test_something_default_ksize(ksize, random_sequence):
    # do stuff...
    assert ksize == 21

@using_ksize(25)
def test_something_override_ksize(ksize, random_sequence):
    # random sequence also gets the
    # override in its ksize fixture
    assert ksize == 25

@using_ksize([21,31])
def test_something_ksize_parametrize(ksize, random_sequence):
    # this one gets properly parametrized for 21 and 31
    assert condition

{% endhighlight %}

I rather like this approach: it's quite clear and retains all the pytest fixture goodness, while also
giving more granular control. This is a simple parametrization case which admittedly could be
accomplished with `indirect` parametrization, but one could imagine scenarios where the indirect
method would be insufficient. Curiously, you don't even have to write an actual fixture function with
this approach, as its implied by the function argument lists.

In my case, I eventually get tests like...

{% highlight bash %}

tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-Start-(Type=Nodegraph)-K=21] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-Start-(Type=Nodegraph)-K=31] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-Start-(Type=Countgraph)-K=21] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-Start-(Type=Countgraph)-K=31] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-End-(Type=Nodegraph)-K=21] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-End-(Type=Nodegraph)-K=31] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-End-(Type=Countgraph)-K=21] PASSED
tests/test_compact_dbg.py::test_compact_triple_fork[(L=1500)-End-(Type=Countgraph)-K=31] PASSED

{% endhighlight %}

In the end, only mild cosmic horror.
