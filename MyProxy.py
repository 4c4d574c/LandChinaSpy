import json
import requests
import queue
from allcon import PROXYURL


class Proxies(object):
    def __init__(self):
        self.proxyurl = PROXYURL
        self.proxies_queue = queue.Queue()

    def __allProxies(self):
        retry_count = 5
        while (retry_count):
            r = requests.get(self.proxyurl)
            if (r.status_code == 200):
                j = json.loads(r.content)
                if (j["success"] == "true"):
                    return j["data"]
                else:
                    print("{},代理获取失败!".format(r.status_code))
                    retry_count -= 1
            else:
                print("代理获取失败!")
                retry_count -= 1
            continue
        return []
    
    def __formProxies(self):
        proxies_list = self.__allProxies()
        for ele in proxies_list:
            proxyHost = ele["IP"]
            proxyPort = ele["Port"]
            proxyMeta = "socks5://{}:{}".format(proxyHost, proxyPort)
            self.proxies_queue.put({"http": proxyMeta, "https": proxyMeta})
    
    def getProxy(self, local=False):
        retry_count = 5
        if (local == True):
            return None
        while (self.proxies_queue.empty() and retry_count > 0):
            retry_count -= 1
            self.__formProxies()
        if (retry_count <= 0):
            raise Exception("获取代理失败，请检查代理设置")
        
        return self.proxies_queue.get()