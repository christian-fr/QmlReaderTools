__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "Screenshotter"

# last edited: 2020/03/12

from selenium import webdriver


def check_if_string(string_check):
    return isinstance(string_check, str)


def check_if_list(list_of_URLs):
    return isinstance(list_of_URLs, list)


class Screenshotter:
    def __init__(self):
        self.output_prefix = 'screenshot'
        self.list_of_URLs = []
        self.base_URL = 'https://'
        self.suffix_URL = '.html'
        self.login = 'part45'
        self.login_URL = self.base_URL + '/' + 'special/login.html?zofar_token=' + self.login

        # init driver
        self.DRIVER = 'chromedriver'
        self.driver = webdriver.Chrome(self.DRIVER)

        self.width = 800
        self.height = 1600

        self.initialize_chromedriver()

    def import_URL_list(self, list_of_URLs):
        check_if_list(list_of_URLs)
        self.list_of_URLs = list_of_URLs

    def import_QML_page_list(self, list_of_QML_pages):
        check_if_list(list_of_QML_pages)
        self.create_URL_list_from_pages(list_of_QML_pages, self.base_URL + '/', self.suffix_URL)

    def create_URL_list_from_pages(self, list_of_QML_pages, URL_prefix, URL_suffix):
        if check_if_string(URL_prefix) and check_if_string(URL_suffix):
            tmp_list = []
            for entry in list_of_QML_pages:
                if check_if_string(entry):
                    tmp_list.append(URL_prefix + entry + URL_suffix)
                else:
                    raise TypeError
        else:
            raise TypeError
        self.list_of_URLs = tmp_list

    def set_output_prefix(self, new_prefix):
        self.output_prefix = new_prefix

    def iterate_through_list(self):
        for i in range(0, len(self.list_of_URLs)):
            nr = str(i).zfill(len(str(len(self.list_of_URLs))))
            self.run_screenshotter(self.list_of_URLs[i], nr)

    def run_screenshotter(self, URL, nr):
        self.driver.get(URL)
        screenshot = self.driver.save_screenshot(self.output_prefix + nr + '.png')

    def initialize_chromedriver(self):
        self.driver.get(self.login_URL)
        self.driver.set_window_size(self.width, self.height)

    def close_chromedriver(self):
        self.driver.quit()
