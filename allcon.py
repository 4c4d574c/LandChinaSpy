MAX_WORKER = 64

POSTDATA = {"endDate": "", "pageNum": "", "pageSize": 40, "startDate": ""}

HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
          "content-type": "application/json"}

XZQURL = "https://api.landchina.com/bptFieldEnum/xzq"
YTURL = "https://api.landchina.com/bptFieldEnum/tdytTreeList"
# 供地计划列表链接
GDJHURL = "https://api.landchina.com/tGyjh/plan/list"
# 供地计划详情页链接
GDJHDETAILURL = "https://api.landchina.com/tGyjh/plan/detail"
# 出让公告列表链接
CRGGURL = "https://api.landchina.com/tGygg/transfer/list"
# 出让公告详情页链接
CRGGDETAILURL = "https://api.landchina.com/tGygg/transfer/detail"
# 其他公告列表链接
QTGGURL = "https://api.landchina.com/tGygg/other/list"
# 其他公告详情页链接
QTGGDETAILURL = "https://api.landchina.com/tGygg/other/detail"
# 地块公示列表链接
DKGSURL = "https://api.landchina.com/tCjgs/deal/list"
# 地块公示详情页链接
DKGSDETAILURL = "https://api.landchina.com/tCjgs/deal/detail"
# 供地结果列表链接
GDJGURL = "https://api.landchina.com/tGdxm/result/list"
# 工地结果详情页链接
GDJGDETAILURL = "https://api.landchina.com/tGdxm/result/detail"
# 代理链接
# PROXYURL = "http://api.xiequ.cn/VAD/GetIp.aspx?act=getturn51&uid=53929&vkey=796074414FEA7E1092654657355241F9&num=1&time=6&plat=0&re=0&type=7&so=3&group=51&ow=1&spl=1&addr=&db=1"
PROXYURL = "http://api.xiequ.cn/VAD/GetIp.aspx?act=getturn82&uid=53929&vkey=796074414FEA7E1092654657355241F9&num=100&time=6&plat=0&re=1&type=7&so=1&group=51&ow=1&spl=1&addr=&db=1"