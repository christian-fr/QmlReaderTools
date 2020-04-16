__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.5"
__status__ = "Prototype"
__name__ = "QmlReader"

# last edited: 2020-04-16

from lxml import objectify
import networkx as nx
import logging

class QmlReader:
    """
    Class for Reading and extracting elements from QML-Files.

    self.dict_of_page_numbers:
        dictionary of: {lfdNr: 'pageNr/Uid'}

    self.dict_of_page_numbers_reversed:
        dictionary of: {'pageNr/Uid': lfdNr}

    """

    def __init__(self, file, create_graph=False, draw=False, truncate=False):
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up QmlReader')
        self.DiGraph = nx.DiGraph()

        with open(file, 'rb') as f:
            self.logger.info('reading file: ' + str(file))
            self.data = f.read()

        self.root = objectify.fromstring(self.data)

        self.title = 'Survey'
        self.set_title()

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

    def set_title(self):
        self.title = self.extract_title()

    def extract_title(self):
        return self.root.name.text

    def extract_questions_from_pages(self):
        pass

    def extract_headers_from_question(self):
        pass

    def extract_response_domains_from_question(self):
        pass

    def extract_items_from_response_domain(self):
        pass

    def extract_answeroptions_from_response_domain(self):
        pass

    def extract_transitions_from_pages_NEW(self):
        pass

    def extract_triggers_from_pages(self):
        pass