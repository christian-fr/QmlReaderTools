__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "0.0.2"
__status__ = "Prototype"
__name__ = "Codebook Generator"

import pylatex
import os
import QuestionnaireElements

path_to_latex_templates = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
path_to_output_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'output', 'codebook')


class Codebook:
    def __init__(self, survey_title_string=None, qml_filename=None):
        self.latex_code_output = None
        self.list_of_codebook_pages = []
        self.survey_title = survey_title_string
        self.filename = qml_filename

    @property
    def survey_title(self):
        return self._survey_title

    @survey_title.setter
    def survey_title(self, survey_title_string):
        assert isinstance(survey_title_string, str) or survey_title_string is None
        self._survey_title = survey_title_string

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename_string):
        assert isinstance(filename_string, str) or filename_string is None
        self._filename = filename_string

    def generate_latex_code(self):
        self.__generate_latex_header()
        self.__generate_latex_body()
        self.__generate_latex_footer()

    def __generate_latex_header(self):
        with open(os.path.join(path_to_latex_templates, 'latex_templates' , 'latex_header_part1.txt'), 'r') as file:
            self.latex_code_output = file.read() + '\n'

        tmp_title = 'Codebook'

        if self.survey_title is not None and self.survey_title != '':
            tmp_title += '\\\\ \n' + self.survey_title.replace('_', '\\_')
        if self.filename is not None and self.filename != '':
            tmp_title += '\\\\ \\vspace{{1em}} \n\\large{{{0}}}'.format(self.filename.replace('_', '\\_'))

        self.latex_code_output += '\n\\title{{{0}}}'.format(tmp_title)

        with open(os.path.join(path_to_latex_templates, 'latex_templates' , 'latex_header_part2.txt'), 'r') as file:
            self.latex_code_output += file.read()

    def __generate_latex_body(self):
        for codebook_page_object in self.list_of_codebook_pages:
            self.latex_code_output += codebook_page_object.latex_code_output + '\n'

    def __generate_latex_footer(self):
        with open(os.path.join(path_to_latex_templates, 'latex_templates' , 'latex_footer.txt'), 'r') as file:
            self.latex_code_output += file.read()

    def add_codebook_page(self, codebook_page_object):
        assert isinstance(codebook_page_object, CodebookPage)
        self.list_of_codebook_pages.append(codebook_page_object)
        self.generate_latex_code()

    def write_latex_file(self, output_filename=os.path.join(path_to_output_dir, r'codebook.tex')):
        print(output_filename)
        with open(output_filename, 'w') as file:
            file.write(self.latex_code_output)


class CodebookTableOfContents:
    def __init__(self):
        pass


class CodebookVariableBaseclass:
    def __init__(self):
        pass


class CodebookPage:
    """
    has to contain the following sections:
    - variablename,
    - all introductory texts on the same page, *
    - question type
    - question texts/instructions/etc. *
    - answer options/items, *
    - other objects/questions/variables asked on the same page (as links within the same PDF) *
    - *[needs a footnotes property for visible conditions / iterated numnber]
    - footnotes objects (as a dict, access via method)

    """

    def __init__(self, variable_name):
        self.latex_code_output = None
        self.list_of_objects_on_page = []
        self.variable_name = variable_name

    def add_object(self, codebook_page_object):
        assert isinstance(codebook_page_object, CodebookTextElement)
        self.list_of_objects_on_page.append(codebook_page_object)
        self.generate_latex_code()

    def generate_latex_code(self):
        self.latex_code_output = '\\newpage\n'
        self.latex_code_output += '\\section{{{0}}}\n'.format(self.variable_name)
        for codebook_page_object in self.list_of_objects_on_page:
            self.latex_code_output += codebook_page_object.latex_code_output + '\n\n'


