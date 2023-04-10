import json
from scholarly import scholarly
from scholarly import ProxyGenerator

# Set up a ProxyGenerator object to use free proxies
# This needs to be done only once per session
pg = ProxyGenerator()

sucess = pg.FreeProxies()
# print(f'Proxy setup sucess: {sucess}.')
scholarly.use_proxy(pg)

# will paginate to the next page by default
pubs_iter = scholarly.search_pubs("1810.04805")


print(json.dumps(next(pubs_iter), indent=2))
