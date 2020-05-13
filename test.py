import requests
import time
import json

end = time.time() * 1000
begin = end - (15 * 60 * 1000)
url = "https://netbeam.es.net"

def getInterfaceTrafficByTimeRange():
    host = "albq-asw1"
    cat = "interfaces/ae10"
    r = requests.get(f"{url}/api/network/esnet/prod/devices/{host}/{cat}/traffic?begin={begin}&end={end}&rollup=30s&agg=avg")

    if r.status_code == 200:
        for k, v in r.json().items():
            # print(k, ":", v)
            if k == 'points':
                for trip in v:
                    print("Time:", time.asctime(time.localtime(trip[0] / 1000)))
                    print("\tIn:", (trip[1] / 1000 ** 2), "Mbps")
                    print("\tOut:", (trip[2] / 1000 ** 2), "Mbps")
                    print()


def getSAPTrafficByTimeRange():
    host = "chic-cr55"
    cat = "saps/111-lag-1-2161"

    r = requests.get(f"{url}/api/network/esnet/prod/devices/{host}/{cat}/traffic?begin={begin}&end={end}")

    if r.status_code == 200:
        for k, v in r.json().items():
            # print(k, ":", v)
            if k == 'points':
                for trip in v:
                    print("Time:", time.asctime(time.localtime(trip[0] / 1000)))
                    print("\tIn:", (trip[1] / 1000**3), "Gbps")
                    print("\tOut:", (trip[2] / 1000**3), "Gbps")
                    print()


getInterfaceTrafficByTimeRange()

