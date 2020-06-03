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
from selenium.webdriver.support.select import Select
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
        input_file = 'input.csv'
    with open(input_file, 'rb') as f:
        reader = csv.reader(f)
        next(reader)  # heading
        rows = [row for row in reader]
    return rows


def append_output_row(row, file_name):
    with open(file_name, 'ab') as f:
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


def click_by_xpath(driver, selector, logger):
    try:
        el = get_element_clickable_by_xpath(driver, selector)
        el.click()
        return el
    except Exception as e:
        logger.info('click_by_xpath: %s' % e)
        raise Exception('click_by_xpath: %s' % e)


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


def get_element_clickable_by_xpath(driver, selector):
    return WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, selector))
        , 'get_element_clickable_by_xpath: timed out on: %s' % selector)


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
    except Exception as e:
        return None


def is_elem_concatenate_by_css(element, css):
    try:
        return element.find_element_by_css_selector(css)
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


def wait_out_spinner(driver, logger, mute=False):
    a = datetime.datetime.now()
    spinner = ".cr-list-loading:not(.aok-hidden)"
    try:
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, spinner))
                                            , 'wait_out_spinner: timed out on: %s' % spinner)
            logger.info("Spinner happened")
        except:
            if mute is False:
                logger.info("Spinner did not happen")

        WebDriverWait(driver, 30).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, spinner))
                                                        , 'wait_out_spinner: timed out on: %s' % spinner)

        if mute is False:
            b = datetime.datetime.now()
            logger.info('took: {} to update'.format(b - a))
    except Exception as e:
        logger.error('UnexpectedException: %s' % e)


def get_today():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def do_reviews():

    conf = get_config()
    input_data = get_csv(conf['reviews']['input_file'])
    logger = get_logger()
    next_selector = '.a-last>a'
    max_range = conf.get('reviews').get("pages")
    if max_range is None:
        max_range = 1000

    separators = ['<i class="a-icon a-icon-text-separator" role="img" aria-label="|"></i>']

    logger.info('max_range set to: %s', max_range)

    for url, run_it in input_data:

        result = []

        logger.info('run url set to: %s', run_it)
        if run_it.lower() != "yes":
            logger.info('to enable url to run, set it to "yes"')
            continue

        with get_driver(conf['headless'], conf['browser'], conf.get('minimize')) as driver:
            logger.info('loading: %s', url)

            try:
                # load page
                driver.get(url)
                result.append(["START SCRAPING REVIEWS", url])

                # set most recent
                select = Select(get_element_by_css(driver, '.reviews-sort-order-options #sort-order-dropdown', logger))
                select.select_by_visible_text("Most recent")
                logger.info("Most recent selected")

                wait_out_spinner(driver, logger)

                for next_ctr in range(1, max_range + 1):

                    wait_out_spinner(driver, logger, True)

                    if conf['reviews']['dates_and_size']:
                        all_reviews = get_all_elements_by_css(driver, '.review-data>a', logger)
                        all_dates = get_all_elements_by_css(driver, '[data-hook="review-date"]', logger)

                        if len(all_reviews) != len(all_dates):
                            raise Exception("Check the script: length all_reviews != all_dates, %s != %s",
                                            len(all_reviews), len(all_dates))
                    else:
                        reviews_customer = get_all_elements_by_css(driver, "[id*='customer_review']", logger)

                        all_reviews = []
                        all_dates = []

                        for idx, customer in enumerate(reviews_customer):
                            reviews = customer.find_elements_by_css_selector('.review-data>a')
                            dates = customer.find_elements_by_css_selector('[data-hook="review-date"]')

                            if len(reviews) != len(dates):
                                logger.info('exclude (%d): reviews: %d, dates: %d', idx, len(reviews), len(dates))
                            else:
                                all_reviews.append(reviews[0])
                                all_dates.append(dates[0])
                                logger.info('include (%d): reviews: %d, dates: %d', idx, len(reviews), len(dates))

                    if all_reviews:
                        logger.info('found reviews: %d on page number: %d', len(all_reviews), next_ctr)

                        for review, review_date in zip(all_reviews, all_dates):
                            rev = review.get_attribute("innerHTML")
                            for sep in separators:
                                rev = rev.replace(sep, "|")
                            logger.info('rev: %s', rev)

                            temp = []
                            for item in rev.split("|"):
                                temp.append(item[item.find(":") + 1:])
                            temp.append(review_date.text)

                            if "What's this?" not in rev:
                                result.append(temp)
                                logger.info('result appended: %s', temp)
                            else:
                                logger.info('result not appended: What\'s this? found')

                    if not is_element_by_css(driver, next_selector, 2):
                        logger.info('next button not found')
                        break
                    else:
                        click_by_css(driver, next_selector, logger)
                        logger.info('next {} clicked'.format(next_ctr + 1))
                        wait_out_spinner(driver, logger)

                else:
                    logger.info('max search reached'.format(max_range))

            except Exception as err:
                logger.error("%s: error: %s", err.__class__.__name__, err)
                result.append([url, err])

        result.append(["COMPLETE SCRAPING REVIEWS", url])
        logger.info('Summary:')
        for r in result:
            logger.info(r)
            append_output_row(r, conf['reviews']['output_file'])


if __name__ == "__main__":
    do_reviews()
