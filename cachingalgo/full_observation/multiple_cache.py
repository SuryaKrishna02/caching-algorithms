import random
from cachingalgo.full_observation.single_cache import LRU


# LRUm algorithm consists of v virtual caches, f-v caches of total size m.
class LRUm(LRU):
    def __init__(self, size, f, v, L):
        """
        size: vector of length f which specifies the length of each list
               If length = 1 and f > 1, all the lists have same length
        f: Total no. of lists used in the algorithm
        v: No. of lists used as virtual Caches.
        L: Library size
        """

        self.f = f
        # No. of lists used as Cache
        self.cnum = f-v
        self.L = L

        # Uses LRU if LRUm uses one list
        if f == 1:
            super().__init__(cache_size=size, L=L)
        else:
            if isinstance(size, list) and len(size) == f:
                self.size = size
            else:
                self.size = [size]*f

            # self.part is to make sure that at the start, each of lists are unique
            self.part = self.L//self.f
            self.collection = []

            #Randomly initializes the f lists
            for itr, length in enumerate(self.size):
                start = int(itr*self.part)
                end = int((itr+1)*self.part)
                self.collection.append(random.sample(range(start, end), int(length)))

    def index_finder(self, req, full_search = False):
        """
        Finds the index of request in the f lists
        req: Request
        full_search: True - searches all list or False - searches only cache excluding virtual caches
        Returns request's position in list and it's corresponding list index. returns -1 if not found
        """
        if full_search:
            part = self.cnum
        else:
            part = self.f
        index = -1
        listnum = -1

        # Searches from the last list
        for i, list_ in enumerate(self.collection[-part:]):
            if req in list_:
                index = list_.index(req)
                listnum = i
        return index, listnum

    def update(self, req):
        """
        Updates the f lists
        req: Request
        """

        # If the algorithm has more lists
        if self.f != 1:
            # Gives the index, list number of the req
            index, listnum = self.index_finder(req)

            if index != -1:
                if listnum < self.f-1:
                    # moves the req to the index 0 of listnum + 1 and listnum+1 last element
                    # is moved to the index 0 of listnum
                    self.collection[listnum].remove(req)
                    temp = self.collection[listnum+1].pop()
                    self.collection[listnum] = [temp] + self.collection[listnum]
                    self.collection[listnum+1] = [req] + self.collection[listnum+1]

                else:
                    # moves the req to the index 0
                    temp = self.collection[listnum].pop(index)
                    self.collection[listnum] = [temp] + self.collection[listnum]

            # adds the ele at index 0 of list 1 and discards the last element of that list.
            else:
                self.collection[0].pop()
                self.collection[0] = [req] + self.collection[0]

        else:
            super().update(req)

    def __contains__(self, req):
        """
        Magic method to use "in" keyword
        req: request
        """
        if self.f != 1:
            index, _ = self.index_finder(req, True)
            if index != -1:
                return True
            else:
                return False

        else:
            if req in self.cache:
                return True
            else:
                return False

    def currcache(self):
        """
        Returns the current cache
        """

        if self.f != 1:
            return self.collection[-self.cnum:]
        else:
            return self.cache

# fLRU algorithm consists of f-1 virtual caches and 1 cache
class fLRU:
    def __init__(self, f, size, L):
        """
        f: total no. of caches
        size: vector of length f which specifies the length of each list
               If length = 1 and f > 1, all the lists have same length
        L: Library Size
        """
        self.f = f
        self.L = L
        if isinstance(size, list) and len(size) == f:
            self.size = size
        else:
            self.size = [size]*f

        self.collection = []

        #Randomly intialiases the f lists
        for length in self.size:
            self.collection.append(random.sample(range(1, L), length))

    def update(self, req):
        """
        Updates the f lists
        req: Request
        """
        found = False
        for i in range(self.f-1, -1, -1):
            currlist = self.collection[i]
            prevlist = self.collection[i-1] if i > 0 else None

            # if the req is present in the ith list, move it to the first position
            if req in currlist:
                currlist.remove(req)
                self.collection[i] = [req] + currlist
                found = True

            # if the req is present in the i-1th list but not in ith list, move it
            # to the first position of the ith list and discard the last item of the ith list.
            elif prevlist is not None and req in prevlist:
                _ = currlist.pop()
                self.collection[i] = [req] + currlist
                found = True

        # if the req is not in the collection of lists then insert it in the first list.
        if not found:
            _ = self.collection[0].pop()
            self.collection[0] = [req] + self.collection[0]

    def __contains__(self, req):
        """
        Magic method to use "in" keyword
        req: request
        """
        if req in self.collection[-1]:
            return True
        else:
            return False

    def currcache(self):
        """
        Returns the current cache
        """
        return self.collection[-1]
