from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

def convert_to_xml(d: dict) -> str:
    """
    Convert a flat key-value Python dictionary to an XML string.

    >>> convertToXml({'element1': 'value1', 'element2': 'value2'})
    '<element1>value1</element1><element2>value2</element2>'

    >>> convertToXml({'element': '<>&'})
    '<element>&lt;&gt;&amp;</element>'
    """
    root = Element('root')

    for key, value in d.items():
        element = SubElement(root, key)
        element.text = str(value)

    xml_string = tostring(root, encoding="unicode")
    return xml_string.replace('<root>', '').replace('</root>', '')

def convert_to_dict(xml_string: str) -> dict:
    """
    Convert an XML string representing a flat key-value dictionary to a Python dictionary.

    >>> convertToDict('<element1>value1</element1><element2>value2</element2>') == \
        {'element1': 'value1', 'element2': 'value2'}
    True

    >>> convertToDict('<element>&lt;&gt;&amp;</element>') == \
        {'element': '<>&'}
    True
    """
    def parse_element(element):
        children = list(element)
        if not children:
            return element.text if element.text else None
        return {child.tag: parse_element(child) for child in children}

    xml_string = '<root>' + xml_string + '</root>'
    root = fromstring(xml_string)
    result = parse_element(root)
    return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()