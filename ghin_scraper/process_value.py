import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
from w3lib.html import replace_escape_chars
import re
from datetime import datetime


def processDate(val):
    #04/20/2017
    # 06/19/19 08:15:26 PM
    value = datetime.strptime(val,'%m/%d/%Y')
    return value.date()
def processDate_apm(val):
    # 06/19/19 08:15:26 PM
    value = datetime.strptime(val,'%m/%d/%y %H:%M:%S %p')
    return value.__str__()


def removeMoneySymbol(value):
    """remove money symbol

    Arguments:
        value {string} -- input value

    Returns:
        string -- output value
    """
    trim = re.compile(r'[^\d.,]+')
    value = trim.sub('', value)
    value = value.replace(",",".")
    return value

def getQuantity(value):
    """Get quantity in a string

    Arguments:
        value {string} -- input string

    Returns:
        string -- quantity
    """
    if value:
        value = str(value)
        value = re.findall(r'(\d+)', value, re.MULTILINE)
        if value:
            value = value[0]
            value = convertToInt(value)
        else:
            value = 0

    return value

def getMoney(value):
    """get money from a string

    Arguments:
        value {string} -- input value

    Returns:
        float -- money
    """
    if value is not None:
        trim = re.compile(r'[^\d.,]+')
        value = trim.sub('', value)
        value = value.replace(",","")
        return convertToFloat(value)
    else:
        return value

def convertToInt(value):
    """convert to int

    Arguments:
        value {string} -- input value

    Returns:
        float -- result
    """
    if value is None:
        return value
    try:
        return int(value)
    except ValueError:
        return None

def convertToFloat(value):
    """convert to float

    Arguments:
        value {string} -- input value

    Returns:
        float -- result
    """
    if value is None:
        return value
    try:
        return float(value)
    except ValueError:
        return None

def processText(value):
    """process to get text, clean specifix character

    Arguments:
        value {string} -- input value

    Returns:
        string -- out put value
    """
    if value:
        value = replace_escape_chars(value)
        value = remove_tags(value)
        return value
    else:
        return ''

def processFloat(value):
    """process to get float value

    Arguments:
        value {string} -- input string

    Returns:
        float -- output value
    """
    if value:
        value = getMoney(value)
        return value
    else:
        return ''

def processInt(value):
    if value:
        value = getQuantity(value)
        return value
    else:
        return ''

def processMoney(value):
    """input_processor to extract money to float

    Arguments:
        value {string} -- input value

    Returns:
        float -- return money in float
    """
    if value:
        value = getMoney(value)
        return value
    else:
        return ''

def processQuantity(value):
    """input_processor to get quantity from a string

    Arguments:
        value {string} -- Input value

    Returns:
        int -- quantity
    """
    if value:
        value = getQuantity(value)
        return value
    else:
        return ''

def processEmail(value):
    emails = re.findall(r'\b[\w.-]+?@\w+?\.\w+?\b', value)
    if emails:
        for email in emails:
            if email not in emails:
                emails.append(email)
    return email
