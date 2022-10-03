import numpy as np
from collections import deque
import math
import random

# Least Frequently Used
class LFU:
    def __init__(self, L, cache_size):
        """
        L : Library size
        cache_size: Size of the Cache
        """
        self.arr = np.zeros((L,)) #intialises the counters array of size = library size
        self.cache_size = cache_size
        self.prob = np.zeros((L,)) # Stores the probability distribution of the library items

    def update(self, req):
        """
        Updates the counter of library items
        req: request
        """
        self.arr[req] += 1

    def currcache(self, Return = True, exclude = []):
        """
        To find the cache using LFU
        exclude: items that are to be excluded from the library while finding cache
        Return: True - returns the current cache or False - doesn't return
        Returns the current cache according to the popularity
        """
        distrib = self.arr/np.sum(self.arr)
        self.prob = distrib
        if len(exclude) != 0 :
            distrib[exclude] = 0
        if Return:
            return np.argsort(distrib)[::-1][:self.cache_size]

    def popularity(self):
        """
        Returns the popularity of the items in the Library
        """
        return self.prob

    def counters_used(self):
        """
        Returns no. of counters used till now
        """
        return np.count_nonzero(self.arr)

# Window LFU
class WLFU:
    def __init__(self, L, cache_size, window=None, F=[]):
        """
        window: Size of the window
        L: Library size
        F: Freshness constraints of the library items and size = L
        cache_size: Cache Size
        """
        if window == None:
            self.window = int(cache_size*cache_size*math.log(L))
        else:
            self.window = window
        self.L = L
        self.cache_size = cache_size

        # Checking whether we need to take F into consideration
        if len(F) == 0:
            self.state = False
        else:
            self.state = True
            # divided by window to normalize the Freshness constriants
            self.F = np.array(F)/self.window


        #deque internally uses double linked list
        self.q = deque(i for i in np.random.randint(L, size = self.window)) # Randomly intialised deque of size window upto L integers
        self.dic = {}

        # Random initialization of the deque
        if not self.state:
            for i in self.q:
                if i in self.dic:
                    self.dic[i] += 1
                else:
                    self.dic[i] = 1
        else:
            for i in self.q:
                if i in self.dic:
                    self.dic[i] += self.F[i]
                else:
                    self.dic[i] = self.F[i]

    def update(self, req):
        """
        Updates the counter deque used in WLFU
        req: request
        """

        #appends the new request to the deque
        self.q.appendleft(req)

        #removes the last request from the deque
        rem = self.q.pop()

        #Decreasing the count or removing the request
        if not self.state:
            if self.dic[rem] == 1:
                del self.dic[rem]
            else:
                self.dic[rem] -= 1
        else:
            if self.dic[rem] == self.F[rem]:
                del self.dic[rem]
            else:
                self.dic[rem] -= self.F[rem]

        #Increasing the count or appending the request
        if not self.state:
            if req in self.dic:
                self.dic[req] += 1
            else:
                self.dic[req] = 1
        else:
            if req in self.dic:
                self.dic[req] += self.F[req]
            else:
                self.dic[req] = self.F[req]

    def currcache(self):
        """
        to find the cache according frequency of items in window
        Returns the current cache
        """

        sort_arr = dict(sorted(self.dic.items(), key= lambda x:x[1], reverse = True)[:self.cache_size]).keys()
        return np.array(list(sort_arr))


class LFULite:
    def __init__(self, L, cache_size, window=None, F=[]):
        """
        window: window size of WLFU
        L: Library Size
        cache_size: Cache Size
        F: Freshness Constraints of the library items
        """
        self.L = L
        self.cache_size = cache_size
        self.counterbank = {} # Consists of key as video ID and value as list of [time, number of occurences]
        self.wlfu = WLFU(L=L, cache_size=cache_size, F=F, window=window)
        self.prob = {} # Item id and it's probability

    def update(self, req, ithreq, wlfu = True):
        """
        Update the counterbank and counter in WLFU
        req: request
        wlfu: whether to update the wlfu counter bank or not
        ithreq: no. of request algorithm processed so far
        """
        #Update the counter of the WLFU
        if wlfu:
            self.wlfu.update(req)

        #most frequent items in the window
        currtop = self.wlfu.currcache()

        #If present in the counterbank it increases the count.
        if req in self.counterbank:
            self.counterbank[req][1] += 1

        #Appending the elements that are not in counterbank
        for j in list(currtop):
            if j not in self.counterbank:
                self.counterbank[j] = [ithreq+1,1]

    def currcache(self, ithreq, Return = True, exclude = []):
        """
        to find the cache according to LFULite
        ithreq: how many request that are given to the algorithm till now
        exclude: items to be excluded while calculating the cache
        Return: True - returns the current cache or False - doesn't return
        Returns the current cache
        """
        if ithreq > 0:
            arr = {i:0 for i in self.counterbank}
            for k in arr:
                # Caluclating the popularity distribution of the elements that we added before this time.
                if self.counterbank[k][0] != (ithreq+1):
                    # Counting the appearnces after it is been added to the counterbank
                    arr[k] = (self.counterbank[k][1]-1)/((ithreq+1)-self.counterbank[k][0])
                self.prob = arr

            # For excluding some library item's in the cache
            if len(exclude) != 0:
                # it will assign 0
                arr.update(dict.fromkeys(exclude, 0))

            sort_arr = dict(sorted(arr.items(), key= lambda x:x[1], reverse = True)[:self.cache_size]).keys()
            if Return:
                return np.array(list(sort_arr))
        else:
            if Return:
                return np.array(list(self.counterbank.keys()))

    def popularity(self):
        "Return the popularity of the items in the counterbank"
        return self.prob

    def counters_used(self):
        """
        Returns no. of counters used till now
        """
        return len(self.counterbank)

