from lxml import etree
import lxml

class XmlReaderElement:
    def __init__(self, etree_element):
        self.list_of_unusable_tags = ['matrixMultipleChoice', 'header', 'page', 'responseDomain',
                                      'matrixQuestionSingleChoice', 'section', 'matrixQuestionOpen',
                                      'comparison', 'item', 'unit', 'display', 'body', 'multipleChoice']
        self.list_of_usable_tags = ['introduction', 'label', 'questionOpen', 'instruction', 'text',
                                    'questionSingleChoice', 'text', 'question', 'answerOption', 'title']
        self.tag = None
        self.uid = None
        self.uid_path = None
        self.tag_path = None
        self.label = False
        self.text = None
        self.labeltext = None
        self.page = None
        assert isinstance(etree_element, lxml.etree._Element)
        self.etree_element = etree_element
        self.walk_through_etree_element()
        self.append_uid_to_path()
        self.automatically_append_path_for_labels()
        self.remove_tabs_and_newlines_from_strings()

    def check_if_usable(self):
        if self.tag is None or self.tag in self.list_of_unusable_tags:
            return False
        elif self.tag in self.list_of_usable_tags:
            return True
        else:
            raise ValueError('Tag of type: "' + str(self.tag) + '" is not yet known - please add it either to:\ntext_de_exporter.XmlReaderElement.list_of_usable_tags\n or to:\n text_de_exporter.XmlReaderElement.list_of_usable_tags')


    def append_tag_path(self, string):
        assert isinstance(string, str)
        if string != '':
            if self.tag_path is not None:
                self.tag_path = string + '.' + self.tag_path
            if self.tag_path is None:
                self.tag_path = string
  
    def append_uid_path(self, string):
        assert isinstance(string, str)
        if string != '':
            if self.uid_path is not None:
                self.uid_path = string + '.' + self.uid_path
            if self.uid_path is None:
                self.uid_path = string

    def set_uid(self, uid):
        assert isinstance(uid, str)
        self.uid = uid

    def set_path(self, path):
        assert isinstance(path, str)
        self.uid_path = path

    def set_label(self, labeltext, label=True):
        self.label = label
        self.labeltext = labeltext

    def walk_through_etree_element(self):
        self.page = None
        self.tag = self.etree_element.tag.replace('{http://www.his.de/zofar/xml/questionnaire}', '').replace(
            '{http://www.dzhw.eu/zofar/xml/display}', '')
        self.uid = self.etree_element.attrib['uid']
        self.append_tag_path(self.tag)
        self.text = self.etree_element.text
        if 'label' in self.etree_element.attrib:
            self.set_label(labeltext=self.etree_element.attrib['label'], label=True)

        parent = self.etree_element.getparent()
        while parent is not None:
            if 'uid' in parent.attrib:
                self.append_uid_path(parent.attrib['uid'])
                self.append_tag_path(parent.tag.replace('{http://www.his.de/zofar/xml/questionnaire}', '').replace('{http://www.dzhw.eu/zofar/xml/display}', ''))
            if str(parent.tag) == '{http://www.his.de/zofar/xml/questionnaire}page':
                self.page = parent.attrib['uid']
            parent = parent.getparent()

    def automatically_append_path_for_labels(self):
        if self.uid_path is not None:
            if self.uid_path[self.uid_path.rfind('.'):] == '.label' and self.label:
                self.uid_path = self.uid_path[:self.uid_path.rfind('.')]
            if self.label:
                self.uid_path += '.label'

    def remove_tabs_and_newlines_from_strings(self):
        if self.text is not None:
            self.text = self.text.replace('"', '""').replace('\t', ' ').replace('\n', ' ').replace('     ', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')
        if self.labeltext is not None:
            self.labeltext = self.labeltext.replace('"', '""').replace('\t', ' ').replace('\n', ' ').replace('     ', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')

    def append_uid_to_path(self):
        if self.uid is not None and self.uid_path is not None:
            self.uid_path += '.' + self.uid

        if self.tag == 'text':
            self.uid_path += '_0'



class XmlReaderEtreeElements:
    def __init__(self):
        self.list_of_elements = []

    def add_xml_element(self, xml_element):
        assert isinstance(xml_element, XmlReaderElement)
        self.list_of_elements.append(xml_element)


class XmlReaderEtree:
    """
    """
    def __init__(self, file):
        with open(file, 'rb') as f:
            self.data_string = f.read()

        self.xml = etree.fromstring(self.data_string)

        self.tree = etree.ElementTree(self.xml)

        self.alternative_liste = []
        self.xml_elements = XmlReaderEtreeElements()
        self.iterate_through_all_elements()
        # self.liste_neu = self.sieve_through_list_of_all_elements()

    def remove_unusable_tags(self):
        tmp_indices_to_pop = []
        for i in range(0, len(self.xml_elements.list_of_elements)):
            if not self.xml_elements.list_of_elements[i].check_if_usable():
                tmp_indices_to_pop.append(i)
        # tmp_indices_to_pop = tmp_indices_to_pop[::-1]
        [self.xml_elements.list_of_elements.pop(i) for i in tmp_indices_to_pop[::-1]]


    def iterate_through_all_elements(self):
        tmp_uid_list = []
        for element in self.tree.iter():
            if 'uid' in element.attrib:
                self.xml_elements.add_xml_element(XmlReaderElement(element))

    def sieve_through_list_of_all_elements(self):
        liste_neu = []
        for entry in self.liste:
            if len(entry) > 5:
                if 'DONE' in entry:
                    entry.remove('DONE')
                    entry_path = entry[:3:-1]
                    # entry_path.sort(reverse=True)
                    if entry[2] is not None:
                        liste_neu.append(
                            entry[0] + '; ' + entry[1] + ".".join(entry_path) + '; "' + str(entry[2].replace('"', '\u201C')) + '"')
                    else:
                        liste_neu.append(".".join(entry_path) + '; ""')
        return liste_neu

file = '/home/a/ownCloud/questionnaire_turkey_new.xml'

x = XmlReaderEtree(file)

x.remove_unusable_tags()

class XmlReaderEtreeResult:
    def __init__(self, etree_element):
        self.etree_element = etree_element
        self.text = ''
        self.label = None
        self.path = ''


with open('/home/a/ownCloud/text_de.properties_edited', 'r') as f:
    data = f.read()

k = data.replace('[','').replace(']','').replace(' ', '').split(',')

w=  [i.uid_path for i in x.xml_elements.list_of_elements if i.uid_path not in k]
