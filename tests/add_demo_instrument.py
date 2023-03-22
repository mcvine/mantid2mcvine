import os
thisdir = os.path.abspath(os.path.dirname(__file__))

import mantid2mcvine as m2m

def add_demo_instrument():
    instrument_name = 'MCVINEDEMO'
    beamline = 101
    mantid_idf = os.path.abspath(os.path.join(thisdir, '../notebooks/MCVINEDEMO_Definition.xml'))
    mcvine_idf = os.path.abspath('mcvine.xml')
    template_nxs = os.path.abspath('template.nxs')
    detsys_shape = m2m.shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.) # meters
    tofbinsize = 0.1 # mus
    im = m2m.InstrumentModel(
        instrument_name, beamline,
        mantid_idf, mcvine_idf, template_nxs,
        detsys_shape,
        tofbinsize = tofbinsize,
    )
    im.convert()
    im.mantid_install()
    import pickle as pkl
    pkl.dump(im, open("demo_instrument_model.pkl", "wb"))
    return


if __name__ == '__main__':
    add_demo_instrument()
