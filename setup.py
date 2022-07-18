from setuptools import setup

setup(
    name='QmlReaderTools',
    version='1.0.14',
    packages=['gui', 'tests', 'codebook', 'pdfOutput', 'qmlReader', 'scrsht', 'advancedFlowchart'],
    url='',
    license='',
    author='christian-fr',
    author_email='',
    description='',
    install_requires=[
        'lxmL>=4.5.0',
        'Pillow>=7.0.0',
        'networkx>=2.6.3',
        'pygraphviz>=1.7'
    ]
)
