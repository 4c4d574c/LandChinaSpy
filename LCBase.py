from MyProxy import Proxies
import os
import queue
import hashlib
import time
import json
import requests
from allcon import *


class Base(object):
    def __init__(self) -> None:
        self.flname = ""
        self.xzqurl = XZQURL
        self.yturl = YTURL
        self.listurl = ""
        self.detailurl = ""
        self.provc = ""
        self.proxies = Proxies()
        self.successcode = list()
        self.xzqcode = dict()
        self.ytcode = dict()
        self.titledict = dict()
        self.detailfailed = queue.Queue()
        self.listfailed = queue.Queue()
        self.pagequeue = queue.Queue()
        self.listqueue = queue.Queue()
        self.guidqueue = queue.Queue()
        self.detailqueue = queue.Queue()
    
    def createHash(self, s: str)->str:
        sha256 = hashlib.sha256()
        eles = [HEADER["User-Agent"], str(int(time.strftime("%d", time.localtime()))), s]
        sha256.update("".join(eles).encode())
        
        return sha256.hexdigest()

    def downloadListFailed(self, url):
        while (not self.listfailed.empty()):
            code, page, tdyt, pgNumFailed = self.listfailed.get()
            if (pgNumFailed):
                if (tdyt):
                    data = {"pageNum": page, "pageSize": 40, "xzqDm": code, "tdYt": tdyt, "startDate": "", "endDate": ""}
                    
                else:
                    data = {"pageNum": page, "pageSize": 40, "xzqDm": code, "startDate": "", "endDate": ""}
                try:
                    resp = self.getResp(url, data)
                    if (not (self.respValid(resp) and self.listValid(resp))):
                        self.listfailed([code, page, tdyt, pgNumFailed])
                        continue
                    page_num = self.getPageNum(json.loads(resp))
                except Exception as e:
                    print("downloadFailed: 获取{}的页数时失败，exceptions: {}".format(code, e))
                    self.listfailed.put([code, 1, tdyt, True])
                else:
                    if (page_num > 150):
                        for tdyt in self.ytcode.keys():
                            data["tdYt"] = tdyt
                            try:
                                resp = self.getResp(url, data)
                                page_num = self.getPageNum(json.loads(resp.content))
                                if (not (self.respValid(resp) and self.listValid(resp))):
                                    print("获取{}的页数时失败，exceptions: {}".format(code, e))
                                    self.listfailed.put([code, 1, tdyt, True])
                                    continue
                            except Exception as e:
                                print("获取{}的页数时失败，exceptions: {}".format(code, e))
                                self.listfailed.put([code, 1, tdyt, True])
                            else:
                                self.downloadAllPage(url, data, page_num)
                    else:
                        self.downloadAllPage(url, data, page_num)
                    # self.downloadAllPage(url, data, page_num)
            else:
                data = {"pageNum": page, "pageSize": 40, "xzqDm": code, "startDate": "", "endDate": ""}
                try:
                    self.downloadPage(url, data)
                except Exception as e:
                    print(e)
    
    def downloadDetailFailed(self, url):
        while (not self.detailfailed.empty()):
            try:
                self.downloadDetailPage(url, self.detailfailed.get())
                # self.downloadDetail(url, self.detailfailed.get())
            except Exception as e:
                print("downloadDetailFailed exceptions: {}".format(e))

    def writeFile(self, flname: str):
        with open(flname, "a+") as fl:
            while (not self.detailqueue.empty()):
                fl.write(json.dumps(self.detailqueue.get(), ensure_ascii=False, indent=4) + "\n")
    
    def writeSuccess(self, code):
        with open("success.txt", "a+") as fl:
            fl.write(str(code) + "\n")
    
    def ignoreCode(self):
        if (os.path.exists("success.txt")):
            with open("success.txt", "r") as fl:
                for ele in fl.readlines():
                    self.successcode.append(ele.strip())
    
    def parseXZQ(self, data: dict):
        if ("children" in data.keys()):
            for ele in data["children"]:
                self.parseXZQ(ele)
        else:
            self.xzqcode[data["enumValue"]] = data["enumName"]
    
    def fetchXZQ(self):
        max_try = 5
        data = json.dumps({"parentXzq": ""})
        proxies = self.proxies.getProxy(True)
        while (max_try):
            try:
                resp = requests.post(self.xzqurl, headers=HEADER, data=data, proxies=proxies, timeout=20)
            except Exception as e:
                print("获取行政区代码失败，开始重试")
                max_try -= 1
                continue
            else:
                if (resp.status_code == 200):
                    for ele in json.loads(resp.content)["data"]:
                        self.parseXZQ(ele)
                    break
                else:
                    max_try -= 1
                    continue

    def parseYT(self, data: dict):
        if ("children" in data.keys()):
            for ele in data["children"]:
                self.parseYT(ele)
        else:
            self.ytcode[data["id"]] = data["label"]

    def fetchYT(self):
        max_try = 5
        proxies = self.proxies.getProxy(True)
        while (max_try):
            try:
                resp = requests.post(self.yturl, headers=HEADER, proxies=proxies, timeout=20)
            except Exception as e:
                print("获取土地用途失败，开始重试")
                max_try -= 1
                continue
            else:
                if (resp.status_code == 200):
                    for ele in json.loads(resp.content)["data"]:
                        if (ele["id"] == "new"):
                            self.parseYT(ele)
                    break
                else:
                    max_try -= 1
                    continue
        if (max_try <= 0):
            raise Exception("获取土地用途失败!")
    
    def getResp(self, url: str, data: dict)->requests.Response:
        max_try = 5
        HEADER["hash"] = self.createHash(url.split("/")[-1])
        while (max_try):
            # time.sleep(5)
            proxies = self.proxies.getProxy()
            try:
                print("getResp开始下载\tMAX_TRY={}".format(max_try))
                resp = requests.post(url, headers=HEADER, data=json.dumps(data), proxies=proxies, timeout=30)
            except Exception as e:
                print("getResp: 获取{}失败!exceptions: {}".format(data, e))
                max_try -= 1
                continue
            break
        
        if (max_try <= 0):
            print("获取响应失败！data: {}".format(data))
            raise Exception("获取响应失败!")
        else:
            return resp
    
    def respValid(self, resp: requests.Response)->bool:
        if (resp.status_code == 200):
            tmp = json.loads(resp.content)
            if (len(tmp) != 0 and "code" in tmp.keys() and int(tmp["code"]) == 200):
                if ("data" in tmp.keys() and tmp["data"] != [] and tmp["data"] != {}):
                    return True
        return False
    
    def parseDetailList(self, resp_content: dict):
        relate = resp_content["relate"] if ("relate" in resp_content.keys()) else []
        data = resp_content["data"] if ("data" in resp_content.keys()) else {}
        self.detailqueue.put({"relate": relate, "data": data})
        # print("详情页响应为空")
    
    def detailValid(self, trueguid: dict, resp: requests.Response):
        pass
    
    def downloadDetailPage(self, url: str, guid: dict)->dict:
        max_try = 5
        while (max_try):
            try:
                resp = self.getResp(url, guid)
                if (not (self.respValid(resp) and self.detailValid(guid, resp))):
                    max_try -= 1
                    continue
            except Exception as e:
                print("获取{}的详情页失败！exceptions: {}".format(guid, e))
                max_try -= 1
                continue
            else:
                self.parseDetailList(json.loads(resp.content))
                break
        if (max_try <= 0):
            self.detailfailed.put(guid)
            print("获取{}的详情页失败，已加入失败队列！".format(guid))
    
    def downloadDetail(self, url: str):
        while (not self.guidqueue.empty()):
            self.downloadDetailPage(url, self.guidqueue.get())
    
    def getPageNum(self, resp_content: dict)->int:
        if (int(resp_content["data"]["pageSize"]) == 40):
            page_num = int(resp_content["data"]["total"]) / 40
            return int(page_num) + (1 if (page_num > int(page_num)) else 0)
        else:
            # print("网页返回了误导列表")
            raise Exception("网页返回了误导列表")
    
    def parseDataList(self, resp_content: dict):
        for ele in resp_content["data"]["list"]:
            self.listqueue.put(ele)
    
    def parseGuid(self):
        pass
    
    def listValid(self, resp: requests.Response)->bool:
        resp_content = json.loads(resp.content)
        datalist = resp_content["data"]["list"]
        for ele in datalist:
            if (self.provc not in ele["xzqFullName"]):
                print("provc:{}\txzqFullName:{}".format(self.provc, ele["xzqFullName"]))
                return False
        
        return True
    
    def downloadPage(self, url, data)->dict:
        max_try = 5
        while (max_try):
            try:
                resp = self.getResp(url, data)
                if (not (self.respValid(resp) and self.listValid(resp))):
                    # print(resp.content.decode())
                    max_try -= 1
                    continue
            except Exception as e:
                print("{}的第{}页失败！exceptions: {}".format(data["xzqDm"], data["pageNum"], e))
                max_try -= 1
                continue
            else:
                return json.loads(resp.content)
        self.listfailed.put([data["xzqDm"], data["pageNum"], None if ("tdYt" not in data.keys()) else data["tdYt"], False])
        raise Exception("{}的第{}页失败，已添加到失败队列！".format(data["xzqDm"], data["pageNum"]))
    
    def downloadAllPage(self, url: str, data: dict, page_num: int):
        """
        :@ url: 列表页面链接
        :@ data: post请求时需上传的数据

        * 该函数下载全部的列表页面，调用downloadPage下载单个页面。
        """
        for page in range(1, page_num+1):
            data["pageNum"] = page
            try:
                resp = self.downloadPage(url, data)
            except Exception as e:
                print("downloadAllPage exceptions: {}".format(e))
            else:
                self.pagequeue.put(resp)
    
    def downloadList(self, dataurl: str, code):
        """
        :@ dataurl: 列表页面链接
        :@ code: 行政区划代码

        * 该函数获取总页数，然后调用downloadAllPage函数下载全部列表页面。
        """
        max_try = 5
        data = {"pageNum": 1, "pageSize": 40, "xzqDm": code, "endDate": "", "startDate": ""}
        while (max_try):
            try:
                resp = self.getResp(dataurl, data)
                if (not (self.respValid(resp) and self.listValid(resp))):
                    max_try -= 1
                    continue
            except Exception as e:
                max_try -= 1
                continue
            else:
                page_num = self.getPageNum(json.loads(resp.content))
            break
        if (max_try <= 0):
            print("获取{}的页数失败，已添加到失败队列。".format(data))
            self.listfailed.put([code, 1, None, False])
        elif (page_num > 150):
            for tdyt in self.ytcode.keys():
                data = {"pageNum": 1, "pageSize": 40, "xzqDm": code, "tdYt": tdyt, "endDate": "", "startDate": ""}
                try:
                    resp = self.getResp(dataurl, data)
                    page_num = self.getPageNum(json.loads(resp.content))
                    if (not (self.respValid(resp) and self.listValid(resp))):
                        print("获取{}的页数时失败，exceptions: {}".format(code, e))
                        self.listfailed.put([code, 1, tdyt, True])
                        continue
                except Exception as e:
                    print("获取{}的页数失败, exceptions: {}".format(code, e))
                    self.listfailed.put([code, 1, tdyt, True])
                else:
                    self.downloadAllPage(dataurl, data, page_num)
        else:
            self.downloadAllPage(dataurl, data, page_num)

    def start(self):
        self.fetchXZQ()
        self.fetchYT()
        self.ignoreCode()
        for code in self.xzqcode.keys():
            self.provc = self.xzqcode[code]
            if (code in self.successcode):
                continue
            print("获取{}".format(code))
            self.downloadList(self.listurl, code)
            print("开始获取失败页面")
            self.downloadListFailed(self.listurl)

            while (not self.pagequeue.empty()):
                self.parseDataList(self.pagequeue.get())
            self.parseGuid()
            # while (not self.guidqueue.empty()):
            self.downloadDetail(self.detailurl)
            print("开始下载失败详情页")
            self.downloadDetailFailed(self.detailurl)
            self.writeFile(self.flname)
            self.writeSuccess(code)
