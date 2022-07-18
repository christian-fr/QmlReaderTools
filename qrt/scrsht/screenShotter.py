import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import os
from os import path
import logging
import time
import errno
from os import listdir, mkdir
import string
from pathlib import Path


def set_viewport_size(driver, width, height):
    assert isinstance(driver, webdriver.Chrome)
    assert isinstance(width, int) and isinstance(height, int)

    window_size = driver.execute_script("""
               return [window.outerWidth - window.innerWidth + arguments[0],
                 window.outerHeight - window.innerHeight + arguments[1]];
               """, width, height)
    driver.set_window_size(*window_size)


class Screenshotter:
    def __init__(self, url_server, url_survey, url_port, viewport_width=1024, viewport_height=1900,
                 language_suffix='de', token='part1', carousel=False, click_on_next_and_screenshot=False,
                 show_token=True, show_x_res=True, show_y_res=True, end_when_done=True, headless=True):
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up Screenshotter')

        self.click_on_next_and_screenshot = click_on_next_and_screenshot

        self.list_of_pages = []
        self.dict_of_URLs = []

        self.carousel = carousel

        self.URL_server = url_server
        self.URL_survey = url_survey
        self.URL_port = url_port

        self.token = token
        self.show_token = show_token
        self.show_x_res = show_x_res
        self.show_y_res = show_y_res

        self.browser_width = viewport_width
        self.browser_height = viewport_height

        self.base_URL = self.URL_server + ":" + self.URL_port + "/" + self.URL_survey

        # self.base_URL = 'http://localhost:8080/corona-sid-addon1'
        # self.base_URL = 'https://presentation.dzhw.eu/Eurostudent-Turkey'
        # self.base_URL = 'http://localhost:8080/Nacaps2020'
        # self.base_URL = 'http://presentation.dzhw.eu/Eurostudent-Albania'
        # self.base_URL = 'http://presentation.dzhw.eu/corona-sid-addon1'

        # self.base_URL = 'http://localhost:8080/Eurostudent-Albania'

        self.language_suffix = language_suffix

        # self.base_URL = 'http://presentation.dzhw.eu/Nacaps2020'
        self.suffix_URL = '.html'
        self.login = token
        self.login_URL = self.base_URL + '/' + 'special/login.html?zofar_token=' + self.login


        # init driver
        self.DRIVER = 'C:\\Users\\friedrich\\PycharmProjects\\Screenshotter_manual\\venv\\chromedriver\\chromedriver.exe'

        # set options
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')

        self.driver = webdriver.Chrome(self.DRIVER, chrome_options=self.options)
        self.output_prefix = 'screenshot'
        # self.output_folder = None

        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        self.end_when_done = end_when_done

        self.set_viewport()
        self.perform_login()

        # self.browser_width = self.driver.get_window_size()['width']
        # self.browser_height = self.driver.get_window_size()['height']

        self.workdir = os.getcwd()
        self.output_folder = self.prepare_output_folder(workdir=self.workdir, timestamp=True)
        # time.sleep(2)

    @property
    def end_when_done(self):
        return self._end_when_done

    @end_when_done.setter
    def end_when_done(self, end_when_done_bool):
        assert isinstance(end_when_done_bool, bool)
        self._end_when_done = end_when_done_bool

    def startup_logger(self, log_level=logging.DEBUG):
        """
        CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10, NOTSET: 0
        """
        logging.basicConfig(level=log_level)
        fh = logging.FileHandler("{0}.log".format('log_' + __name__))
        fh.setLevel(log_level)
        fh_format = logging.Formatter('%(name)s\t%(module)s\t%(funcName)s\t%(asctime)s\t%(lineno)d\t'
                                      '%(levelname)-8s\t%(message)s')
        fh.setFormatter(fh_format)
        self.logger.addHandler(fh)

    # def set_size(self, browser_width, height):
    #     assert isinstance(browser_width, int) and isinstance(height, int)
    #     self.viewport_width = browser_width
    #     self.viewport_height = height
    #     self.driver.set_window_size(self.viewport_width, self.viewport_height)

    def add_pages(self, list_of_pages):
        assert isinstance(list_of_pages, list)
        self.list_of_pages = list_of_pages
        self.translate_list_of_pages_into_dict_of_url()

    def translate_list_of_pages_into_dict_of_url(self):
        self.dict_of_URLs = {}
        for pagename in self.list_of_pages:
            self.dict_of_URLs[pagename] = self.base_URL + '/' + pagename + self.suffix_URL + '?zofar_lang=' + self.language_suffix

    def check_if_carousel(self, page):
        """

        :param page: uid of page
        :return: list of question uids
        """

        results_list = []
        max_number_of_parallel_shown_questions = 2
        question_uid_list = ['mqsc', 'msc', 'sc']

        uid_search_list = []
        for uid in question_uid_list:
            uid_search_list.append(str(uid))
            for i in [i for i in range(0, max_number_of_parallel_shown_questions)]:
                uid_search_list.append(str(uid) + str(i + 1))

        print("uid_search_list: " + str(uid_search_list))

        for uid in uid_search_list:
            # try:
            #     self.driver.find_element_by_xpath('//*[@id="form_' + page + '_' + uid + '_rd_carousel"]/div[2]/a[2]')
            #     results_list.append(uid)
            # except:
            #     pass
            try:
                tmp_xpath = '//*[@id="form_' + page + '_' + uid + '_rd_carousel"]/*'
                self.driver.find_element_by_xpath(tmp_xpath)
                results_list.append(uid)
            except:
                continue

        if len(results_list) == 0:
            return False, []
        else:
            return True, results_list

    def iterate_through_carousel(self, page, times, output_folder, nr, uids_list, browser_width):
        assert isinstance(output_folder, str) or isinstance(output_folder, Path)
        print("iterate_trough_carousel")
        counter = 0
        for i in range(0, 20):
            try:
                tmp_xpath = f'//*[@id="form_{page}_{uids_list[0]}_rd_carousel"]/ol/li[{str(i)}]'
                self.driver.find_element_by_xpath(tmp_xpath)
                counter = i
            except NoSuchElementException:
                pass
            try:
                tmp_xpath = f'// *[ @ id = "form_{page}_{uids_list[0]}_rd_carousel"] / div[1] / ol / li[{str(i)}]'
                self.driver.find_element_by_xpath(tmp_xpath)
                counter = i
            except NoSuchElementException:
                pass

        print('final: ' + str(counter))
        print(counter)

        j = 0
        for i in range(0, counter):
            self.make_screenshot(os.path.join(output_folder, nr + '__' + page + '##' + str(
                browser_width) + 'x1024##' + self.language_suffix + 'carouselform_' + page + '_carousel_slide' + str(
                j) + '.png'))
            for uid in uids_list:
                tmp_xpath = f'//*[@id="form_{page}_{uid}_rd_carousel"]/div[*]/a[2]'
                self.driver.find_element_by_xpath(tmp_xpath).click()
            time.sleep(1.5)
            j += 1

    def iterate_through_dict_of_pages(self, output_folder=None, output_token=False, end_when_done=True):
        browser_width = self.driver.get_window_size()['width']
        # if workdir is None:
        #     workdir = os.getcwd()
        if output_folder is None:
            output_folder = self.output_folder
        print("iterate_trough_dict_of_pages")
        length_number_string = len(str(len(self.dict_of_URLs)))
        i = 0
        for page in self.dict_of_URLs:
            nr = str(i).zfill(length_number_string)
            self.run_screenshotter(url=self.dict_of_URLs[page], nr=nr, page=page, browser_width=browser_width,
                                   output_token=output_token, output_folder=output_folder)
            i += 1
        if end_when_done:
            self.driver.close()

    def run_screenshotter(self, url, nr, page, browser_width, output_folder, output_token=False):
        assert isinstance(output_folder, str) or isinstance(output_folder, Path)
        assert isinstance(output_token, bool)
        assert isinstance(nr, str)
        assert isinstance(page, str)

        self.driver.get(url)
        question_uids = self.check_if_carousel(page)[1]
        if output_token:
            tmp_str = '##'
            for char in self.login:
                if char not in string.ascii_lowercase + string.ascii_uppercase + string.digits:
                    tmp_str += '-'
                else:
                    tmp_str += char
            token = tmp_str
        else:
            token = ''

        tmp_output_filename = nr + '__' + page + '##' + str(
            browser_width) + 'x1024##' + self.language_suffix + token + '.png'
        if self.carousel:
            if self.check_if_carousel(page)[0]:
                print(page, nr, url)
                self.iterate_through_carousel(page=page, times=15, nr=nr, uids_list=question_uids,
                                              browser_width=browser_width, output_folder=output_folder)
            else:
                self.make_screenshot(os.path.join(output_folder, tmp_output_filename))
        else:
            self.make_screenshot(os.path.join(output_folder, tmp_output_filename))

        if self.click_on_next_and_screenshot:
            time.sleep(1)
            self.driver.find_element_by_id('form:btPanel:forward:forwardBt').click()
            tmp_output_filename_next = os.path.splitext(tmp_output_filename)[0] + '_next_' + \
                                       os.path.splitext(tmp_output_filename)[1]
            self.make_screenshot(os.path.join(output_folder, tmp_output_filename_next))

    def make_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def set_viewport(self):
        set_viewport_size(self.driver, self.viewport_width, self.viewport_height)

    def close_chromedriver(self):
        self.driver.quit()

    @staticmethod
    def timestamp():
        """
        :return: string timestamp: YYYY-MM-DD-hh-mm
        """
        t = time.localtime()
        return time.strftime('%Y-%m-%d_%H-%M-%S', t)

    def prepare_output_folder(self, workdir, timestamp=True):
        if timestamp:
            output_folder = str(
                path.join(workdir, self.timestamp() + '_screenshots_' + self.URL_survey + '_' + self.language_suffix))
        else:
            output_folder = str(path.join(workdir, 'screenshots_' + self.URL_survey + '_' + self.language_suffix))

        if self.show_x_res:
            output_folder += '_' + str(self.browser_width)

        if self.show_x_res and self.show_y_res:
            output_folder += 'x'
        else:
            output_folder += '_'

        if self.show_y_res:
            output_folder += str(self.browser_height)

        if self.show_token:
            output_folder += '_' + str(self.token)

        self.logger.info('output_folder: ' + output_folder)
        try:
            mkdir(output_folder)
            self.logger.info('"' + output_folder + '" created.')
        except OSError as exc:
            self.logger.info('folder could not be created at first attempt: ' + output_folder)
            if exc.errno == errno.EEXIST and path.isdir(output_folder):
                self.logger.info('folder exists already: ' + output_folder)
                pass
            self.logger.exception('folder could not be created')

        return output_folder

    def perform_login(self):
        self.driver.get(self.login_URL)

#
# x = Screenshotter(url_server='localhost', url_survey='Nacaps2020-1', url_port='8080', token='part1', viewport_width=411,
#                   viewport_height=2000)
