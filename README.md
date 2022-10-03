### Algorithms in the  Notebooks
- **Full Observation Single Cache:** LFU, WLFU, LFULite, CountSketch
- **Full Observation Multiple Cache:** LRU, fLRU, LRUm
- **Partial Observation Single Cache:** CBMPS, CBSI, CBSILite
- **Tandem Model Static Data:** LFU-LFU, LFULite-LFULite
- **Tandem Model Dynamic Data:** LU2, LU2-LFU, LU2-LFULite
- **Dynamic Data:** LU, LU-LFU, LU-LFULite[C or 2C or 3C], LU-LFULite(V)[C or 2C or 3C]
- **Cost Minimization:** CMSR, CMDR, CMDRM, CMDRP

### Request Generation

```python
from cachingalgo.request_generation.continuous import szipf, dzipf, youtube, netflix

# To generate requests which follows Static Zipf distribution.
# 50,000 requests with library size = 1,61,085 and Zipf shape parameter = 1

szdata = szipf(count=50_000, a=1, L=1_61_085)
# Probabilty distribution
szdataprob = szdata['prob']
# Array of requests
szdatareq = szdata['req']   


# To generate requests which follows Static Zipf distribution but with changing popularity.
# 50,000 requests with library size = 1,61,085 and popularity changes for every 5,000 requests
# by shifting probabilities of the top 500 items by 50.

dzdata = dzipf(count=50_000, a=1, L=1_61_085, req_step=5_000, window=500, top=50, cache_size=10)
# Array of requests
dzdatareq = dzdata['req']   
# Array of size (count//req_step)*cache_size i.e optimal cache for each req_step requests
optimalcache = dzdata['optim_cache']


# To generate requests from the YouTube data.
# 50,000 requests with the library size = 1,61,085

ytdata = youtube(count=50_000)
# Probability distribution
ytdataprob = ytdata['prob']
# Array of requests
ytdatareq = ytdata['req']


# To generate requests from the Netflix data.
# 50,000 requests with the library size = 17,770

netdata = netflix(count=50_000)
# Probability distribution
netdataprob = netdata['prob']
# Array of requests
netdatareq = netdata['req']
```
We can use any of the four types of requests for analyzing the caching algorithms. In this documentation, we will use requests generated from the YouTube data.

### Usage of LFU algorithm

```python
from cachingalgo.full_observation.single_cache import LFU

# Initialising the algorithm
alg = LFU(L=100, cache_size=5)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)
    # Returns the cache at current instant
    currcache = alg.currcache()

```

### Usage of WLFU algorithm

```python
from cachingalgo.full_observation.single_cache import WLFU

# Initialising the algorithm
alg = WLFU(L=100, cache_size=5)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)
    # Returns the cache at current instant
    currcache = alg.currcache()

```

### Usage of LFU-Lite algorithm

```python
from cachingalgo.full_observation.single_cache import LFULite

# Initialising the algorithm
alg = LFULite(L=100, cache_size=5)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request, i)
    # Returns the cache at current instant
    currcache = alg.currcache(i)

```

### Usage of LRU algorithm

```python
from cachingalgo.full_observation.single_cache import LRU

# Initialising the algorithm
alg = LRU(L=100, cache_size=5)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)

    # To check whether a request is present in the cache
    present = request in alg
```

### Usage of Count-Sketch algorithm

```python
from cachingalgo.full_observation.single_cache import CountSketch

# Initialising the algorithm
alg = CountSketch(l=6, b=10, L=100)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)
    # Returns the cache at current instant
    currcache = alg.currcache(request)
```

### Usage of f-LRU algorithm

```python
from cachingalgo.full_observation.multiple_cache import fLRU

# Initialising the algorithm
alg = fLRU(L=100, size=5, f=2)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)

    # To check whether a request is present in the cache
    present = request in alg

```

### Usage of LRU(m) algorithm

```python
from cachingalgo.full_observation.multiple_cache import LRUm

# Initialising the algorithm
alg = LRUm(L=100, size=5, f=2, v=1)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)

    # To check whether a request is present in the cache
    present = request in alg

```

### Usage of CB-MPS algorithm
```python
from cachingalgo.partial_observation.single_cache import CBMPS

# Initialising the algorithm
alg = CBMPS(L=100, cache_size=5)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Returns the cache at current instant
    currcache = alg.currcache(request)
    # Updates the counter
    alg.update(request)

```

### Usage of CB-SI algorithm
```python
from cachingalgo.partial_observation.single_cache import CBSI, calculate_delta

# Calculate the parameter which are to be provided for the CB-SI algorithms
delta, mu_c = calculate_delta(ytdataprob, cache_size=10)
# Initialising the algorithm
alg = CBSI(L=100, cache_size=5, delta=delta, mu_c=mu_c)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Returns the cache at current instant
    currcache = alg.currcache(request)
    # Updates the counter
    alg.update(request)

```

### Usage of CB-SILite algorithm
```python
from cachingalgo.partial_observation.single_cache import CBSILite, calculate_delta

# Calculate the parameter which are to be provided for the CB-SI algorithms
delta, mu_c = calculate_delta(ytdataprob, cache_size=10)
# Initialising the algorithm
alg = CBSILite(L=100, cache_size=5, delta=delta, mu_c=mu_c)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # update the counterbank
    alg.counterbank_update(request)
    # Returns the cache at current instant
    currcache = alg.currcache(request)
    # Updates the counter
    alg.update(request)

```

