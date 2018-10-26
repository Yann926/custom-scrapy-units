import requests
import json

# 处理表单数据
# Form表单中的数据放到字典中，再进行编码转换
# data = {
#     "mid":"30",
#     "csrf":''
# }
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

# 抓包抓到的POST请求地址
# url = "https://space.bilibili.com/ajax/member/GetInfo"
url = "http://www.xicidaili.com/nn/1"
# res = requests.post(url, data=data, headers=headers)
res = requests.get(url, headers=headers)
res.encoding = 'utf-8'
result = res.text

print(result)
