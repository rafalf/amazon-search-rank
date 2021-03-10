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
import re

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
AMAZON_URL = "https://www.amazon.com"


@contextmanager
def get_driver(headless, browser, minimize):

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

    for _ in range(10):
        try:
            d.get(AMAZON_URL)
            break
        except Exception as err:
            print(str(err))
            print("ERROR: d.get(AMAZON_URL) failed!")

            print("Recover: d.quit() & d = webdriver.Firefox()")
            d.quit()
            d = webdriver.Firefox()

            with open('fail.txt', 'ab') as file_hdlr:
                file_hdlr.write("ERROR: d.get(AMAZON_URL) failed!\n")
                file_hdlr.write(str(err))
                file_hdlr.write("------------------")

    # d.maximize_window()
    if minimize:
        d.set_window_position(-2000, 0)
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


def get_csv(input_file):
    if not input_file:
        input_file = 'search_in.csv'
    with open(input_file, 'rb') as f:
        reader = csv.reader(f)
        next(reader)  # heading
        rows = [row for row in reader]
    return rows


def append_output_row(row):
    with open(r'search_out.csv', 'ab') as f:
        writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)


def click_by_css(driver, selector, logger):
    try:
        el = get_element_clickable_by_css(driver, selector)
        el.click()
        return el
    except Exception as e:
        logger.info('click_by_css: %s' % e)
        raise Exception('click_by_css: %s' % e)


def send_by_css(driver, selector, value, logger, clear=True):
    try:
        el = get_element_by_css(driver, selector, logger)
        if clear:
            el.clear()
        el.send_keys(value)
        logger.info('send_by_css: sent: {}'.format(value))
    except Exception as e:
        logger.info('send_by_css: UnexpectedException: %s' % e)
        raise Exception('send_by_css: UnexpectedException: %s' % e)


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


def is_element_by_css(driver, css, time_out=0.5):
    try:
        return WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.CSS_SELECTOR, css))
                                                           , 'is_element_by_css: timed out on: %s' % css)
    except Exception:
        return None


def is_elem_concatenate_by_css(element, css):
    try:
        return element.find_element_by_css_selector(css)
    except Exception:
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
    input_data = get_csv(conf['search']['input'])
    logger = get_logger()
    next_selector = '.a-last>a'
    sponsored_append_selector = '[data-component-type="sp-sponsored-result"]'

    for search, exclude_words, include_words, run, comment in input_data:

        with get_driver(conf['headless'], conf['browser'], conf.get('minimize')) as driver:
            logger.info('loading: {} for search: {}'.format(AMAZON_URL, search))

            result = []

            try:
                if run != "yes":
                    result.append([search, 'marked as not to run'])
                    logger.info('marked as not to run')
                    continue

                send_by_css(driver, ".nav-search-field input", search, logger)
                click_by_css(driver, '[value="Go"]', logger)
                send_enter(driver)
                wait_out_spinner(driver, logger)

                idx = 0
                idx_incl_sponsored = 0
                for next_ctr in range(conf['search']['max_search']):
                    search_items = get_element_by_css(driver, '.s-desktop-toolbar .a-section', logger, True, 10)
                    if search_items:
                        logger.info('items found: {}'.format(search_items.text))
                        all_asins = get_all_elements_by_css(driver, '.s-result-item[data-asin][data-component-id]', logger)
                        for ctr, el in enumerate(all_asins, 1):
                            idx += 1  # rank excluding sponsored
                            idx_incl_sponsored += 1  # rank incl sponsored

                            asin_temp = el.get_attribute('data-asin')
                            if is_elem_concatenate_by_css(el, sponsored_append_selector):
                                # sponsored so deduct
                                idx -= 1
                                logger.info('found asin {} but its sponsored-products'.format(asin_temp))
                                continue

                            else:
                                if asin_temp != "":
                                    try:
                                        title = el.find_element_by_css_selector("span.a-text-normal").text.encode('utf-8')

                                        exclude_words_list = exclude_words.split(",")

                                        for word in exclude_words_list:
                                            exclude_match = bool(re.search(word, title, re.IGNORECASE))
                                            if exclude_match:
                                                break

                                        if exclude_words != "" and exclude_match:
                                            logger.info("Found excluded word: |%s| in: |%s|", word, title)
                                            continue

                                        include_words_list = include_words.split(",")
                                        for word in include_words_list:
                                            include_match = bool(re.search(word, title, re.IGNORECASE))
                                            if word != "" and not include_match:
                                                logger.info("Not found required word: |%s| in |%s|", word, title)
                                                continue
                                            elif word != "":
                                                logger.info("Found required word: %s in: %s", word, title)
                                                result.append([asin_temp, title])
                                                break
                                            else:
                                                result.append([asin_temp, title])
                                                break
                                    except:
                                        logger.info("Could not get title for asin: %s", asin_temp)
                    else:
                        # search item not found
                        result.append([search, 'searched items not found'])
                        logger.info('searched items not found')
                        break

                    if not is_element_by_css(driver, next_selector, 15):
                        logger.info('next button not found')
                        break
                    else:
                        click_by_css(driver, next_selector, logger)
                        logger.info('next {} clicked'.format(next_ctr + 1))
                        wait_out_spinner(driver, logger)

            except Exception as err:
                logger.error(err)
                result.append([search, err])

    logger.info('Summary:')
    for r in result:
        logger.info(r)
        append_output_row(r)


if __name__ == "__main__":
     main()