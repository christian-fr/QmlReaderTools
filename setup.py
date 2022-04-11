from setuptools import setup

setup(
    name='QmlReaderTools',
    python_requires='>=3.8',
    version='1.0.14',
    packages=['gui', 'tests', 'codebook', 'pdfOutput', 'qmlReader', 'screenshotter', 'advancedFlowchart'],
    url='https://github.com/christian-fr/QmlReaderTools',
    license='MIT',
    author='Christian Friedrich',
    author_email='mail-python@chr-fr.net',
    description='QmlReaderTools - Toolbox for processing and analyzing QML files',
    install_requires=['networkx>=2.5',
                      'pygraphviz>=1.7',
                      'Pillow>=9.0.1',
                      'lxml>=4.6.2',
                      'pandas>=1.0.5',
                      'numpy>=1.19.1',
                      'setuptools>=57.0.0']
)
