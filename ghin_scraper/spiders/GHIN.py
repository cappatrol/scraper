# -*- coding: utf-8 -*-
import time
import csv
import sys
import scrapy
from scrapy.http.cookies import CookieJar
from ..items  import (ScoreMaintenance,GolferMaintenance,History)
from scrapy.loader import ItemLoader
from datetime import datetime
from datetime import timedelta
from hashlib import md5
from pymysql.cursors import DictCursor
import pymysql
import logging

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

# 5. Field Club - assn: 55 Club # 003 password: pfc1882
# 6. Terrace Park - assn # 11 Club # 0016 or 016 password 20tpcc14

class GhinSpider(scrapy.Spider):
    name = 'GHIN'
    allowed_domains = ['ghin.com']
    start_urls = ['http://ghp.ghin.com/GHPOnline/Club/LogonClub.aspx?ReturnUrl=%2fGHPOnline%2fClub%2fdefault.aspx',]
    sub_url = 'http://ghp.ghin.com/GHPOnline/Club/'
    sub2_url = 'http://ghp.ghin.com'

    # Config custom setting
    custom_settings = {
        'IS_STOP_REPORT'   : False,
        # 'MYSQL_TABLE'   : detail_item,
        # 'DOWNLOAD_TIMEOUT'   : 180,
        'ROTATING_PROXY_PAGE_RETRY_TIMES'   : 2,
        'RETRY_TIMES'   : 2,
        'HTTPERROR_ALLOWED_CODES': [],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 543,
            # 'ghin_scraper.middlewares.RandomUserAgentMiddleware': 400,
            # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware':543,
        },
        'ROTATING_PROXY_BAN_POLICY':'ghin_scraper.middlewares.MyDetectionPolicy',
        'ITEM_PIPELINES': {
            'ghin_scraper.pipelines.MySQLPipeline': 100,
            # 'ghin_scraper.pipelines.PrintPipeline': 200,
        },
    }

    def __init__(self, scraped_key=None, *args, **kwargs):
        self.custom={}
        super().__init__(*args, **kwargs)
        if scraped_key is not None:
            self.scraped_key = scraped_key
        else:
            self.scraped_key = datetime.now().strftime("%Y%m%d")

    def getInputFromDB(self, limit=100000):
        db_args = {
            'host': self.settings.get('MYSQL_HOST', 'localhost'),
            'port': self.settings.get('MYSQL_PORT', 8889),
            'user': self.settings.get('MYSQL_USER', None),
            'password': self.settings.get('MYSQL_PASSWORD', ''),
            'db': self.settings.get('MYSQL_DB', None),
            'charset': 'utf8',
            'cursorclass': DictCursor
        }
        sqlconnect = pymysql.connect(**db_args)
        try:
            with sqlconnect.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM clubs"
                sql += " LIMIT {}".format(limit)
                logger.info('==== select sql: %s', sql)
                cursor.execute(sql)
                items = cursor.fetchall()
        finally:
            sqlconnect.close()
        if not items:
            logger.info("NO MORE ITEM TO GET FROM DATABASE")
        return items


    def parse(self, response):
        clubs = self.getInputFromDB()
        for club in clubs:
            yield scrapy.FormRequest.from_response(response,formdata={ 'ctl00$cph$txtAssociation': club['assn'],
                        'ctl00$cph$txtClub': club['club_number'],
                        'ctl00$cph$txtPassword': club['password'],
                        }, callback=self.start_crawl, meta={'item':club})


    def start_crawl(self, response):
        item = response.meta['item'].copy()
        ass = response.xpath('//*[@id="cph_gvServices"]/tbody/tr')
        for i in ass:
            url = i.xpath('td[6]/a/@href').extract_first()
            sub_club_number = i.xpath('td[1]/text()').extract_first().rstrip()
            club_name = i.xpath('td[2]/text()').extract_first().strip()
            service_name = i.xpath('td[3]/text()').extract_first().strip()
            hole = i.xpath('td[4]/text()').extract_first().strip()
            item['AssociationsNumber'] = item['assn']
            item['club_number'] = item['club_number']
            item['sub_club_number'] = sub_club_number.strip()
            item['club_name'] =  club_name
            item['service_name'] =  service_name
            item['hole'] =  hole
            _full = self.sub_url + url
            request = scrapy.Request(_full, callback=self.list_names,method='POST',meta={'item':item})
            request.cookies['GolferSearch.aspx:ctl00$cph$gvGolfer$trPager$cboPagerSize'] = 2000
            yield request


    def list_names(self,response):
        item = response.meta['item'].copy()
        total = response.xpath('//*[@id="cph_lblCountTotal"]/text()').extract_first()
        users_link = response.xpath('//*[@id="cph_gvGolfer"]/tbody/tr/td[4]/a/@href').extract()
        for link in users_link:
            detail_url = self.sub2_url + link
            yield scrapy.Request(detail_url,callback=self.user,meta={'item':item})


    def user(self,response):
        item = response.meta['item'].copy()
        item['ghin_number'] = response.xpath('//*[@id="cph_lblGHINNumber"]/text()').extract_first()
        rows = response.xpath('//*[@id="cph_tabHI_tabHIHistory_gvHIHistory"]/tbody/tr')

        for row in rows:
            history = ItemLoader(item=History(), response=response)
            date = rows.xpath('td[1]/text()').extract_first()
            index = rows.xpath('td[2]/text()').extract_first()
            tscores = rows.xpath('td[3]/text()').extract_first()
            identify_data = f"{item['ghin_number']}{date}{index}{tscores}"
            history.add_value('id', md5((identify_data).encode('utf-8')).hexdigest())
            history.add_value('ghin_number',response.xpath('//*[@id="cph_lblGHINNumber"]/text()').extract_first())
            history.add_value('date',date)
            history.add_value('index',index)
            history.add_value('tscores',tscores)
            history.add_value('ref_url', response.url)
            history.add_value('scraped_key', self.scraped_key)
            history.add_value('created_at', datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            history.add_value('created_by', self.name)
            history.add_value('modified_at', datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            history.add_value('modified_by', self.name)
            history.add_value('table_name', ['history'])
            yield history.load_item()

        golfer = ItemLoader(item=GolferMaintenance(), response=response)
        golfer.add_value('associationsnumber',item['AssociationsNumber'])
        golfer.add_value('club_number',item['club_number'])
        golfer.add_value('sub_club_number',item['sub_club_number'])
        golfer.add_value('club_name',item['club_name'] )
        golfer.add_value('service_name',item['service_name'])
        golfer.add_value('hole',item['hole'])
        golfer.add_value('ghin_number',response.xpath('//*[@id="cph_lblGHINNumber"]/text()').extract_first())
        golfer.add_xpath('status','//*[@id="cph_lblStatus"]/text()')
        golfer.add_xpath('status_date','//*[@id="cph_lblStatusDate"]/text()')
        golfer.add_xpath('_type','//*[@id="cph_cboType"]/option[@selected]/text()')
        golfer.add_xpath('p_name','//*[@id="cph_tabLookup_tpGolfer_nameGolfer_txtPrefix"]/@value')
        golfer.add_xpath('f_name','//*[@id="cph_tabLookup_tpGolfer_nameGolfer_txtFirst"]/@value')
        golfer.add_xpath('m_name','//*[@id="cph_tabLookup_tpGolfer_nameGolfer_txtMiddle"]/@value')
        golfer.add_xpath('l_name','//*[@id="cph_tabLookup_tpGolfer_nameGolfer_txtLast"]/@value')
        golfer.add_xpath('s_l_name','//*[@id="cph_tabLookup_tpGolfer_nameGolfer_txtSuffix"]/@value')
        golfer.add_xpath('email','//*[@id="cph_tabLookup_tpGolfer_txtEmail"]/@value')
        golfer.add_value('ref_url', response.url)
        golfer.add_value('scraped_key', self.scraped_key)
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        golfer.add_value('created_at', timestamp)
        golfer.add_value('created_by', self.name)
        golfer.add_value('modified_at', timestamp)
        golfer.add_value('modified_by', self.name)
        golfer.add_value('table_name', 'golfer')
        yield golfer.load_item()


        maintenance_url = response.url.replace('GolferMaintenance','ScoreMaintenance')
        request = scrapy.Request(maintenance_url, callback=self.get_maintenance,method='POST',meta={'item':item})
        request.cookies['ScoreMaintenance.aspx:ctl00$cph$gvScores$trPager$cboPagerSize'] = 10000
        yield request


    def get_maintenance(self,response):
        item = response.meta['item'].copy()
        avg = response.xpath('//*[@id="cph_lblAvgDiff"]/text()').extract_first()
        playingindicator = response.xpath('//*[@id="cph_lblPlayingIndicator"]/text()').extract_first()
        _maintenances = response.xpath('//*[@id="cph_gvScores"]/tbody/tr')
        item['avg'] = avg
        item['playingindicator'] = playingindicator
        histories=[]
        for i,his in enumerate(_maintenances):
            score = ItemLoader(item=ScoreMaintenance(), response=response)
            score.add_value('ghin_number',item['ghin_number'])
            _type = his.xpath('td[1]/text()').extract_first()
            date = his.xpath('td[2]/text()').extract_first()
            _score = his.xpath('td[3]/b[number(.) = .]').extract_first().strip()
            if not _score:
                _score = his.xpath('td[3]/b/text()').extract_first().strip()
            cr_slope = his.xpath('td[4]/text()').extract_first()
            used = his.xpath('td[5]/text()').extract_first()
            diff = his.xpath('td[6]/text()').extract_first()
            course = his.xpath('td[7]/text()').extract_first()
            date_update = his.xpath('td[8]/text()').extract_first()
            score.add_value('type',_type)
            score.add_value('date',date)
            score.add_value('score',_score)
            score.add_value('cr_slope',cr_slope.strip())
            score.add_value('used',used.strip())
            score.add_value('diff',diff)
            score.add_value('course',course)
            score.add_value('date_update',date_update)
            score.add_value('ref_url', response.url)
            score.add_value('scraped_key', self.scraped_key)
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            score.add_value('created_at', timestamp)
            score.add_value('created_by', self.name)
            score.add_value('modified_at', timestamp)
            score.add_value('modified_by', self.name)
            score.add_value('table_name', 'score')
            identify_data= f'{item["ghin_number"]}-{type}-{date}-{score}-{cr_slope}-{used}-{diff}-{course}-{date_update}'
            score.add_value('id', md5((identify_data).encode('utf-8')).hexdigest())
            yield score.load_item()