class CountSketch:
    def __init__(self, l, b, L):
        """
        t: No. of random functions for each s and h
        b: No. of objects that h has to map from L
        L: Library Size
        """
        self.l = l
        self.b = b
        self.L = L
        self.h, self.s = self.createmap()
        self.cs = np.zeros((l,b))
        # Cache is of size C but as we are using zipf with parameter 1. C = b
        self.cache = []

    def randomassign(self, num, bi = False):
        """
        Generates random mapping value for mapping function
        num: no. of different mapping values
        bi: True - +1 or -1 and False - 1 to num (both inclusive)
        Returns generated random number in the given range
        """
        if bi:
            n = random.random()
            if(n > 0.5):
                return 1
            else:
                return -1
        else:
            return int(random.randint(1, num))

    def createmap(self):
        """
        Creates l number of h and s mapping functions for each library item.
        Return h and s mapping functions
        """
        h = {i:[] for i in range(self.L)}
        s = {i:[] for i in range(self.L)}

        # Creating l number of h functions
        for _ in range(self.l):
            for i in range(self.L):
                n = self.randomassign(self.b)
                h[i].append(n)

        # Creating l number of s functions
        for _ in range(self.l):
            for i in range(self.L):
                n = self.randomassign(2, True)
                s[i].append(n)

        return h,s

    def update(self, req):
        """
        Updates the cs counters which is a t*b array
        req: Request
        """
        for i in range(self.l):
            self.cs[i,self.h[req][i]-1] += self.s[req][i]

    def estimate(self, req):
        """
        Calculates the estimate of the requested item by finding median hi[r(t)]*si[r(t)]
        req: Request
        """
        med = np.zeros((self.l,))
        for i in range(self.l):
            med[i] = self.cs[i,self.h[req][i]-1]*self.s[req][i]
        return np.median(med)

    def min_est(self):
        """
        Calculates the minimum estimate of the cache and it's position
        Returns position and minimum value
        """
        arr = np.zeros((len(self.cache),))
        for i,j in enumerate(self.cache):
            arr[i] = self.estimate(j)
        index = np.argmin(arr)

        return index, arr[index]

    def currcache(self, req):
        """
        Updates the cs counter and inserts the request into the cache
        req: Request
        Returns the current cache
        """
        self.update(req)
        # If length of cache is less than b and not in cache.
        if(len(self.cache)<self.b and req not in self.cache):
            # Adding the request to the cache
            self.cache.append(req)
        elif(req not in self.cache):
            # Finding the estimate of the request
            req_est = self.estimate(req)
            # Adding the new request and removing the min_est item from the cache
            ind, est = self.min_est()
            if req_est > est:
                self.cache[ind] = req

        return np.array(self.cache)

# Least Recently Used
class LRU:
    def __init__(self, cache_size, L):
        """
        cache_size: Cache Size
        L: Library Size
        """
        self.cache_size = cache_size
        self.L = L
        self.cache = random.sample(range(1,L+1), cache_size)

    def update(self, req):
        """
        Updates the elements in the cache
        req: request
        """
        currcache = self.cache

        # If present in the cache, bring the item to the begining of the list
        if req in self.cache:
            currcache.remove(req)
            self.cache = [req] + currcache
        # else remove the last element of the list and insert in the first position.
        else:
            _ = currcache.pop()
            currcache.insert(0, req)
            self.cache = currcache

    def __contains__(self, req):
        """
        Magic method to use "in" keyword
        req: request
        """
        if req in self.cache:
            return True
        else:
            return False

    def currcache(self):
        "Returns the current cache"
        return self.cache

