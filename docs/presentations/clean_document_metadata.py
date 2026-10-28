"""Set generic course metadata on the generated presentation and PDF."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import pymupdf
import argparse

for prefix, namespace in {
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}.items():
    ET.register_namespace(prefix, namespace)

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--stem', default='field-demo')
stem = parser.parse_args().stem
title = 'Learning public health informatics with interactive notebooks'
target = HERE / (stem + '.pptx')
temporary = HERE / (stem + '.metadata.pptx')
with ZipFile(target) as source, ZipFile(temporary, 'w') as output:
    for item in source.infolist():
        raw = source.read(item.filename)
        if item.filename == 'docProps/core.xml':
            root = ET.fromstring(raw)
            for tag, text in {
                '{http://purl.org/dc/elements/1.1/}title': title,
                '{http://purl.org/dc/elements/1.1/}creator': 'FETP Informatics',
                '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy': 'FETP Informatics',
            }.items():
                element = root.find(tag)
                if element is None:
                    element = ET.SubElement(root, tag)
                element.text = text
            raw = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        output.writestr(item, raw)
temporary.replace(target)
target = HERE / (stem + '.pdf')
temporary = HERE / (stem + '.metadata.pdf')
with pymupdf.open(target) as document:
    metadata = document.metadata
    metadata.update(title=title, author='FETP Informatics')
    document.set_metadata(metadata)
    document.save(temporary, garbage=4, deflate=True)
temporary.replace(target)
print('Set generic course title and author metadata on both documents.')
