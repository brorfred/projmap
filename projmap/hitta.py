import sys, os
import traceback
import numpy as np
import pylab as pl


def projfig(label='',figno=[],lev=0,dpi=100):
    stack =  traceback.extract_stack()
    parfun = stack[-2][2]
    namefun  = stack[-2][0][:-3]
    print parfun, namefun
    print "---"
    print stack[-2]
    print "---"

    figno = pl.gcf().number
    figdir = os.getcwd() + '/figs/' + namefun + "/" + parfun + '/'
    try:
        os.makedirs(figdir)
    except OSError:
        pass
    file = '%s/fig_%02i_%s.png' % (figdir, figno, label)
    print file
    pl.savefig(file, dpi=dpi)

def WRY():
    import matplotlib as mpl
    cdict = {'red': (  (0.00, 1.0, 1.0),
                       (0.20, 1.0, 1.0),
                       (0.60, 0.3, 0.3),
                       (1.00, 1.0, 1.0)),
             'green': ((0.00, 1.0, 1.0),
                       (0.20, 0.5, 0.5),
                       (0.60, 0.0, 0.0),
                       (1.00, 1.0, 1.0)),
             'blue':  ((0.00, 1.0, 1.0),
                       (0.20, 0.4, 0.4),
                       (0.60, 0.0, 0.0),
                       (1.00, 0.4, 0.4))}
    return mpl.colors.LinearSegmentedColormap('GreenBlueRedYellow',cdict,256)

def GBRY():
    import matplotlib as mpl
    cdict = {'red': (  (0.00, 0.6, 0.6),
                       (0.20, 0.0, 0.0),
                       (0.40, 0.4, 0.4),
                       (0.50, 1.0, 1.0),
                       (0.60, 1.0, 1.0),
                       (0.80, 0.3, 0.3),
                       (1.00, 1.0, 1.0)),
             'green': ((0.00, 1.0, 1.0),
                       (0.20, 0.0, 0.0),
                       (0.40, 1.0, 1.0),
                       (0.50, 1.0, 1.0),
                       (0.60, 0.5, 0.5),
                       (0.80, 0.0, 0.0),
                       (1.00, 1.0, 1.0)),
             'blue':  ((0.00, 0.6, 0.6),
                       (0.20, 0.4, 0.4),
                       (0.40, 1.0, 1.0),
                       (0.50, 1.0, 1.0),
                       (0.60, 0.4, 0.4),
                       (0.80, 0.0, 0.0),
                       (1.00, 0.4, 0.4))}
    return mpl.colors.LinearSegmentedColormap('GreenBlueRedYellow',cdict,256)

def GBRY9010():
    import matplotlib as mpl
    cdict = {'red': (  (0.00, 0.6, 0.6),
                       (0.40, 0.0, 0.0),
                       (0.80, 0.4, 0.4),
                       (0.91, 1.0, 1.0),
                       (0.95, 1.0, 1.0),
                       (0.97, 0.3, 0.3),
                       (1.00, 1.0, 1.0)),
             'green': ((0.00, 1.0, 1.0),
                       (0.40, 0.0, 0.0),
                       (0.80, 1.0, 1.0),
                       (0.91, 1.0, 1.0),
                       (0.95, 0.5, 0.5),
                       (0.97, 0.0, 0.0),
                       (1.00, 1.0, 1.0)),
             'blue':  ((0.00, 0.6, 0.6),
                       (0.40, 0.4, 0.4),
                       (0.80, 1.0, 1.0),
                       (0.91, 1.0, 1.0),
                       (0.95, 0.4, 0.4),
                       (0.97, 0.0, 0.0),
                       (1.00, 0.4, 0.4))}
    return mpl.colors.LinearSegmentedColormap('GreenBlue90RedYellow10',cdict,256)

def GrGr():
    import matplotlib as mpl
    cdict = {'red': (  (0.00, 0.5, 0.5),
                       (1.00, 0.5, 0.5) ),
             'green': ((0.00, 0.5, 0.5),
                       (1.00, 0.5, 0.5) ),
             'blue':  ((0.00, 0.5, 0.5),
                       (1.00, 0.5, 0.5) ) }
    return mpl.colors.LinearSegmentedColormap('AllGrey',cdict,8)
