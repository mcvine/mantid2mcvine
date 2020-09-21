def xml_equal(p1, p2):
    """compare two xml files. p1 and p2 are paths
    """
    r1 = load_xmltree_root(p1)
    r2 = load_xmltree_root(p2)
    return xmltree_equal_elements(r1, r2)


def xmltree_equal_elements(e1, e2):
    """compare two xml element tree e1 and e2 are roots of two trees
    """
    res = True
    if e1.tag != e2.tag:
        print("tag: %r != %r" % (e1.tag, e2.tag))
        res = False
    _strip = lambda v: (v or '').strip() # deal with None
    if _strip(e1.text) != _strip(e2.text):
        if not _equal_quantity(e1.text, e2.text):
            print("text: %r != %r" % (e1.text, e2.text))
            res = False
    if _strip(e1.tail) != _strip(e2.tail):
        print("tail: %r != %r" % (e1.tail, e2.tail))
        res = False
    if e1.attrib != e2.attrib:
        print("attrib: %r != %r" % (e1.attrib, e2.attrib))
        res = False
    if len(e1) != len(e2):
        print("len: %r != %r" % (len(e1), len(e2)))
        res = False
    for c1, c2 in zip(e1, e2):
        if not xmltree_equal_elements(c1, c2):
            res = False
    return res


from pyre.units import parser
unitparser = parser()
import numpy as np
def _equal_quantity(t1, t2):
    """if t1 and t2 are texts that can be parsed by pyre.units such as '1*cm",
    check if they are equal or close
    """
    try:
        q1 = unitparser.parse(t1)
        q2 = unitparser.parse(t2)
    except:
        return False
    if hasattr(q1, 'derivation') and hasattr(q2, 'derivation'):
        if q1.derivation!=q2.derivation: return False
        return np.isclose(q1.value, q2.value)
    return q1==q2

def test_equal_quantity():
    assert _equal_quantity('1', '1.')
    assert not _equal_quantity('a', 'b')
    assert not _equal_quantity('1', 'a')
    assert not _equal_quantity('1*m', '1*second')
    assert not _equal_quantity('1.1*deg', '1.1*radian')
    assert _equal_quantity('1.1*deg', '1.1*deg')
    return

def load_xmltree_root(path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    return tree.getroot()
