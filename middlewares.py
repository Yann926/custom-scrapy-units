# middlewares.py
import random
import base64
import logging
import time

from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from config import PROXIES,USER_AGENTS

logger = logging.getLogger(__name__)

class RandomUserAgent(UserAgentMiddleware):
    def __init__(self):
        self.user_agent_list = USER_AGENTS

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)


class RandomProxy(HttpProxyMiddleware):
    def __init__(self):
        self.proxy = random.choice(PROXIES)

    def process_request(self, request, spider):
        if self.proxy["user:pwd"]:
            print("Private Proxy...")
            # proxy_user_pwd should be formed as "USERNAME:PASSWORD"
            proxy_user_pwd = self.proxy["user:pwd"]
            encoded_user_pass = base64.b64encode(proxy_user_pwd)
            # set request's parameters
            request.meta['proxy'] = self.proxy["proxy"] # "https://183.151.41.66:1133"
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

        else:
            print("Public Proxy...")
            request.meta['proxy'] = self.proxy["proxy"]





from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name



class DownloaderMiddleware(RetryMiddleware):
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            logger.info("ExceptionResponseUrl: ",response.url," ErrorHTTPCode: ",response.status," Time: ",time.ctime())
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            logger.error("Exception Type: ",exception," ExceptionRequestUrl: ",request.url," Time: ",time.ctime())
            return self._retry(request, exception, spider)
        else:
            logger.info("Other Exception: ",exception)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})


# settings.py
DOWNLOADER_MIDDLEWARES = {
    'projectName.middlewares.RandomUserAgent': 400,
    'projectName.middlewares.RandomProxy': 410,
    'projectName.middlewares.DownloaderMiddleware': 420,

}



from datetime import datetime
# 日志文件
# LOG_FILE = '自定义名称.log'
date = datetime.now()
LOG_FILE = "log/scrapy-{}-{}-{}.log".format(date.year, date.month, date.day)
# 日志等级 最低级别
LOG_LEVEL = 'INFO'
# 是否启用日志（创建日志后，不需开启，进行配置）
LOG_ENABLED = False  # （默认为True，启用日志）
# 日志编码
LOG_ENCODING = 'utf-8'

# 如果是True ，进程当中，所有标准输出（包括错误）将会被重定向到log中
# 例如：在爬虫代码中的 print（）
LOG_STDOUT = False  # (默认为False)

# 等级分为5个级别    （大写）
# 最高等级5 - -严重错误 - -critical（CRITICAL）
# 等级4 - -----一般错误 - -error(ERROR)
# 等级3 - -----警告错误 - -warning(WARNING)
# 等级2 - -----一般信息 - -info(INFO)
# 等级1 - -----调试信息 - -debug(DEBUG)

