import numpy as np
import random
from collections import deque
import math

# Caching Bandit Marginal Posterior Sampling
class CBMPS:
    def __init__(self, L, cache_size):
        """
        L: Library Size
        cache_size: Cache Size
        """
        # Index 0 is alpha, Index 1 is beta of the beta distribution and Index 2 is Popularity.
        self.param = {i:[1,1,0] for i in range(L)}
        self.L = L
        self.cache_size = cache_size
        self.cache = random.sample(range(0,self.L),self.cache_size)

    def currcache(self, Return = False):
        """
        Calculates the current cache
        Return: True - returns the currcache or False - void return
        """
        # Generating the samples from the beta distribution for the items in the library.
        for i in self.param:
            #.item() returns the element in the single element numpy array
            self.param[i][2] = np.random.beta(self.param[i][0], self.param[i][1],1).item()

        #Sorting in decreasing order according to popularity distribution.
        sort = [k for k,_ in sorted(self.param.items(), key = lambda item: item[1][2], reverse = True)]

        #Updating the Current Cache
        self.cache = sort[:self.cache_size]

        if Return:
            return self.cache


    def update(self, req):
        """
        Updates the paramters of the beta distribution
        req: Request
        """

        #Updates only if the element is in the current cache
        if req in self.cache:
            #incrementing the alpha of ele
            self.param[req][0] += 1

            #incrementing the beta of all items in the currcache except for ele
            for i in self.cache:
                if i != req:
                    self.param[i][1] += 1

# Caching Bandit Structural Information
class CBSI:
    def __init__(self, L, cache_size, mu_c, delta):
        """
        L: Library Size
        cache_size: Cache Size
        mu_c: Probability of most popular Cth library item
        delta: Difference b/n probabilities of Cth and C+1 th most popular library items
        """
        self.L = L
        self.cache_size = cache_size
        # Index 0 is alpha, Index 1 is beta
        self.param = {i:[0, 0] for i in range(self.L)}
        # Probability of item
        self.prob = {i: 1/self.L for i in range(self.L)}
        # Cache at time t
        self.cache = random.sample(range(self.L), self.cache_size)
        self.mu_c = mu_c
        self.delta = delta
        # Library used for sampling
        self.Lib = self.prob

    def compute_A(self):
        """
        Calculates the dictionary A along with the probability according to mu_c and delta
        Returns A
        """
        A = {}
        for i in self.Lib:
            if self.Lib[i] >= (self.mu_c - (self.delta / 2)):
                A[i] = self.Lib[i]
        return A

    def sampling(self, pr, number):
        """
        Calculates the sampled set of items from the probability dictionary
        Return Set B
        """
        indices = list(pr.keys())
        probabilities = np.hstack(list(pr.values()))
        # B contains unique items
        B = np.random.choice(indices,p = probabilities, size = number, replace = False)
        return set(B)

    def currcache(self, Return = False):
        """
        Calculates the current cache
        Return: True - returns the currcache or False - void return
        """
        # Computing A with along with probabilities
        A = self.compute_A()

        if len(A) >= self.cache_size:
            # Sorting in decreasing order according to popularity distribution.
            sort = [k for k,_ in sorted(A.items(), key = lambda item: item[1], reverse = True)]

            # Updating current cache
            self.cache = sort[:self.cache_size]

        else:
            # Calculating the prob distribution (potential function) for the elements in the Lib other than in set A
            setA = set(A.keys())
            p = {}

            for i in self.Lib:
                if i not in A:
                    p[i] = 1/((self.mu_c - self.Lib[i])**2)

            c = sum(p.values())

            pdf = {k: v/c for k,v in p.items()}

            # Returns the setB which are sampled from the items that are not in setA according to prob
            setB = self.sampling(pdf, self.cache_size - len(A))

            self.cache = list(setA.union(setB))

        if Return:
            return self.cache

    def update(self, req):
        """
        Updates the parameters of the algorithm
        """

        #Checks whether request present in cache
        if req in self.cache:

            #Increase the alpha for the req
            self.param[req][0] += 1

            #Increase the beta for the items other than req
            for ele in self.cache:
                if ele != req:
                    self.param[ele][1] += 1

                #Updates the popularity distribution
                self.Lib[ele] = self.param[ele][0] / (self.param[ele][0] + self.param[ele][1])


def calculate_delta(prob, cache_size):
    """
    Calculates the delta which mu_c - mu_c+1, and mu_c
    Returns delta and mu_c
    """
    #calculates the delta = mu_c - mu_c+1
    prob_c_plus1 = np.sort(prob)[-(cache_size+1):][::-1]
    mu_c = prob_c_plus1[cache_size-1]
    mu_c_plus1 = prob_c_plus1[cache_size]
    delta = mu_c - mu_c_plus1
    return delta, mu_c


class CBSILite(CBSI):
    def __init__(self, win=None, **kwargs):
        """
        win: Window Size
        """
        # Inherits the methods and attributes from CBSI Class
        super().__init__(**kwargs)

        if win == None:
            win = int(self.cache_size*self.cache_size*math.log(self.L))

        # deque internally uses double linked list
        self.q = deque(i for i in np.random.randint(self.L, size = win)) # Randomly intialised deque of size window upto L integers

        # Ocuurences of elements in the deque are intialised
        self.dic = {}
        for i in self.q:
            if i in self.dic:
                self.dic[i] +=1
            else:
                self.dic[i] = 1

        #Counter_bank
        self.Lib = {}

    def deq_update(self, req):
        """
        Updates the deque q
        req: Request
        """
        # appends the new request to the deque
        self.q.appendleft(req)
        # removes the last request from the deque
        rem = self.q.pop()
        # Decreasing the count or removing the request
        if self.dic[rem] == 1:
            del self.dic[rem]
        else:
            self.dic[rem] -= 1
        # Increasing the count or appending the request
        if req in self.dic:
            self.dic[req] += 1
        else:
            self.dic[req] = 1

    def freq_top(self):
        """
        Returns the most frequently occuring items in the window
        """
        return [k for k, _ in sorted(self.dic.items(), key = lambda x: x[1], reverse = True)[:self.cache_size]]

    def counterbank_update(self, req):
        """
        Updates the Counter Bank
        req: Request
        """
        self.deq_update(req)
        topfreq = self.freq_top()

        for i in topfreq:
            if i not in self.Lib:
                self.Lib[i] = self.prob[i]
