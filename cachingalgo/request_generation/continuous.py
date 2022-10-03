from collections import deque
import numpy as np
import time
import pickle
from pathlib import Path

class StaticZipf:
    def __init__(self, L, a):
        """
        L is the Library Size
        a is the shape parameter of the Zipf distribution
        """
        self.L = L
        self.a = a
        self.prob = self.zipf(L, a)

    def req_gen(self, count):
        """
        Generates the 'count' no. of requests according to self.prob
        """
        items = list(range(self.L))
        req = np.random.choice(items, p = self.prob, size = count)
        return req

    def zipf(self, n, a):
        """
        n is the size
        a is the shape factor
        pdf of X, fx(X) = c/(x^a) where c = summation of (1/i)^a where i runs from 1 to n
        To get the top one element one has to substitute x = 1 and vice versa
        """
        x = sum([(1/i)**a for i in range(1,n+1)])
        y = [None]*n
        for i in range(n):
            y[i] = (1/(i+1)**a)*(1/x)
        return np.array(y)

    def rotatetop(self, y, top, step, direction):
        """
        y is the array to cyclically shift the first top elements by step.
        step: amount which the we have to shift
        direction: +1/-1 right or left
        """
        s = deque(y[:top])
        s.rotate(direction*step)
        return np.array(list(s)+list(y[top:]))



def szipf(L=100, count=10_000, a=1, silent=True):
    """
    Generates the static zipf requests

    Refer to the Static Zipf Class to understand variables
    Returns the prob distribution and generated requests dictionary
    """

    start = time.time()

    szipf = StaticZipf(L=L, a=a)
    prob = szipf.prob
    req = szipf.req_gen(count)

    if not silent:
        print(f'TimeTaken:{time.time() - start} sec')

    return {'prob':prob, 'req':req}


def dzipf(L=100, count=10_000, req_step=1000, window=50, top=10, cache_size=10, a=1, silent=True):
    """
    Generates the dynamic zipf requests

    Refer to the Static Zipf Class to understand variables
    req_step: no. of requests after which popularity changes
    window: no. of most popular items for which the popularities are changed
    top: the no. of item's popularities are moved to left or right
    Returns the generated requests and optimal cache
    """

    # Input checking
    if not np.all([window < L, top < window, count % req_step == 0, top < L]):
        raise ValueError("Input arguments are not valid")

    start = time.time()

    count_step = int(count/req_step)

    szipf = StaticZipf(L=L, a=a)
    optimcache = np.zeros((count_step*cache_size)).astype(int)
    req = np.zeros((count,)).astype(int)
    for i in range(count_step):
        optimcache[cache_size*i:cache_size*(i+1)] = np.argsort(szipf.prob)[::-1][:cache_size]
        req[req_step*i:req_step*(i+1)] = szipf.req_gen(req_step)
        szipf.prob = szipf.rotatetop(szipf.prob, window, top, 1)

    if not silent:
        print(f'TimeTaken:{time.time() - start} sec')

    return {'optim_cache':optimcache, 'req':req}

# Netflix Data is collected between 1998 and 2005
# Library Size - 17, 770
# Requests logs processed - 10_04_80_507
def netflix(count=10_000, silent=True):
    """
    Loads the popularity profile from netflixdata file and generates the requests

    count: No. of requests to be generated
    Returns the prob distribution and generated requests dictionary
    """
    curr_path = Path(__file__).resolve().parents[1]
    data_path = Path("./data/netflixdata.pkl")

    with open(curr_path / data_path,'rb') as f:
        popularity_dic = pickle.load(f)

    items = list(popularity_dic.keys())
    prob = list(popularity_dic.values())

    start = time.time()
    # Random sampling
    req = np.random.choice(items, p = prob, size = count)
    if not silent:
        print(f'TimeTaken:{time.time()-start}sec')
    return {'prob':prob, 'req':req}


# Library Size - 1,61,085
def youtube(count=10_000, silent=True):
    """
    Loads the popularity profile from youtube data file and generates the requests

    count: No. of requests to be generated
    Returns the prob distribution and generated requests dictionary
    """
    curr_path = Path(__file__).resolve().parents[1]
    data_path = Path("./data/youtubedata.pkl")

    start = time.time()
    with open(curr_path / data_path,'rb') as f:
        prob = pickle.load(f)

    items = list(range(prob.shape[0]))
    # Random Sampling
    req = np.random.choice(items, p = prob, size = count)
    if not silent:
        print(f'TimeTaken:{time.time()-start}sec')
    return {'prob':prob, 'req':req}
