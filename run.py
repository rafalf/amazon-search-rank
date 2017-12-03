# -*- coding: utf-8 -*-

from selenium import webdriver
from sys import platform
from contextlib import contextmanager
import logging
import logging.config
import yaml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import datetime
import time

LOGGING_CONFIG = {
    'formatters': {
        'brief': {
            'format': '[%(asctime)s][%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'brief',
            'filename': 'log.log',
            'maxBytes': '1024',
            'backupCount': '3',
        },
    },
    'loggers': {
        'main': {
            'propagate': False,
            'handlers': ['console', 'file'],
            'level': 'INFO'
        }
    },
    'version': 1
}
AMAZON_URL = "https://www.amazon.com/ref=nb_sb_noss_null"


@contextmanager
def get_driver(headless, browser):

    if browser == 'chrome':
        chromeOptions = webdriver.ChromeOptions()
        prefs = dict()
        prefs["credentials_enable_service"] = False
        prefs["password_manager_enabled"] = False
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.add_argument("--disable-extensions")
        chromeOptions.add_argument("--disable-infobars")
        if headless:
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--no-sandbox")
            chromeOptions.add_argument("--disable-gpu")
        if platform == 'darwin':
            d = webdriver.Chrome(chrome_options=chromeOptions)
        elif platform == 'linux' or platform == 'linux2':
            d = webdriver.Chrome(chrome_options=chromeOptions)
    else:
        d = webdriver.Firefox()

    d.get(AMAZON_URL)
    d.maximize_window()
    yield d
    #  teardown
    d.quit()


def get_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger('main')
    log.setLevel(level=logging.getLevelName('INFO'))
    return log


def get_config():
    with open('config.yaml', 'r') as yaml_file:
        yaml_config = yaml.load(yaml_file)
        return yaml_config


def get_csv():
    with open('input.csv', 'rb') as f:
        reader = csv.reader(f)
        next(reader)  # heading
        rows = [row for row in reader]
    return rows


def append_output_row(row):
    with open(r'output.csv', 'ab') as f:
        writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)


def click_by_css(driver, selector, logger):
    try:
        el = get_element_clickable_by_css(driver, selector)
        el.click()
        return el
    except Exception as e:
        logger.info('click_by_css: UnexpectedException: %s' % e)
        return None


def send_by_css(driver, selector, value, logger, clear=True):
    try:
        el = get_element_by_css(driver, selector, logger)
        if clear:
            el.clear()
        el.send_keys(value)
        logger.info('send_by_css: sent: {}'.format(value))
    except Exception as e:
        logger.info('send_by_css: UnexpectedException: %s' % e)
        return None


def get_element_clickable_by_css(driver, selector):
    return WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        , 'get_element_clickable_by_css: timed out on: %s' % selector)


def get_element_by_css(driver, css, logger, log=False, wait_time=30):
    try:
        return WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css))
                                                           , 'get_element_by_css: timed out on: %s' % css)
    except Exception as e:
        if log:
            logger.info("get_element_by_css " + str(e).strip())
            return None
        else:
            raise Exception(str(e))


def is_element_by_css(driver, css):
    try:
        return WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, css))
                                                           , 'is_element_by_css: timed out on: %s' % css)
    except Exception as e:
        return None


def get_all_elements_by_css(driver, selector, logger):
    try:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            , 'get_all_elements_by_css: timed out on: %s' % selector)

    except TimeoutException as e:
        logger.info(str(e))
    except Exception as e:
        logger.info(str(e))


def send_enter(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)

    cover = "#nav-cover"
    for _ in range(10):
        if is_element_by_css(driver, cover):
            actions.send_keys(Keys.ENTER)
            time.sleep(0.5)
        else:
            break


def wait_out_spinner(driver, logger):
    a = datetime.datetime.now()
    spinner = ".loadingSpinner"
    try:
        WebDriverWait(driver, 30).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, spinner))
                                                        , 'wait_out_spinner: timed out on: %s' % spinner)
        b = datetime.datetime.now()
        logger.info('took: {} to update'.format(b - a))
    except Exception as e:
        logger.error('UnexpectedException: %s' % e)


def get_today():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def main():

    conf = get_config()
    input_data = get_csv()

    with get_driver(conf['headless'], conf['browser']) as driver:
        logger = get_logger()
        logger.info('loaded: {}'.format(AMAZON_URL))

        result = []
        for asin, search, active, details in input_data:

            driver.get('https://www.amazon.com/ref=nb_sb_noss_null')
            found_asin = False
            if active != "yes":
                result.append([asin, search, get_today(), 'not active'])
                continue

            send_by_css(driver, ".nav-search-field input", search, logger)
            click_by_css(driver, '[value="Go"]', logger)
            send_enter(driver)
            wait_out_spinner(driver, logger)

            idx = 0
            for next_ctr in range(conf['max_search']):
                search_items = get_element_by_css(driver, '#s-result-count', logger, True, 10)
                if search_items:
                    logger.info('items found: {}'.format(search_items.text))
                    all = get_all_elements_by_css(driver, '.s-result-item[data-asin]', logger)
                    for ctr, el in enumerate(all, 1):
                        idx += 1
                        asin_temp = el.get_attribute('data-asin')
                        if asin_temp == asin:
                            result.append([asin, search, get_today(), next_ctr + 1, idx])
                            logger.info('found asin {} at place: {}'.format(asin, idx))
                            found_asin = True
                            break
                else:
                    # search item not found
                    result.append([asin, search, get_today(),"",'error: not found searched items returned'])
                    logger.info('searched items not returned')
                    break

                # asin not found yet
                if not found_asin:
                    if click_by_css(driver, '#pagnNextString', logger):
                        logger.info('asin not found - next {} clicked'.format(next_ctr + 1))
                        wait_out_spinner(driver, logger)
                    else:
                        # asin not found, unable to click next page
                        result.append([asin, search, get_today(),"",'error: unable to click next page: {}'.format(next_ctr + 1)])
                else:
                    break

            else:
                # asin not found, max search reached
                result.append([asin, search, get_today(),"", 'not found on pages: {}'.format(conf['max_search'])])
                logger.info('asin not found - max search reached'.format(conf['max_search']))

        logger.info('Summary:')
        for r in result:
            logger.info(r)
            append_output_row(r)


if __name__ == "__main__":
     main()