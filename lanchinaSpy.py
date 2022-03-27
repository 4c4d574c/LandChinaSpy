#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from allcon import *
from LCBase import Base
from concurrent.futures import ThreadPoolExecutor as TP
from concurrent.futures import as_completed


class DownloadGDJH(Base):
    def __init__(self, save_flname) -> None:
        super().__init__()
        self.flname = save_flname
        self.listurl = GDJHURL
        self.detailurl = GDJHDETAILURL
    
    def parseGuid(self):
        while (not self.listqueue.empty()):
            data = self.listqueue.get()
            if ("gyjhGuid" in data.keys()):
                self.guidqueue.put({"gyjhGuid": data["gyjhGuid"]})
                self.titledict[data["gyjhGuid"]] = data["biaoti"]
            else:
                print("bad data: {}".format(data))

    def detailValid(self, trueguid: dict, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        datakeys = list(resp_content["data"].keys())
        if ("gyjhGuid" in datakeys and 
            resp_content["data"]["gyjhGuid"] == trueguid["gyjhGuid"]):
            return True
        else:
            return False


class DownloadCRGG(Base):
    def __init__(self, save_flname) -> None:
        super().__init__()
        self.flname = save_flname
        self.listurl = CRGGURL
        self.detailurl = CRGGDETAILURL
    
    def parseGuid(self):
        while (not self.listqueue.empty()):
            data = self.listqueue.get()
            if ("gyggGuid" in data.keys()):
                self.guidqueue.put({"gyggGuid": data["gyggGuid"]})
                if ("gyggBt" in data.keys()):
                    self.titledict[data["gyggGuid"]] = data["gyggBt"]
                else:
                    self.titledict[data["gyggGuid"]] = ""
                    print(data)
            else:
                print("bad data: {}".format(data))
    
    def detailValid(self, trueguid: dict, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        if (resp_content["relate"] == []):
            relatekeys = []
        else:
            relatekeys = list(resp_content["relate"][0].keys())
        if (resp_content["data"] == {}):
            datakeys = []
        else:
            datakeys = list(resp_content["data"].keys())
        if ("gyggGuid" in relatekeys and
            resp_content["relate"][0]["gyggGuid"] == trueguid["gyggGuid"]):
            return True
        elif ("gyggBt" in datakeys and
              resp_content["data"]["gyggBt"] == self.titledict[trueguid["gyggGuid"]]):
            return True
        else:
            return False


class DownloadDKGS(Base):
    def __init__(self, save_flname) -> None:
        super().__init__()
        self.flname = save_flname
        self.listurl = DKGSURL
        self.detailurl = DKGSDETAILURL
    
    def parseGuid(self):
        while (not self.listqueue.empty()):
            data = self.listqueue.get()
            if ("cjgsGuid" in data.keys()):
                self.guidqueue.put({"cjgsGuid": data["cjgsGuid"]})
                self.titledict[data["cjgsGuid"]] = data["gsbt"]
            else:
                print("bad data: {}".format(data))
    
    def detailValid(self, trueguid: dict, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        relatekeys = list(resp_content["relate"][0].keys())
        if ("gyggGuid" in relatekeys and
            resp_content["relate"][0]["gyggGuid"] == trueguid["cjgsGuid"]):
            return True
        else:
            return False


class DownloadGDJG(Base):
    def __init__(self, save_flname) -> None:
        super().__init__()
        self.flname = save_flname
        self.listurl = GDJGURL
        self.detailurl = GDJGDETAILURL

    def parseGuid(self):
        while (not self.listqueue.empty()):
            data = self.listqueue.get()
            if ("gdGuid" in data.keys()):
                self.guidqueue.put({"gdGuid": data["gdGuid"]})
                self.titledict[data["gdGuid"]] = data["tdZl"]
            else:
                print("bad data: {}".format(data))
    
    def detailValid(self, trueguid: dict, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        datakeys = list(resp_content["data"].keys())
        if ("zdGuid" in datakeys and
            resp_content["data"]["zdGuid"] == trueguid["gdGuid"]):
            return True
        else:
            return False


class DownloadQTGG(Base):
    def __init__(self, save_flname) -> None:
        super().__init__()
        self.flname = save_flname
        self.listurl = QTGGURL
        self.detailurl = QTGGDETAILURL
    
    def parseGuid(self):
        while (not self.listqueue.empty()):
            data = self.listqueue.get()
            if ("gyggGuid" in data.keys()):
                self.guidqueue.put({"gyggGuid": data["gyggGuid"]})
                self.titledict[data["gyggGuid"]] = data["gyggBt"]
            else:
                print("bad data: {}".format(data))
    
    def detailValid(self, trueguid: dict, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        datakeys = list(resp_content["data"].keys())
        if ("gyggBt" in datakeys and 
            resp_content["data"]["gyggBt"] == self.titledict[trueguid["gyggGuid"]]):
            return True
        else:
            return False


class DownloadCRGG_T(DownloadCRGG):
    def __init__(self, save_flname) -> None:
        super().__init__(save_flname)
    
    def downloadDetail(self, url: str):
        with TP(max_workers=MAX_WORKER) as executor:
            while (not self.guidqueue.empty()):
                executor.submit(self.downloadDetailPage, url, self.guidqueue.get())
                
    
    def downloadAllPage(self, url: str, data: dict, page_num: int):
        datalist = list()
        with TP(max_workers=MAX_WORKER) as executor:
            for page in range(1, page_num+1):
                data["pageNum"] = page
                datalist.append(data.copy())
            allpage = {executor.submit(self.downloadPage, url, dat): dat for dat in datalist}
            for page in as_completed(allpage):
                data = allpage[page]
                try:
                    resp = page.result()
                except Exception as e:
                    print("downloadAllPage exceptions: {}".format(e))
                else:
                    self.pagequeue.put(resp)


if __name__ == "__main__":
    t = DownloadCRGG_T("crgg.json")
    t.start()
