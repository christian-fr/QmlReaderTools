__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "just for testing purposes"

import QmlReader
import Questionnaire

file = "/home/a/PycharmProjects/QmlReaderTools/qml/questionnaire.xml"

x = QmlReader.QmlReader(file, create_graph=False, draw=False, truncate=False)

