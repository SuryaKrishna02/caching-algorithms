from cachingalgo.full_observation.single_cache import LU


class LU2(LU):
    def __init__(self, cache_sizes, **kwargs):
        """
        cache_sizes - array of cache size - length = 2
        """
        # Inherits the methods and attributes from LU Class
        super().__init__(**kwargs, cache_size=None)
        
        self.cache_size1 = cache_sizes[0]
        self.cache_size2 = cache_sizes[1]
        
        # self.fetch stores the time at which cache elements are fetched
        self.fetchtime1 = {}
        self.fetchtime2 = {}
    
    def cache1_update(self, req, time):
        """
        Updates the cache 1
        req: Request
        time: Request arrival time
        """
        vk = {}
        if len(self.fetchtime2) > 0:
            for i in self.fetchtime2:
                vk[i] = self.prob[i]*(self.fetchtime2[i]+self.F[i] - (time+1))

            maxindk = max(vk, key=vk.get) # Gives the key with maximum value

            if self.prob[req]*self.F[req] < vk[maxindk]:
                freshtime = self.fetchtime2.pop(maxindk)
                self.fetchtime1[maxindk] = freshtime
                self.fetchtime1.pop(req)
                self.fetchtime2[req] = time + 1
            else:
                self.fetchtime1[req] = time + 1
        else:
            self.fetchtime1[req] = time + 1
    
    def cache2_update(self, req, time):
        """
        Updates the cache 2
        req: Request
        time: Request arrival time
        """
        vj = {}
        for i in self.fetchtime1:
            vj[i] = self.prob[i]*(self.fetchtime1[i] + self.F[i] - (time+1))

        minindj = min(vj, key=vj.get) # Gives the key with minimum value
        if self.prob[req]*self.F[req] > vj[minindj]:
            freshtime = self.fetchtime1.pop(minindj)
            self.fetchtime2[minindj] = freshtime
            self.fetchtime2.pop(req)
            self.fetchtime1[req] = time + 1
        else:
            self.fetchtime2[req] = time + 1
    
    def cache12_update(self, req, time):
        """
        Updates the cache 1 and 2 simultaneously
        req: Request
        time: Request arrival time
        """
        vj = {} # Cache 1
        vk = {} # Cache 2

        for i in self.fetchtime1:
            vj[i] = self.prob[i]*(self.fetchtime1[i]+self.F[i] - (time+1))

        for i in self.fetchtime2:
            vk[i] = self.prob[i]*(self.fetchtime2[i]+self.F[i] - (time+1))

        minindj = min(vj, key=vj.get) # Gives the key with minimum value of cache 1
        minindk = min(vk, key=vk.get) # Gives the key with minimum value of cache 2

        if (self.prob[req]*self.F[req]) > vj[minindj]:
            if vj[minindj] >= vk[minindk]:
                freshtime = self.fetchtime1.pop(minindj)
                self.fetchtime2[minindj] = freshtime
                self.fetchtime2.pop(minindk)
                self.fetchtime1[req] = time + 1
            elif vk[minindk] > (self.prob[req]*self.F[req]):
                freshtime = self.fetchtime2.pop(minindk)
                self.fetchtime1[minindk] = freshtime
                self.fetchtime1.pop(minindj)
                self.fetchtime2[req] = time + 1
            else:
                self.fetchtime1.pop(minindj)
                self.fetchtime1[req] = time + 1
        elif (self.prob[req]*self.F[req]) >= vk[minindk]:
            self.fetchtime2.pop(minindk)
            self.fetchtime2[req] = time + 1
                    
    def currcache(self, req, time, ithreq = None):
        """
        Calculates the current cache
        req: Request
        time: Request arrival time
        ithreq: no. of request algorithm processed so far
        Returns: cache, cache_hit and miss_type
        """
        
        hit1 = 0 # hit '1' or miss '0' for cache 1
        hit2 = 0 # hit '1' or miss '0' for cache 2
        c2pass = 0 # Whether the request goes to cache 2
        
        if req >= self.L:
            raise Exception("The Requested item is not in the library")
        
        # Updates the popularity
        if self.calpop:    
            self.popularity_update(req, ithreq)

        # Check whether Cache1 is full or not
        if len(self.fetchtime1) < self.cache_size1:
            if self.method == 'lfulite' and req not in self.prob:
                self.arr[req] = [ithreq+1, 1] # storing the items that are in start of the cache
            self.fetchtime1[req] = time + 1
        
        # Serving request in Cache1
        elif req in self.fetchtime1:
            if self.fetchtime1[req] + self.F[req] >= (time + 1):
                hit1 = 1
            else:                
                self.cache1_update(req, time)
        
        # Check whether Cache2 is full or not
        elif len(self.fetchtime2) < self.cache_size2:
            c2pass = 1
            if self.method == 'lfulite' and req not in self.prob:
                self.arr[req] = [ithreq+1, 1] # storing the items that are in start of the cache
            self.fetchtime2[req] = time + 1
        
        # Serving the request from the Cache2
        elif req in self.fetchtime2:
            c2pass = 1
            if self.fetchtime2[req] + self.F[req] >= (time+1):
                hit2 = 1
            else:
                self.cache2_update(req, time)
        
        # Serving the request from the library
        else:
            c2pass = 1
            if self.method == 'lfu' or ((self.method == 'lfulite')^(req not in self.prob)):
                self.cache12_update(req, time)
                    
        return {'cache':[[*self.fetchtime1.keys()],[*self.fetchtime2.keys()]], 'cache_hit':[hit1,hit2], 'c2pass':c2pass}
    