# Least Useful: Refer LFU, LFULite and WLFU algorithms to understand.
class LU:
    def __init__(self, L, F, cache_size, arr = [], method = '', useF = False, freqtop=None, window=None):
        """
        L: Library Size
        F: Freshness constant array of size L
        cache_size: Size of the cache for the algorithm
        freqtop: No. of the most frequent elements wlfu needs to consider
        useF: use of F for WLFU
        window: window size of the WLFU
        arr: probability of library ites in case of LU algorithm.
        method: 'lfu' or 'lfulite': Default is 'lfu' if arr is not given
        """
        self.F = {i:j for i, j in enumerate(F)}
        self.L = L
        self.cache_size = cache_size
        self.method = method

        # self.calpop determines whether we have to calculate popularity or not
        self.calpop = True if len(arr) == 0 else False

        # self.arr counter for the library items
        # self.prob contains the probabilty of items used by the algorithm
        if not self.calpop:
            self.prob = np.array(arr)
        elif self.method == 'lfu':
            self.arr = np.zeros((L,))
            self.prob = np.zeros((L,))
        elif self.method == 'lfulite': # LFU-Lite maintains the popularity of the items only in the counter bank
            self.arr = {} # Consists of key as video ID and value as list of [time, number of occurences]
            if useF:
                self.wlfu = WLFU(L=L, cache_size=freqtop, F=F, window=window)
            else:
                self.wlfu = WLFU(L=L, cache_size=freqtop, window=window)
            self.prob = {}
        # self.fetchtime stores the time at which cache elements are fetched
        self.fetchtime = {}

    def update(self, req, ithreq = None):
        """
        Updates the counters of the items used in the algorithm
        req: Request
        ithreq: no. of request algorithm processed so far
        """

        if self.method == 'lfu':
            self.arr[req] += 1
        elif self.method == 'lfulite':
            # finds the most frequent items according to WLFU
            self.wlfu.update(req)
            currtop = self.wlfu.currcache()
            if req in self.arr:
                self.arr[req][1] += 1

            for j in currtop:
                if j not in self.arr:
                    self.arr[j] = [ithreq+1, 1]

    def cache_update(self, req, time):
        """
        Updates the cache based on the request and it's arrival time
        req: Request
        time: arrival time of the request
        """
        v = {}

        for i in self.fetchtime:
            v[i] = self.prob[i]*(self.fetchtime[i]+self.F[i] - (time+1))

        minind = min(v, key=v.get) # Gives the key with minimum value

        if (self.prob[req]*self.F[req]) > v[minind]:
            self.fetchtime.pop(minind)
            self.fetchtime[req] = (time+1)

    def popularity_update(self, req, ithreq):
        """
        Calculates and updates the popularity of the items used in the algorithm
        req: Request
        ithreq: no. of request algorithm processed so far
        """
        self.update(req, ithreq = ithreq)
        if self.method == 'lfu':
            distrib = self.arr/np.sum(self.arr)
        elif self.method == 'lfulite':
            distrib = {i:0 for i in self.arr}
            for k in distrib:
                if self.arr[k][0] != (ithreq+1):
                    distrib[k] = (self.arr[k][1]-1)/((ithreq+1)-self.arr[k][0])
        self.prob = distrib

    def currcache(self, req, time, ithreq = None):
        """
        Calculates the current cache
        req: Request
        time: Request arrival time
        ithreq: no. of request algorithm processed so far
        Returns: cache, cache_hit and miss_type
        """
        hit = 0
        miss_type = -1 # Hit

        if req >= self.L:
            raise Exception("The request is not in the library")

        # Updates the popularity
        if self.calpop:
            self.popularity_update(req, ithreq)

        # Check whether cache is full or not
        if len(self.fetchtime) < self.cache_size:
                if self.method == 'lfulite' and req not in self.prob:
                    self.arr[req] = [ithreq+1, 1] # storing the items that are in start of the cache
                self.fetchtime[req] = time + 1
                miss_type = 1 # miss due to freshness constraint
        else:
            if req in self.fetchtime:
                if self.fetchtime[req] + self.F[req] >= (time + 1):
                    hit = 1
                else:
                    self.fetchtime[req] = (time+1)
                    miss_type = 1
            else:
                miss_type = 2 # miss due to not present in the cache

                if self.method == 'lfu' or ((self.method == 'lfulite')^(req not in self.prob)):
                    self.cache_update(req, time)

        return {'cache':list((self.fetchtime.keys())), 'cache_hit':hit, 'miss_type':miss_type}

    def popularity(self):
        "Return the popularity of the items used in the counterbank"
        return self.prob
