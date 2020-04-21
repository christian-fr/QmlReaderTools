__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "just for testing purposes"

import QmlReader
import Questionnaire
import lxml

file = "/home/a/PycharmProjects/QmlReaderTools/qml/Nacaps_questionnaire_generated.xml"

x = QmlReader.QmlReader(file, create_graph=False, draw=False, truncate=False)

# class NewQmlReader():
#     def __init__(self, qmlreader_object):  # needs to change when fully implemented!
#         self.root = qmlreader_object.root  # needs to change when fully implemented!

# y = NewQmlReader(x)