### Usage of LU algorithm

```python
from cachingalgo.full_observation.single_cache import LU

# Defining the parameters
L = 100
cache_size = 5

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU(L=L, F=F, cache_size=cache_size, arr=ytdataprob)
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i)
```

### Usage of LU-LFU algorithm

```python
from cachingalgo.full_observation.single_cache import LU

# Defining the parameters
L = 100
cache_size = 5

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU(L=L, F=F, cache_size=cache_size, method='lfu')
# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i)
```

### Usage of LU-LFULite[C or 2C or 3C] algorithm

```python
from cachingalgo.full_observation.single_cache import LU
import math
# Defining the parameters
L = 100
cache_size = 5
window = int((cache_size^2)*math.log(L))

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU(L=L, F=F, cache_size=cache_size, method='lfulite', window=window, freqtop=cache_size)

# In the above initialisation changing freqtop, one can get
# freqtop = 2*cache_size - LU-LFULite[2C] algorithm
# freqtop = 3*cache_size - LU-LFULite[3C] algorithm

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request, ithreq=i)
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i, ithreq=i)

```

### Usage of LU-LFULite(V)[C or 2C or 3C] algorithm

```python
from cachingalgo.full_observation.single_cache import LU
import math
# Defining the parameters
L = 100
cache_size = 5
window = int((cache_size^2)*math.log(L))

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU(L=L, F=F, cache_size=cache_size, method='lfulite', window=window, freqtop=cache_size, useF=True)

# In the above initialisation changing freqtop, one can get
# freqtop = 2*cache_size - LU-LFULite(V)[2C] algorithm
# freqtop = 3*cache_size - LU-LFULite(V)[3C] algorithm

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request, ithreq=i)
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i, ithreq=i)

```

### Usage of LU2 algorithm
```python
from cachingalgo.tandem_model.dynamic import LU2

# Defining the parameters
L = 100

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU2(L=L, F=F, cache_sizes=[5, 10], arr=ytdataprob)

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i)
```

### Usage of LU2-LFU algorithm
```python
from cachingalgo.tandem_model.dynamic import LU2

# Defining the parameters
L = 100

# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU2(L=L, F=F, cache_sizes=[5, 10], method='lfu')

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request)
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i)
```

### Usage of LU2-LFULite(V)[3C] algorithm
```python
from cachingalgo.tandem_model.dynamic import LU2
import math

# Defining the parameters
L = 100
# 5 is the size of cache 1
window = int((5^2)*math.log(L))
# Freshness Constraint array
F = np.ones((L,), dtype=int)

# Initialising the algorithm
alg = LU2(L=L, F=F, cache_sizes=[5, 10], method='lfulite', window=window, fretop=3*5, useF=True)

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
    request = ytdatareq[i]
    # Updates the counter
    alg.update(request, ithreq=i)
    # Returns the cache and hit or miss information at current instant
    currcache = alg.currcache(req=request, time=i, ithreq=i)

```

### Usage of CMSR algorithm
```python
from cachingalgo.full_observation.cost_min import CMSR

# Initialising the algorithm
alg = CMSR(cache_size=5, L=100, beta=10, z=1.5, lambda_param=5, Cost=[1, 0.1, 0.05, 0.025], prob=ytdataprob, seed=7)

# To retrieve the cache
algcache = alg.currcache()

# To calculate the average system cost
avg_sys_cost = alg.avg_sys_cost(alg.mu_hat)

```

### Usage of CMDR algorithm
```python
from cachingalgo.full_observation.cost_min import CMDR

# Defining the parameter
cache_size = 5

# Initialising the algorithm
alg = CMDR(cache_size=cache_size, L=100, beta=10, z=1.5, lambda_param=5, Cost=[1, 0.1, 0.05, 0.025], prob=ytdataprob, C_hat=np.arange(cache_size, dtype='int'), seed=7)

# To retrieve the cache
algcache = alg.currcache()

# To calculate the average system cost
avg_sys_cost = alg.avg_sys_cost(alg.mu_hat)

```

### Usage of CMDRM algorithm
```python
from cachingalgo.full_observation.cost_min import CMDR

# Defining the parameter
cache_size = 5

# Initialising the algorithm
alg = CMDR(cache_size=cache_size, L=100, beta=10, z=1.5, lambda_param=5, Cost=[1, 0.1, 0.05, 0.025], cache_update='marg', seed=7)

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
  request = ytdatareq[i]

  # To retrieve the cache
  algcache = alg.currcache(request)

  # To calculate the average system cost
  avg_sys_cost = alg.avg_sys_cost(alg.mu_hat)
```

### Usage of CMDRP algorithm
```python
from cachingalgo.full_observation.cost_min import CMDR

# Defining the parameter
cache_size = 5

# Initialising the algorithm
alg = CMDR(cache_size=cache_size, L=100, beta=10, z=1.5, lambda_param=5, Cost=[1, 0.1, 0.05, 0.025], cache_update='pop', seed=7)

# Total no. of requests
totalreq = ytdatareq.shape[0]

for i in range(totalreq):
  request = ytdatareq[i]

  # To retrieve the cache
  algcache = alg.currcache(request)

  # To calculate the average system cost
  avg_sys_cost = alg.avg_sys_cost(alg.mu_hat)

```
