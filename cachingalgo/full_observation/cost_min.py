from scipy.optimize import minimize_scalar, minimize
import numpy as np
import random

# Cost Minimisation with Same Refresh Rate
class CMSR:
    def __init__(self, cache_size, beta, z, lambda_param, L, Cost, prob=[], mu_hat=[], C_hat=[]):
        """
        Cost : [C_f, C_ca, C_ch, C_o] = [fetching, additional caching, checking, constant]
        beta : Arrival Rate
        cache_size : Size of the Cache
        lambda_param : lambda parameter
        z: order of the lambda_ (Refresh rates of the library gets decreased)
        prob: Popularity profile of the contents in the library
        mu_hat: optimal refresh rate
        C_hat: optimal cache elements
        """
        self.prob = prob
        self.L = L
        self.cost = Cost
        self.cache_size = cache_size
        self.beta = beta
        self.lambda_param = lambda_param
        self.lambda_ = np.array([self.lambda_param/(i)**z for i in range(1,self.L+1)],dtype=np.float64) # Refresh rates of the contents
        self.C_hat = np.array(C_hat)                              # Current Cache
        self.C_old =  np.argsort(self.prob)[::-1][:self.cache_size]# Old cache
        self.firsttime = True
        self.mu_hat = self.minimize_cost()                       # Checking Rate of the cache
        self.firsttime = False
        self.cache_update()                                    # Calculated cache

    # Average System Cost
    def avg_sys_cost(self, rr):
        """
        Calculates the average system cost
        rr: Refresh rate of the cache
        Returns the average system cost
        """
        eps = 1e-15
        # if we are
        if not self.firsttime:
            d = self.C_hat
        else:
            d = self.C_old

        try:
            return self.beta*self.cost[0] + \
                        len(self.C_hat)*rr*self.cost[2] + \
                        rr*self.cost[1]*np.sum((self.lambda_[d])/(self.lambda_[d] + rr)) + \
                        self.beta*np.sum(self.prob[d]*((self.lambda_[d]*self.cost[-1]/(rr+eps))-self.cost[0]))
        # if cache contains no elements
        except:
            return self.beta*self.cost[0]

    def minimize_cost(self):
        """
        Convex Constrained Minimisation of the average system Cost
        Returns the optimal refresh rate of the cache
        """
        return minimize_scalar(self.avg_sys_cost, bounds = (0, None)).x

    def marg_cost(self):
        """
        Calculates the marginal cost vector of the items in the library
        Returns the marginal cost vector
        """
        eps = 1e-15
        return self.mu_hat*self.cost[2] +\
            ((self.mu_hat*self.lambda_)/(self.lambda_ + self.mu_hat))*self.cost[1] + \
            self.beta*self.prob*(((self.cost[3]*self.lambda_)/(self.mu_hat+eps))-self.cost[0])

    def cache_update(self):
        """
        Updates the Cache according to the marginal cost
        """
        mc = self.marg_cost()
        sorted_mc = np.argsort(mc[mc<0])
        if len(sorted_mc) > self.cache_size:
            self.C_hat = sorted_mc[:self.cache_size]
        else:
            self.C_hat = sorted_mc

    def refreshrate_cache(self):
        """
        Calculates the optimal refresh rate of the cache and optimal cache after their convergence
        """
        while(not np.array_equal(self.C_hat, self.C_old)):
            self.C_old = self.C_hat
            self.mu_hat = self.minimize_cost()
            self.cache_update()

    def currcache(self):
        """
        Calculates and returns the current cache
        """
        self.refreshrate_cache()
        return self.C_hat

