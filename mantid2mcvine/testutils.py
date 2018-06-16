def xml_equal(p1, p2):
    """compare two xml files. p1 and p2 are paths
    """
    r1 = load_xmltree_root(p1)
    r2 = load_xmltree_root(p2)
    return xmltree_equal_elements(r1, r2)


def xmltree_equal_elements(e1, e2):
    """compare two xml element tree e1 and e2 are roots of two trees
    """
    if e1.tag != e2.tag:
        print "tag: %r != %r" % (e1.tag, e2.tag)
        return False
    _strip = lambda v: (v or '').strip() # deal with None
    if _strip(e1.text) != _strip(e2.text):
        print "text: %r != %r" % (e1.text, e2.text)
        return False
    if _strip(e1.tail) != _strip(e2.tail):
        print "tail: %r != %r" % (e1.tail, e2.tail)
        return False
    if e1.attrib != e2.attrib:
        print "attrib: %r != %r" % (e1.attrib, e2.attrib)
        return False
    if len(e1) != len(e2):
        print "len: %r != %r" % (len(e1), len(e2))
        return False
    return all(xmltree_equal_elements(c1, c2) for c1, c2 in zip(e1, e2))


def load_xmltree_root(path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    return tree.getroot()
