
import xml.etree.ElementTree as ET
import os, shutil, warnings, glob

class DefinitionExists(Exception): pass
class BeamlineOccupied(Exception): pass

def install_mantid_xml_to_userhome(mantid_xml, beamline=99, mantid_instr_dir=None):
    # NOTE: it seems mantid_instr_dir has to be ~/.mantid.
    # NOTE: setting it to $PREFIX/instrument does not work. the facilities.xml under ~/.mantid has higher priority
    assert mantid_xml.endswith('.xml')
    fn_base = os.path.basename(mantid_xml)
    if "_Definition" not in mantid_xml:
        raise RuntimeError('Filename %s does not conform to the convention {name}_Definition[_date].xml' % fn_base)
    instr_name, date = fn_base[:-4].split('_Definition')
    # get instrument name
    tree = ET.parse(mantid_xml)
    root = tree.getroot()
    instrument_name = root.attrib['name']
    # Facilities.xml
    mantid_instr_dir = mantid_instr_dir or os.path.expanduser("~/.mantid/instrument")
    assert os.path.exists(mantid_instr_dir)
    # check IDF file
    dest = os.path.join(mantid_instr_dir, fn_base)
    if os.path.exists(dest):
        raise DefinitionExists("%s" % dest)
    fac_xml = os.path.join(mantid_instr_dir, 'Facilities.xml')
    assert os.path.exists(fac_xml)
    # create new Facilities.xml
    tree = ET.parse(fac_xml)
    root = tree.getroot()
    sns = root.find("facility[@name='SNS']")
    tmp = sns.find("instrument[@name='%s']" % instrument_name)
    if tmp is not None:
        # skip if instrument already added
        warnings.warn("Instrument %s already exists in %s" % (instrument_name, fac_xml))
    else:
        # check beamline
        tmp = sns.find("instrument[@beamline='%s']" % beamline)
        if tmp is not None:
            raise BeamlineOccupied("#%s" % beamline)
        # save a backup
        mk_bkup(fac_xml)
        # add entry
        arcs = sns.find("instrument[@name='ARCS']")
        t = arcs.copy()
        t.attrib['name'] = instrument_name
        t.attrib['beamline'] = '%s' % beamline
        sns.append(t)
        tree.write(fac_xml)
    # copy IDF file
    shutil.copyfile(mantid_xml, dest)
    # multiple versions
    all_defs = glob.glob(os.path.join(mantid_instr_dir, "%s_Definition*.xml" % instr_name))
    files = [p for p in all_defs if p != dest]
    if files:
        msg = "** multiple versions of IDF exists for %s: %s. Please check the valid-from and valid-to attributes." % (
            instr_name, files)
        warnings.warn(msg)
    return


def mk_bkup(path):
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    bkup = path + ".saved-" + now
    import shutil
    shutil.copyfile(path, bkup)
    return
    
