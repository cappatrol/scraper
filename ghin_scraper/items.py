# -*- coding: utf-8 -*-
import datetime
import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from .process_value import (removeMoneySymbol,getQuantity,getMoney,convertToInt,convertToFloat,processText,processFloat,processInt,processMoney,processQuantity,processEmail,processDate,processDate_apm)

class BaseForAll(object):
    ref_url = scrapy.Field()
    created_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    created_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    scraped_key = scrapy.Field(
        output_processor=TakeFirst()
    )

class GolferMaintenance(scrapy.Item):
    club_number = scrapy.Field(output_processor=TakeFirst())
    associationsnumber = scrapy.Field(output_processor=TakeFirst())
    sub_club_number = scrapy.Field(output_processor=TakeFirst())
    club_name = scrapy.Field(output_processor=TakeFirst())
    service_name = scrapy.Field(output_processor=TakeFirst())
    hole = scrapy.Field(output_processor=TakeFirst())
    ghin_number = scrapy.Field(output_processor=TakeFirst())
    status = scrapy.Field(output_processor=TakeFirst())
    status_date = scrapy.Field(output_processor=TakeFirst())
    _type = scrapy.Field(output_processor=TakeFirst())
    p_name = scrapy.Field(output_processor=TakeFirst())
    f_name = scrapy.Field(output_processor=TakeFirst())
    m_name = scrapy.Field(output_processor=TakeFirst())
    l_name = scrapy.Field(output_processor=TakeFirst())
    s_l_name = scrapy.Field(output_processor=TakeFirst())
    email = scrapy.Field(output_processor=TakeFirst())

    ref_url = scrapy.Field(output_processor=TakeFirst())
    created_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    created_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    scraped_key = scrapy.Field(
        output_processor=TakeFirst()
    )

    table_name = scrapy.Field(
        output_processor=TakeFirst()
    )


class History(scrapy.Item,BaseForAll):
    id = scrapy.Field(output_processor=TakeFirst())
    ghin_number = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(
        input_processor=MapCompose(processDate),
        output_processor=TakeFirst()
    )
    index = scrapy.Field(output_processor=TakeFirst())
    tscores = scrapy.Field(output_processor=TakeFirst())
    ref_url = scrapy.Field(output_processor=TakeFirst())
    created_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    created_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    scraped_key = scrapy.Field(
        output_processor=TakeFirst()
    )

    table_name = scrapy.Field(
        output_processor=TakeFirst()
    )


class ScoreMaintenance(scrapy.Item,BaseForAll):
    id = scrapy.Field(output_processor=TakeFirst())
    ghin_number = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(output_processor=TakeFirst())
    score = scrapy.Field(
        input_processor=MapCompose(processText),
        output_processor=TakeFirst())
    cr_slope = scrapy.Field(output_processor=TakeFirst())
    used = scrapy.Field(output_processor=TakeFirst())
    diff = scrapy.Field(output_processor=TakeFirst())
    course = scrapy.Field(output_processor=TakeFirst())
    date_update = scrapy.Field(
        input_processor=MapCompose(processDate_apm),
        output_processor=TakeFirst()
        )
    ref_url = scrapy.Field()

    created_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    created_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    modified_by = scrapy.Field(
        output_processor=TakeFirst()
    )
    scraped_key = scrapy.Field(
        output_processor=TakeFirst()
    )

    table_name = scrapy.Field(
        output_processor=TakeFirst()
    )