# Cost Minimization with Different Refresh Rates
# Variants of CMDR- CMDR: Popularity is given
#                   CMDRP: Popularity is not given and cache update according to popularity
#                   CMDRM: Popularity is not given and cache update according to marginal cost 
class CMDR:
    def __init__(self, cache_size, beta, z, lambda_param, L, Cost, cache_update = 'marg', seed = 7, prob = [], C_hat=[]):
        """
        Cost : [C_f, C_ca, C_ch, C_o] = [fetching, additional caching, checking, constant]
        beta : Arrival Rate
        cache_size : Size of the Cache
        lambda_param : lambda parameter
        prob: probability profile of the items in the library
        z: order of the lambda_ (Refresh rates of the library gets decreased)
        cache_update: 'marg' - updates the cache according to the which has the more negative marginal cost
                    'pop'- updates the cache according to the most popular items in the library.
        C_hat: optimal cache of length cache_size
        seed: seed for numpy and random
        """
        np.random.seed(seed)
        random.seed(seed)
        self.upd = cache_update
        self.L = L
        self.cost = Cost
        self.cache_size = cache_size
        self.beta = beta
        self.lambda_param = lambda_param
        self.lambda_ = np.array([self.lambda_param/(i)**z for i in range(1,self.L+1)],dtype=np.float64) # Refresh rates of the contents
        self.C_hat = np.array([], dtype='int') if len(C_hat) == 0 else C_hat
        self.mu_hat = np.array([random.uniform(0,i) for i in self.lambda_])
        # Setting Bounds for the cost minimisation
        self.bounds = [(0, i) for i in self.lambda_]
        if len(prob) == 0:
            self.prob = np.zeros((L,))
            self.arr = np.zeros((L,)) # arary Counter
            self.calpop = True
        else:
            self.prob = prob
            self.calpop = False
            self.minimize_cost()


    # Average System Cost
    def avg_sys_cost(self, rr):
        """
        Calculates the average system cost
        rr: Refresh rates of the cache elements
        Returns the average system cost
        """
        eps = 1e-15

        # For the empty cache it returns self.beta*self.cost[0]
        try:
            return self.beta*self.cost[0] + \
                    np.sum(rr[self.C_hat])*self.cost[2] + \
                    self.cost[1]*np.sum((rr[self.C_hat]*self.lambda_[self.C_hat])/(self.lambda_[self.C_hat] + rr[self.C_hat])) + \
                    self.beta*np.sum(self.prob[self.C_hat]*((self.lambda_[self.C_hat]*self.cost[-1]/(rr[self.C_hat]+eps))-self.cost[0]))
        except:
            return self.beta*self.cost[0]

    # Minimising the System Cost for the Cache size equal to the library size i.e., infinite Cache
    def avg_sys_cost_inf(self, rr):
        """
        Calculates the average system cost if cache consists of entire library
        rr: Refresh rates of the entire library
        Returns the average system cost
        """
        eps = 1e-15
        return self.beta*self.cost[0] + \
                        np.sum(rr)*self.cost[2] + \
                        self.cost[1]*np.sum((rr*self.lambda_)/(self.lambda_ + rr)) + \
                        self.beta*np.sum(self.prob*((self.lambda_*self.cost[-1]/(rr+eps))-self.cost[0]))

    # Convex Constrained Minimisation

    def minimize_cost(self):
        """
        Convex Constrained Minimisation of the average system Cost
        Returns the optimal refresh rates of the cache
        """
        # x0 - initial values for the cost minimization
        return minimize(self.avg_sys_cost, x0=self.mu_hat[self.C_hat], bounds=[self.bounds[i] for i in self.C_hat]).x


    # Caluclates the marginal cost vector and returns it
    def marg_cost(self):
        """
        Calculates the marginal cost vector of the items in the library
        Returns the marginal cost vector
        """
        eps = 1e-15
        return self.mu_hat*self.cost[2] +\
            ((self.mu_hat*self.lambda_)/(self.lambda_ + self.mu_hat))*self.cost[1] + \
            self.beta*self.prob*(((self.cost[3]*self.lambda_)/(self.mu_hat+eps))-self.cost[0])

    def cache_update(self, req):
        """
        Updates the cache
        req: Request
        """
        if len(self.C_hat) < self.cache_size:
            if req not in self.C_hat:
                self.C_hat = np.append(self.C_hat, req)
        else:
            self.mu_hat[self.C_hat] = self.minimize_cost()
            if self.upd == 'marg':
                if req not in self.C_hat:
                    mc = self.marg_cost()
                    item_rem = self.C_hat[np.argmax(mc[self.C_hat])]
                    if mc[item_rem] > mc[req]:
                        self.C_hat = np.delete(self.C_hat, np.where(self.C_hat == item_rem))
                        self.C_hat = np.append(self.C_hat, req)
            elif self.upd == 'pop':
                self.C_hat = np.argsort(self.prob)[::-1][:self.cache_size]


    def counter_update(self, req):
        """
        Increases the counter of the library items
        req: Request
        """
        self.arr[req] += 1

    # Calculates the popularity distribution
    def currcache(self, req):
        """
        Calculates and Returns the current cache
        """
        if self.calpop:
            self.counter_update(req)
            self.prob = self.arr/np.sum(self.arr)
            self.cache_update(req)
        return self.C_hat
