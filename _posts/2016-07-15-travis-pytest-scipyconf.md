---
layout: post
title: some notes on py.test, travis-ci, and SciPy 2016
---

I've been in Austin since Tuesday for [SciPy 2016](http://scipy2016.scipy.org/ehome/index.php?eventid=146062&tabid=332930&), and
after a couple weeks in Brazil and some time off the grid in the Sierras, I can now say that I've been officially bludgeoned back into
my science and my Python. Aside from attending talks and meeting new people, I've been working on getting a little package of mine
up to scratch with tests and continuous integration, with the eventual goal of submitting it to the 
[Journal of Open Source Software](http://joss.theoj.org/). I had never used [travis-ci](https://travis-ci.org/) before, nor had I used
[py.test](http://docs.pytest.org/) in an actual project, and as expected, there were some hiccups -- 
learn from mine to avoid your own :)

Note: this blog post is not beginner friendly. For a simple intro to continuous integration, check out our [pycon tutorial](https://github.com/dib-lab/2016-pycon-tutorial/issues),
travis ci's [intro docs](https://docs.travis-ci.com/user/getting-started/), or do further googling. Otherwise, to quote Worf: ramming speed!

## travis 

Having used drone.io in the past, I had a good idea of where to start here. travis is much more feature rich than drone though, and as such,
requires a bit more configuration. My package, [shmlast](https://github.com/camillescott/shmlast), is not large, but it has some external dependencies
which need to be installed and relies on the numpy-scipy-pandas stack. drone's limited configuration options and short maximum run time quickly make it intractable
for projects with non-trivial dependencies, and this was where travis stepped in.

### getting your scientific python packages

The first stumbling block here was deciding on a python distribution. Using virtualenv and PyPI is burdensome with numpy, scipy, and pandas -- they almost always
want to compile, which takes much too long. Being an impatient page-refreshing fiend, I simply could not abide the wait. 
The alternative is to use [anaconda](https://www.continuum.io/downloads),
which does us the favor of compiling them ahead of time (while also being a little smarter about managing dependencies). The default distribution is quite large though,
so instead, I suggest using the stripped-down miniconda and installing the packages you need explicitly. Detailed instructions are available [here](http://conda.pydata.org/docs/travis.html),
and I'll run through my setup.

The miniconda setup goes under the `install` directive in your `.travis.yml`:

    install:
      - sudo apt-get update
      - if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then
          wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh;
        else
          wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
        fi
      - bash miniconda.sh -b -p $HOME/miniconda
      - export PATH="$HOME/miniconda/bin:$PATH"
      - hash -r
      - conda config --set always_yes yes --set changeps1 no
      - conda update -q conda
      - conda info -a
      - conda create -q -n test python=$TRAVIS_PYTHON_VERSION numpy scipy pandas=0.17.0 matplotlib pytest pytest-cov coverage sphinx nose
      - source activate test
      - pip install -U codecov
      - python setup.py install

Woah! Let's break it down. Firstly, there's a check of travis's python environment variable to grab the correct miniconda distribution. Then we install it, add it to `PATH`,
and configure it to work without interaction. The `conda info -a` is just a convenience for debugging. Finally, we go ahead and create the environment. I do specify a version
for Pandas; if I were more organized, I might write out a conda `environment.yml` and use that instead. After creating the environment and installing a non-conda dependency
with pip, I install the package. This gets use ready for testing.

After a lot of fiddling around, I believe this is the fastest way to get your Python environment up and running with numpy, scipy, and pandas. You can probably safely use
virtualenv and pip if you don't need to compile massive libraries. The downside is that this essentially locks your users into the conda ecosystem, unless they're
willing to risk going it alone re: platform testing.

### non-python stuff

Bioinformatics software (or more accurately, users...) often have to grind their way through the Nine Circles (or perhaps orders of magnitude) of Dependency Hell to
get software installed, and if you want CI for your project, you'll have to automate this devilish journey. Luckily, travis has extensive support for this. For example,
I was easily able to install [LAST](last.cbrc.jp) aligner from source by adding some commands under `before_script`:

    before_script:
      - curl -LO http://last.cbrc.jp/last-658.zip
      - unzip last-658.zip
      - pushd last-658 && make && sudo make install && popd

The source is first downloaded and unpacked. We need to avoid mucking up our current location when compiling, so we use `pushd` to save our directory and
move to the folder, then make and install before using `popd` to jump back out. 

Software from Ubuntu repos is even simpler. We can these commands to `before_install`:

    before_install:
      - sudo apt-get -qq update
      - sudo apt-get install -y emboss parallel

This grabbed emboss (which includes `transeq`, for 6-frame DNA translation) and gnu-parallel. These commands could probably just as easily go in the `install` section,
but the travis docs recommended they go here and I didn't feel like arguing.

## py.test

### and the import file mismatch

I've used nose in my past projects, but I'm told the cool kids (and the less-cool kids who just don't like deprecated software) are using py.test these days. Getting
some basic tests up and running was easy enough, as the patterns are similar to nose, but getting everything integrated was more difficult. Pretty soon, after
running a `python setup.py test` or even a simple `py.test`, I was running into a nice collection of these errors:

    import file mismatch:
    imported module 'shmlast.tests.test_script' has this __file__ attribute:
      /work/shmlast/shmlast/tests/test_script.py
    which is not the same as the test file we want to collect:
      /work/shmlast/build/lib/shmlast/tests/test_script.py
    HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules

All the google results for this were to threads with devs and other benevolent folks patiently explaining that you need to have unique basenames for your
test modules (I mean it's right there in the error duh), or that I needed to delete `__pycache__`. My basenames were unique and my caches clean, so something
else was afoot. An astute reader might have noticed that one of these paths given is under the `build/` directory, while the other is in the root of the repo.
Sure enough, deleting the `build/` directory fixes the problem. This seemed terribly inelegant though, and quite silly for such a common use-case.

Well, it turns out that this problem is indirectly addressed in the [docs](http://docs.pytest.org/en/latest/goodpractices.html). Unfortunately, it's 1) under the
obligatory "good practices" section, and who goes there? and 2) doesn't warn that this error can result (instead there's a somewhat confusing warning
telling you not to use an `__init__.py` in your tests subdirectory, but also that you need to use one if you want to inline your tests and distribute them
with your package). The problem is that py.test happily slurps up the tests
in the build directory as well as the repo, which triggers the expected unique basename error. The solution is to be a bit more explicit about where to find tests.

Instead of running a plain old `py.test`, you run `py.test --pyargs <pkg>`, which in clear and totally obvious language in the help is said to
make py.test "try to interpret all arguments as python packages." Clarity aside, it fixes it! To be extra double clear, you can also add a `pytest.ini` to your
root directory with a line telling where the tests are:

    [pytest]
    testpaths = path/to/tests

### organizing test data

Other than documentation gripes, py.test is a solid library. Particularly nifty are fixtures, which make it easy to abstract away more boilerplate. For example,
in the past I've use the structure of our lab's [khmer project](https://github.com/dib-lab/khmer) for grabbing test data and copying it into temp directories,
but it involves a fair amount of code and bookkeeping. With a fixture, I can easily access test data in any test, while cleaning up the garbage:

{% highlight py %}
@fixture
def datadir(tmpdir, request):
    '''
    Fixture responsible for locating the test data directory and copying it
    into a temporary directory.
    '''
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)
    data_dir = os.path.join(test_dir, 'data') 
    dir_util.copy_tree(data_dir, str(tmpdir))

    def getter(filename, as_str=True):
        filepath = tmpdir.join(filename)
        if as_str:
            return str(filepath)
        return filepath

    return getter
{% endhighlight %}

Deep in my heart of hearts I must be a functional programmer, because I'm really pleased with this. Here, we get the path to the tests directory,
and then the data directory which it contains. The test data is then all copied to a temp directory, and by the awesome raw power of closures,
we return a function which will join the temp dir with a requested filename. A better version would handle a nonexistant file, but I said *raw* power,
not *refined* and *domesticated* power. Best of all, this fixture uses another fixture, the builtin `tmpdir`, which makes sure then files get blown away
when you're done with them.

Use it as a fixture in a test in the canonical way:

{% highlight py %}
def test_test(datadir):
    test_filename = datadir('test.csv')
    assert True # professional coder on a closed course
{% endhighlight %}

Next up: thoughts on SciPy 2016!