class CodebookTextElement:
    """
    provides LaTeX formatting for all Text elements: italics, bold, underlined
    """

    def __init__(self, text_value, formatting=None):
        self.__allowed_formatting_list = ['textsc', 'textit', 'textbf', 'texttt', 'underline']
        self.formatting = formatting
        self.text = text_value
        self.latex_code_output = None
        self.generate_latex_code_output()
        pass

    @staticmethod
    def __escape_latex_special_characters(input_string):
        return pylatex.utils.escape_latex(input_string)

    def generate_latex_code_output(self):
        tmp_text = self.text
        tmp_text = self.__escape_latex_special_characters(tmp_text)
        tmp_text = self.replace_zofar_layout_with_latex(tmp_text)
        tmp_text = self.replace_zofar_layout_with_latex(tmp_text)
        tmp_text = self.set_latex_formatting(input_string=tmp_text, formatting=self.formatting)
        tmp_text = tmp_text.replace('\n\n\n\n', '\n')
        tmp_text = tmp_text.replace('\n\n\n', '\n')
        tmp_text = tmp_text.replace('\n\n', '\n')
        tmp_text = tmp_text.replace('\n', '\\\\')

        self.latex_code_output = '\\noindent ' + tmp_text

    @staticmethod
    def replace_zofar_layout_with_latex(input_string):
        output_string = input_string
        output_string = output_string.replace(r'\#\{layout.BLANK\}', ' ')
        output_string = output_string.replace(r'\#\{layout.BREAK\}', '\n')
        output_string = output_string.replace(r'\#\{layout.BOLD\_START\}', '\\textbf{')
        output_string = output_string.replace(r'\#\{layout.BOLD\_END\}', '}')
        output_string = output_string.replace(r'\#\{layout.UNDERLINED\_START\}', '\\underline{')
        output_string = output_string.replace(r'\#\{layout.UNDERLINED\_END\}', '}')
        return output_string
        tmp_text = tmp_text.r
    @staticmethod
    def set_latex_formatting(input_string, formatting):
        output_string = ''
        if input_string is None:
            output_string = None

        elif formatting is None:
            output_string = input_string
        elif formatting == 'textsc':
            output_string = '\\textsc{{{0}}}'.format(input_string)
        elif formatting == 'textit':
            output_string = '\\textit{{{0}}}'.format(input_string)
        elif formatting == 'textbf':
            output_string = '\\textbf{{{0}}}'.format(input_string)
        elif formatting == 'texttt':
            output_string = '\\texttt{{{0}}}'.format(input_string)
        elif formatting == 'underline':
            output_string = '\\underline{{{0}}}'.format(input_string)
        return output_string

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text_value):
        assert isinstance(text_value, str) or text_value is None
        if text_value == '' or text_value is None:
            self._text = None
        else:
            self._text = text_value.strip().replace('\t', ' ').replace('     ', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace('\n', '')
        pass

    @property
    def formatting(self):
        return self._formatting

    @formatting.setter
    def formatting(self, formatting):
        assert isinstance(formatting, str) or formatting is None
        if formatting in self.__allowed_formatting_list or formatting is None:
            self._formatting = formatting
        else:
            raise ValueError('Formatting style not allowed/unknown: "{0}".'.format(formatting))


class CodebookTextElementCanHaveFootnote(CodebookTextElement):
    def __init__(self, text_value, formatting=None, footnote_string=None):
        super().__init__(text_value=text_value, formatting=formatting)
        self.footnote = footnote_string
        self.add_footnote_to_latex_code()

    @property
    def footnote(self):
        return self._footnote

    @footnote.setter
    def footnote(self, footnote_object):
        assert isinstance(footnote_object, str) or isinstance(footnote_object, QuestionnaireElements.ConditionObject) or footnote_object is None
        if footnote_object is None:
            self._footnote = None
        elif isinstance(footnote_object, QuestionnaireElements.ConditionObject):
            self._footnote = str(footnote_object.condition)
        elif isinstance(footnote_object, str):
            self._footnote = footnote_object

    def add_footnote_to_latex_code(self):
        if self.footnote is not None and self.footnote != '' and self.latex_code_output is not None \
                and self.latex_code_output != '':
            self.latex_code_output = self.latex_code_output + '\\footnote{{{0}}}'.format(pylatex.utils.escape_latex(self.footnote))


class CodebookTextVariableName(CodebookTextElement):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


class CodebookTextQuestionType(CodebookTextElement):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


class CodebookTextQuestionTexts(CodebookTextElementCanHaveFootnote):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


class CodebookTextAnswerOption(CodebookTextElementCanHaveFootnote):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


class CodebookTextItems(CodebookTextElementCanHaveFootnote):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


class CodebookTextOtherVariablesOnSamePage(CodebookTextElement):
    def __init__(self, text_value):
        super().__init__(text_value=text_value)
        pass


# te1 = CodebookTextElementCanHaveFootnote(text_value=r'asd\asd a_sd a&&s sad', formatting='textsc')
# te2 = CodebookTextElementCanHaveFootnote(text_value=r'asdasd #{layout.BOLD_START}asd #{layout.UNDERLINED_START}as#{'
#                                                  'layout.UNDERLINED_END}#{layout.BOLD_END} #{layout.BLANK}sad',
#                                        formatting='textsc', footnote_string='SHOW IF adbi01 = 2')
# print(te1.latex_code_output)

# pa1 = CodebookPage('adbi01')
# pa1.add_object(te1)
# pa1.add_object(te2)
#
# pa2 = CodebookPage('adbi02 ')
# pa2.add_object(te1)
# pa2.add_object(te2)
#
#
#
# cb = Codebook()
# cb.add_codebook_page(pa1)
# cb.add_codebook_page(pa2)
#
# cb.filename = 'questionnaire_nacaps.xml'
# cb.survey_title = 'Nacaps2020-1'
#
# cb.generate_latex_code()
#
# print(cb.latex_code_output)
#
# cb.write_latex_file(r'/home/christian/PycharmProjects/QmlReaderTools/output/codebook/codebook.tex')