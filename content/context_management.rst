Practical Python: Context Managers and IPython Notebook
#######################################################
:date: 2014-05-05
:author: Camille Scott
:slug: context-managers-for-ipython
:summary: context managers for handling matplotlib figures in ipython notebook
:category: python
:tags: python, ipython, matplotlib, plotting

Recently, I've been making a lot of progress on the lamprey transcriptome project,
and that has involved a lot of IPython notebook. While I'll talk about lamprey in
a later post, I first want to talk about a nice technical tidbit I came up with
while trying to manage a large IPython notebook with lots of figures. This involved
learning some more about the internals of matplotlib, as well as the usefulness of
the `with` statement in python.

So first, some background! `matplotlib <http://matplotlib.org/index.html>`__ is
the go-to plotting package for python.  It has many weaknesses, and a whole series
of posts could be (and has been) written about why we should use something else,
but for now, its reach is long and it is widely used in the scientific community. 
It is particularly useful in concert with IPython notebook, where figures can be
embedded into cells inline. However, an important feature(?) of matplotlib is that
its built around a state machine; when it comes to deciding what figure (and other
components) are currently being worked with, matplotlib keeps track of the current
context. That allows you to just call `plot()` at any given time and have your
figures be pushed more or less where you'd like. It *also* means that you need
to keep track of the current context, lest you end up drawing a lot of figures
onto the same plot and producing a terrible abomination from beyond space and time itself.

IPython has a number of ways of dealing with this. While in its inline mode,
the default behavior is to simply create a new plotting context at the beginning
of each cell, and close it at the cell's completion. This is convenient because
it means the user doesn't have to open and close figures manually, saving a lot
of coding time. It becomes a burden, however, when you have a large notebook,
with lots of figures, some of which you don't want to be automatically displayed.
While we can turn off the automatic opening and closing of figures with

.. code:: python

    %config InlineBackend.close_figures = False

we're now stuck with having to manage our own figure context. Suddenly, our
notebooks aren't nearly as clean and beautiful as they once were, being littered
with ugly declarations of new figures and axes, calls to `gcf()` and `plt.show()`,
and other such not-pretty things. I like pretty things, so I sought out a solution.
As it tends to do, python delivered.

Enter context managers!

Some time ago, many's a programmer was running into a similar problem with
opening and closing files. To do things properly, we needed to do exception
handling to properly and cleanly call `close()` on our file
pointers when something went wrong. To handle that and a number of similar issues,
python introduced `context managers and the with statement <https://docs.python.org/2/reference/datamodel.html#context-managers>`__. From the docs::

    A context manager is an object that defines the runtime context to be established when executing a with statement. The context manager handles the entry into, and the exit from, the desired runtime context for the execution of the block of code.

Though this completely loses the ~awesomeness~ of context managers, it *does*
sound about like what we want! In simple terms, context managers are just objects
that implement the `__enter__` and `__exit__` methods. When you use the `with`
statement on one of them, `__enter__` is called, where we put our setup code
; if it returns something, it takes the name given it by `as`. `__exit__` is called after 
the `with` block is left, and contains the teardown code. For our purposes, we want
to take care of matplotlib context. Without further ado, let's look at a simple example:

.. code:: python

    import matplotlib.pyplot as plt

    class FigManager(object):

        def __init__(self, fn='', exts=['svg', 'pdf', 'png', 'eps'], 
		    show=False, nrows=1, ncols=1, 
		    figsize=(18,12), tight_layout=True,
		    **fig_kwds):
            
	    if plt.gcf():
                print 'leaving context of', repr(plt.gcf())
        
	    self.fig, self.ax = plt.subplots(nrows=nrows, 
					     ncols=ncols, 
					     figsize=figsize,									tight_layout=tight_layout, 
					     **fig_kwds)
        
	    self.fn = fn
	    self.exts = exts
	    self.show = show
        
	    assert self.fig == plt.gcf()
    
	def __enter__(self):

	    return self.fig, self.ax
    
	def __exit__(self, exc_t, exc_v, trace_b):

	    if exc_t is not None:
		print 'ERROR', exc_t, exc_v, trace_b
        
	    if self.fn:
		print 'saving figure', repr(self.fig)
		for ext in self.exts:
		    self.fig.savefig('{}.{}'.format(self.fn, ext))
        
	    if self.show:
		assert self.fig == plt.gcf()
		print 'showing figure', repr(self.fig)
		plt.show(self.fig)

	    print 'closing figure', repr(self.fig)
	    self.fig.delaxes(self.ax)
	    plt.close(self.fig)
	    del self.ax
	    del self.fig
	    print 'returning context to', repr(plt.gcf())

Let's break this down. The `__init__` actually does most of our setup here;
it takes some basic parameters to pass to `plt.subplots`, as well as some
parameters for whether we want to show the plot and whether we want to save the
result to file(s). The `__enter__` method returns the generated `figure` and
`axes` objects. Finally, `__exit__` saves the figure to the filename with the
given extensions (matplotlib uses the extension to infer the file format), and
shows the plot if necessary. It then calls `close()` on the figure, deletes
the `axes` objects from the figure, and calls `del` on both instances just
to be sure. The three expected parameters to `__exit__` are for exception
handling, which is discussed in greater detail in the docs.

Here's an example of how I used it in practice:

.. code:: python

    with FigManager('genes_per_sample', figsize=tall_size) as (fig, ax):
        
        genes_support_df.sum().plot(kind='barh', fontsize=14, color=labels_df.color, figure=fig, ax=ax)
        ax.set_title('Represented Genes per Sample')
    FileLink('genes_per_sample.svg')

That's taken directly out of the lamprey `notebook <http://nbviewer.ipython.org/github/camillescott/2013-lamprey/blob/lamp3/pub/tale_of_two_transcriptomes_compute.ipynb>`__ where I first implemented this. I usually put a filelink in there, so that
the resulting image can easily be viewed in its own tab for closer inspection.

The point is, all the normal boilerplate for handling figures is done in one line,
and the code is much more clear.
