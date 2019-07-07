"""
Requirements:
- scrapy>=1.4.0
- pymysql>=0.7.11

"""


import pprint
import pymysql
from scrapy.exceptions import DropItem
from pymysql.cursors import DictCursor
from pymysql import OperationalError
from pymysql.constants.CR import CR_SERVER_GONE_ERROR,  CR_SERVER_LOST, CR_CONNECTION_ERROR
from twisted.internet import defer
from twisted.enterprise import adbapi
import logging
logger = logging.getLogger(__name__)
# logger.setLevel('DEBUG')


class MySQLPipeline(object):  #
    """
    Defaults:
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = None
    MYSQL_PASSWORD = ''
    MYSQL_DB = None
    MYSQL_TABLE = None
    MYSQL_MARK_SCRAPED_TABLE   : None
    MYSQL_MARK_SCRAPED_KEY   : None
    MYSQL_MARK_SCRAPED_VALUE   : None
    MYSQL_UPSERT = False
    MYSQL_RETRIES = 3
    MYSQL_CLOSE_ON_ERROR = True
    Pipeline:
    ITEM_PIPELINES = {
       'scrapy_mysql_pipeline.MySQLPipeline': 300,
    }
    """
    stats_name = 'mysql_pipeline'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.stats = crawler.stats
        self.stats.set_value('done', 0)
        self.settings = crawler.settings
        db_args = {
            'host': self.settings.get('MYSQL_HOST', 'localhost'),
            'port': self.settings.get('MYSQL_PORT', 8889),
            'user': self.settings.get('MYSQL_USER', None),
            'password': self.settings.get('MYSQL_PASSWORD', ''),
            'db': self.settings.get('MYSQL_DB', None),
            'charset': 'utf8',
            'cursorclass': DictCursor,
            'cp_reconnect': True,
        }
        print("db_args",db_args)
        self.retries = self.settings.get('MYSQL_RETRIES', 3)
        self.close_on_error = self.settings.get('MYSQL_CLOSE_ON_ERROR', True)
        self.upsert = self.settings.get('MYSQL_UPSERT', False)
        self.table = self.settings.get('MYSQL_TABLE', None)
        self.db = adbapi.ConnectionPool('pymysql', **db_args)

    def close_spider(self, spider):
        self.db.close()

    @staticmethod
    def preprocess_item(item):
        """Can be useful with extremly straight-line spiders design without item loaders or items at all
        CAVEAT: On my opinion if you want to write something here - you must read
        http://scrapy.readthedocs.io/en/latest/topics/loaders.html before
        """
        return item

    def postprocess_item(self, *args):
        """Can be useful if you need to update query tables depends of mysql query result"""
        if len(args) > 1:
            if 'mark_parent_done_sql' not in args[0]:
                self.stats.inc_value('done')

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        # Start process insert db
        retries = self.retries
        status = False
        while retries:
            try:
                item = self.preprocess_item(item)
                yield self.db.runInteraction(self._process_item, item)
            except OperationalError as e:
                if e.args[0] in (
                        CR_SERVER_GONE_ERROR,
                        CR_SERVER_LOST,
                        CR_CONNECTION_ERROR,
                ):
                    retries -= 1
                    logger.info('%s %s attempts to reconnect left', e, retries)
                    self.stats.inc_value('{}/reconnects'.format(self.stats_name))
                    continue
                logger.exception('%s', pprint.pformat(item))
                self.stats.inc_value('{}/errors'.format(self.stats_name))
            except Exception:
                logger.exception('%s', pprint.pformat(item))
                self.stats.inc_value('{}/errors'.format(self.stats_name))
            else:
                status = True  # executed without errors
            break
        else:
            if self.close_on_error:  # Close spider if connection error happened and MYSQL_CLOSE_ON_ERROR = True
                spider.crawler.engine.close_spider(spider, '{}_fatal_error'.format(self.stats_name))
        self.postprocess_item(item, status)

        if self.stats.get_value('done') % 10 == 0:
            logger.info("--> Done %s/ %s", self.stats.get_value('done'), self.stats.get_value('total'))
        yield item

    def _generate_sql(self, data):
        table_name = self.table
        if 'table_name' in data:
            if data['table_name'] != '':
                table_name = data['table_name']


        columns = lambda d: ', '.join(['`{}`'.format(k) for k in d])
        values = lambda d: [v for v in d.values()]
        placeholders = lambda d: ', '.join(['%s'] * len(d))
        if self.upsert:
            sql_template = 'INSERT INTO `{}` ( {} ) VALUES ( {} ) ON DUPLICATE KEY UPDATE {}'
            on_duplicate_placeholders = lambda d: ', '.join(['`{}` = %s'.format(k) for k in d])
            return (
                sql_template.format(
                    table_name, columns(data),
                    placeholders(data), on_duplicate_placeholders(data)
                ),
                values(data) + values(data)
            )
        else:
            sql_template = 'INSERT INTO `{}` ( {} ) VALUES ( {} )'
            return (
                sql_template.format(table_name, columns(data), placeholders(data)),
                values(data)
            )

    def _process_item(self, tx, row):
        if 'mark_parent_done_sql' in row:
            try:
                # Mark parent done
                tx.execute(row['mark_parent_done_sql'], [])
                return
            except Exception:
                logger.error("Mark done SQL: %s", row['mark_parent_done_sql'])
                raise

        # Insert or update data in database
        sql, data = self._generate_sql(row)
        # logger.info(sql)
        try:
            tx.execute(sql, data)

        except Exception:
            logger.error("SQL: %s", sql)
            # logger.error("SQL: %s", upsql)
            raise
        self.stats.inc_value('{}/saved'.format(self.stats_name))


class PrintPipeline(object):
    def process_item(self, item, spider):
        print(item)
        yield item
