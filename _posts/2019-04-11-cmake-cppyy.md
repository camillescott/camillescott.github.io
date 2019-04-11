---
layout: post
title: "Automating The Dark Arts"
subtitle: "Packaging and Distributing cppyy-generated Python Bindings for C++ Projects with CMake and Setuptools"
mathjax: true
---

### TL;DR

I rewrote the [cppyy](https://cppyy.readthedocs.io/en/latest/index.html) CMake modules to be much more user friendly and to work using only Anaconda/PyPI packages, and to generate more feature-complete and customizable Python packages using CMake's `configure_file`, while also supporting distribution of cppyy pythonization functions. I then [rewrote](https://github.com/camillescott/cppyy-knn) the existing [k-nearest-neighbors](https://github.com/jclay/cppyy-knearestneighbors-example/) example project to use my new system, and wrote bindings generation for [bbhash](https://github.com/rizkg/BBHash) as an [example with a real library](https://github.com/camillescott/cppyy-bbhash). Finally, I wrote a [recipe](https://github.com/camillescott/cookiecutter-cppyy-cmake) for [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) to generate project templates for CMake-built cppyy bindings.

### A Bit About Bindings

I've been writing Python bindings for C++ code for a number of years now. My first experiences were with raw CPython for our lab's [khmer/oxli project](https://github.com/dib-lab/khmer); if you've ever done this before, you're aware that it's laborious, filled with boilerplate and incantations which are required but easily overlooked. After a while, we were able to convince Titus that the maintenance burden and code bloat would be much lessened by switching to [Cython](https://cython.org/) for bindings generation. After a major refactor, most of the old raw CPython was excised.

Cython, however, while powerful, is much more suited for interacting with C than C++. Its support for templates is limited (C\++11 features are only marginally supported, let alone newer features like variadic templates); it often fails with more than a few overloads; and there's no built-in mechanism for generating Python classes from templated code. Furthermore, one has to redefine the C/C\++ interface in `cdef extern` blocks in Cython `.pxd` files, before dealing with many issues converting types and dealing with encodings. In short, Cython obviates the need for a lot of the boilerplate required with raw CPython, while requiring its own boilerplate and keeping three distinct layers of code synchronized.

My own research codebase makes considerably more use of C\++11 and beyond template features than the khmer/oxli codebase, but I still wrap it in Python for easier high-level scripting and, in particular, testing. I've been working around Cython's template limitations with a jury-rigged solution: Cython files defined with [Jinja2](http://jinja.pocoo.org/docs/2.10/) templates and a hacknied template type substitution mechanism, all hooked together with my own build system written in [pydoit](http://pydoit.org/) with its own pile of half-assed code for deducing Cython compilation dependencies, a feature which setuptools for Cython currently lacks. This system has worked *surprisingly* well, regardless of my labmates' looks of horror when I describe it, but its obviously brittle. Luckily, there is a better way...

### Automatic Bindings Generation

While discussing this eldritch horror of a build system, my labmate [Luiz](https://github.com/luizirber) mentioned a project he'd heard of in passing called [cppyy](https://cppyy.readthedocs.io/en/latest/index.html). I began looking into it, and then tested it out on my project. I quickly came to the conclusion that it's the darkest bit of code art I've ever laid eyes on, and I can only assume that [Wim Lavrijsen](https://bitbucket.org/wlav/) and coauthors spent many a long night around a demon-summoning circle to bring it into existence. Regardless, when it comes to projects that so nicely solve my problems, I can work around Azazel being a core dev.

cppyy is built around the [cling](https://github.com/root-project/cling) interactive C++ interpreter, which itself grew out of the [ROOT project](https://root.cern.ch/) at CERN. It uses Clang/LLVM to generate introspection data for C++ code, and then generates and JITs bindings for use in Python. A demo and some more explanation is available on the [Python Wiki](https://wiki.python.org/moin/cppyy), though I believe the cppyy docs and their [notebook tutorial](https://bitbucket.org/wlav/cppyy/src/master/doc/tutorial/CppyyTutorial.ipynb?viewer=nbviewer&fileviewer=notebook-viewer%3Anbviewer) are more up to date.

cppyy does, to put it mildly, some damn cool shit. A few examples are:
- Python metaclasses for C++ template classes: the C++ templates become first-class objects in Python, and used the bracket operators for type selection.
- C++ namespaces as Python submodules.
- C\++17 features. It handles templates so well it can even wrap BOOST.
- Ability to pass Python functions into C++ by converting them to `std::function`!
- Cross-language inheritance. You can even override C++ pure virtual methods, or overload C++ functions, in derived classes, on the Python side
- Everything is generated lazily. This adds some startup time the first time classes are requested, but it's all JIT'd after that.

And remember that this happens automatically. Awesome!

### Meta

This post isn't meant to be a complete tutorial on cppyy. For that, you should look through the [documentation](https://cppyy.readthedocs.io/en/latest/index.html) and [tutorial](https://bitbucket.org/wlav/cppyy/src/master/doc/tutorial/CppyyTutorial.ipynb?viewer=nbviewer&fileviewer=notebook-viewer%3Anbviewer). Rather, I'm aiming to head off problems that I ran into along the way, and then provide some solutions. So, read on!

### Getting it Working

Now, with much love to our colleagues at CERN and elsewhere, my experience interacting with code written by physicists, or even touched by physicists, has been checkered at best. cppyy suffers from some of that familiar lack of tutorials and documentation, but is greatly served by an extremely responsive developer who also happens to seem like a nice person. [wlav](https://bitbucket.org/wlav/) was very helpful during my experimentation, and I thank them for that.

With that said, I'm going to go through some of the problems I ran into. Ultimately, I decided that if I was going to solve those problems for me, I ought to solve them for everybody, hence this post and the associated software.

To start testing, I immediately began trying to run the associated tools on my own code to see if I could get a few classes working. First, I would need to install cppyy, which turns out to be quite simple. Unfortunately, there is not a recent package on conda-forge, but PyPI is up-to-date, and you can install with `pip install cppyy`. This will build cppyy's modified `libcling`. 

#### Dependencies

The documentation suggested running the code through `genreflex`, which would require an interface file `#include`ing my headers and explicitly declaring any template specializations I would need. `genreflex` runs `rootcling` with a bunch of preconfigured options, which ends up calling into `clang` and hence needs properly configured includes and library paths. It's likely it will fail at first, due to being unable to find `libclang.so` or some variant; this can be solved by a `sudo apt install clang-7 libclang-7-dev`, or whatever the equivalent for your distribution. You can then go on to run `genreflex` and then compile with your system compilers as [described in the docs](https://cppyy.readthedocs.io/en/latest/dictionaries.html).

This is fine for mucking about on your own computer, but ultimately, with modern scientific software, it's desirable to get this working in a [conda](https://docs.conda.io/en/latest/) environment (and for my purposes, [bioconda](https://bioconda.github.io/)). This required a lot of trial and error, but ultimately, the necessary minimal invocation for the test of this post is:

    conda create -n cppyy-example python=3 cxx-compiler c-compiler clangdev libcxx libstdcxx-ng libgcc-ng cmake
    conda activate cppyy-example 
    pip install cppyy clang

The `cxx-compiler` and `c-compiler` packages bring in the conda-configured `gcc` and `g++` binaries, and `libcxx`, `libstdcxx-ng`, and `libgcc-ng` bring in the standard libraries. Finally, `clangdev` brings in `libclang.so`, which is needed down the line, as is the Python `clang` package. Then we install `cppyy` from PyPI with `pip`, which will build its own cling and whatnot.

At this point, you should be able to generate and build bindings, and then load the resulting dictionaries, as described.

#### Build Systems

Now that I was able to get things working, I wanted to get it fit into a proper build system. I had already decided to convert my project to CMake, and cppyy happens to include its own [cmake modules](https://cppyy.readthedocs.io/en/latest/bindings_generation.html#cmake-interface) for automating the process. Unfortunately, I rather quickly ran into issues here:

- As opposed to the documentation, which uses `genreflex` for introspection generation, followed by a call to the compiler to create a shared , the `cppyy_add_bindings` function provided by `FindCppyy.cmake` calls `rootcling` directly. This means you can't use a [selection XML](https://cppyy.readthedocs.io/en/latest/dictionaries.html#selection-files) to select and unselect C++ names to bind, and I was completely unable to get `rootcling`'s LinkDef mechanism working. This resulted in invalid code being generated, and I was ultimately unable to get it to compile.
- cppyy includes a script called `cppyy-generator` which parses your headers and provides a mapping so that a provided initializor routine can inject all the C++ bindings names into the Python module's namespace; this allows you to call `dir()` on a namespace and see what's available before the names are requested and lazily compiled. This script, however, uses the Python `clang` bindings (`pip install clang`), which need to find a `libclang.so`. You can do a `conda install clangdev` to get the dynamically linked library in a conda environment, but this will still fail, because it also needs the `clangdev` headers. The conda package tucks these away in `$CONDA_PREFIX/lib/clang/<CLANG_VERSION>/include`, which is not in any default include path, and so the provided `FindLibClang.cmake` fails. Minor modifications are not enough: if you add this directory to the provided `INCLUDE_DIRS` argument to `cppyy_add_bindings`, it will be passed to the `rootcling` and `g++` invocations as well, which will fail with all sorts of compilation and linking errors because you've just mixed up several standard library versions.
- If you get it all working, the resulting bindings library will fail to find symbols, as described [here](https://bitbucket.org/wlav/cppyy/issues/76/binding-generation-issue-on-ubuntu1604). This is because CMake needs the `LINK_WHAT_YOU_USE` directive to instruct `ld` not to drop the symbols for your C++ shared library.
- The provided `setup.py` generators provide no ability to customize for your own target. They dump a string directly to a file with only a few basic package and author options.
- There is no ability to package pythonization routines. These are sorely need to make some of the directly-generated C++ interfaces more Pythonic. The autogenerated package also lacks things like a `MANIFEST.in`.  

### Results

#### A First Pass: bbhash

So, I went about fixing these things. I took a step away from my rather more complex project, and aimed at wrapping a smaller library (which happens to be one of my dependencies), bbhash, which provides [minimal perfect hash functions](https://en.wikipedia.org/wiki/Perfect_hash_function). This also gave me the chance to learn a lot more about CMake. The results can be found on my [github](https://github.com/camillescott/cppyy-bbhash). Essentially, this implementation solves the problems listed above: it uses `genreflex` and a selection XML; it properly finds and utilizes all the conda compilers and libraries; it allows for packaging pythonizations with a discovery mechanism similar to pytest and other such packages; and it uses templates for the generation of the necessary Python package files. The end result also provides installation targets for the both the underlying C++ library and the resulting bindings. Finally, it's portable enough that I even have it running and [continuous integration](https://travis-ci.org/camillescott/cppyy-bbhash).

#### The Second pass: knn-nearest-neighbors-example

The bbhash example above, while more complex than the existing [toy example](https://github.com/jclay/cppyy-knearestneighbors-example), does not use a dynamically linked library: rather, the underling header-only library is stuck into a static library and bundled directly into the bindings' shared library. I figured I should also apply my work to the existing example, and at the same time fix the [previously mentioned issue](https://bitbucket.org/wlav/cppyy/issues/76/binding-generation-issue-on-ubuntu1604), so I went ahead and used the same project structure from cppyy-bbhash for a new [knn-example](https://github.com/camillescott/cppyy-knn). This time, a shared library is created for the underlying C++, and dynamically linked to the bindings library.

#### The Third pass: a cookiecutter template

Now that I'd worked out most of the kinks, I figured I ought to make usage a bit easier. So, I created a [cookiecutter recipe](https://github.com/camillescott/cookiecutter-cppyy-cmake) that will sketch out a basic project structure with my CMake modules and packaging templates. This is a work in progress, but is sufficient to reproduce the previous two repositories.


### *fin.* Well, not really.

![](https://superherojunky.com/wp-content/uploads/2018/12/rest.gif)

I plan to continue work on improving the cookiecutter template and ironing out any more kinks. And of course, I now have to finish applying this work to my own project, as I set out to do in the first place! Finally, I plan on working up a conda recipe demonstrating distribution, so that hopefully, one will soon be able to do a simple `conda install mybindings`. Look for a future post on that front :)

If you got this far, thanks for your patience and happy hacking!
