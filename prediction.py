
from __future__ import division
import os

import numpy as np

from sklearn.externals import joblib


human_names = {
    'z': {
        'name': 'isothermal bulk modulus',
        'units': 'GPa',
        'symbol': 'B',
        'rounding': 0
    },
    'y': {
        'name': 'enthalpy of formation',
        'units': 'kJ g-at.-1',
        'symbol': 'H',
        'rounding': 0
    },
    'x': {
        'name': 'heat capacity at constant pressure',
        'units': 'J K-1 g-at.-1',
        'symbol': 'C<sub>p</sub>',
        'rounding': 0
    },
    'k': {
        'name': 'Seebeck coefficient',
        'units': 'muV K-1',
        'symbol': 'S',
        'rounding': 1
    },
    'm': {
        'name': 'temperature for congruent melting',
        'units': 'K',
        'symbol': 'T<sub>melt</sub>',
        'rounding': 0
    }
}

periodic_elements = ['X',
                                                                                                                                                                                    'H',  'He',
'Li', 'Be',                                                                                                                                                 'B',  'C',  'N',  'O',  'F',  'Ne',
'Na', 'Mg',                                                                                                                                                 'Al', 'Si', 'P',  'S',  'Cl', 'Ar',
'K',  'Ca',                                                                                     'Sc', 'Ti', 'V',  'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
'Rb', 'Sr',                                                                                     'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',  'Xe',
'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W',  'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',  'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

periodic_numbers = [0,
                                                                                                                                                                                    1,    112,
2,    8,                                                                                                                                                     82,   88,   94,  100,  106,  113,
3,    9,                                                                                                                                                     83,   89,   95,  101,  107,  114,
4,   10,                                                                                        14,    46,   50,   54,   58,   62,   66,   70,   74,   78,   84,   90,   96,  102,  108,  115,
5,   11,                                                                                        15,    47,   51,   55,   59,   63,   67,   71,   75,   79,   85,   91,   97,  103,  109,  116,
6,   12,    16,    18,   20,  22,   24,    26,   28,   30,   32,   34,   36,   38,   40,  42,   44,    48,   52,   56,   60,   64,   68,   72,   76,   80,   86,   92,   98,  104,  110,  117,
7,   13,    17,    19,   21,  23,   25,    27,   29,   31,   33,   35,   37,   39,   41,  43,   45,    49,   53,   57,   61,   65,   69,   73,   77,   81,   87,   93,   99,  105,  111,  118]

pmin, pmax = 1, max(periodic_numbers)
periodic_numbers_normed = [(i - pmin)/(pmax - pmin) for i in periodic_numbers]


def get_descriptor(ase_obj, kappa=18, overreach=False):
    """
    From ASE object obtain
    a vectorized atomic structure
    populated to a certain fixed (relatively big) volume
    defined by kappa
    """
    if overreach: kappa *= 2

    norms = np.array([ np.linalg.norm(vec) for vec in ase_obj.get_cell() ])
    multiple = np.ceil(kappa / norms).astype(int)
    ase_obj = ase_obj.repeat(multiple)
    com = ase_obj.get_center_of_mass() # NB use recent ase version here, because of the new element symbols
    ase_obj.translate(-com)
    del ase_obj[[atom.index for atom in ase_obj if np.sqrt(np.dot(atom.position, atom.position)) > kappa]]

    ase_obj.center()
    ase_obj.set_pbc((False, False, False))
    sorted_seq = np.argsort(np.fromiter((np.sqrt(np.dot(x, x)) for x in ase_obj.positions), np.float))
    ase_obj = ase_obj[sorted_seq]

    DV = []
    for atom in zip(
        ase_obj.get_chemical_symbols(),
        ase_obj.get_scaled_positions()
    ):
        DV.append([
            periodic_numbers_normed[periodic_elements.index(atom[0])],
            np.sqrt(atom[1][0]**2 + atom[1][1]**2 + atom[1][2]**2)
        ])

    return np.array(DV).flatten()


def load_ml_model(prop_model_files):
    ml_model = {}
    for n, file_name in enumerate(prop_model_files, start=1):
        basename = file_name.split(os.sep)[-1]
        if basename.startswith('ml') and basename[3:4] == '_' and basename[2:3] in human_names:
            prop_id = basename[2:3]
            print("Detected property %s in file %s" % (human_names[prop_id]['name'], basename))
        else:
            prop_id = str(n)
            print("No property name detected in file %s" % basename)

        model = joblib.load(file_name)
        if hasattr(model, 'predict') and hasattr(model, 'metadata'):
            ml_model[prop_id] = model
            print("Model metadata: %s" % model.metadata)

    print("Loaded property models: %s" % len(ml_model))
    return ml_model


def get_legend(pred_dict):
    legend = {}
    for key in pred_dict.keys():
        legend[key] = human_names.get(key, {
            'name': 'Unspecified property ' + str(key),
            'units': 'arb.u.',
            'symbol': 'P' + str(key),
            'rounding': 0
        })
    return legend


def ase_to_ml_model(ase_obj, ml_model):
    result = {}
    descriptor = get_descriptor(ase_obj, overreach=True)
    d_dim = len(descriptor)

    if not ml_model: # testing

        test_prop = round(np.sum(descriptor))
        return {prop_id: {'value': test_prop, 'mae': 0, 'r2': 0} for prop_id in human_names.keys()}, None

    for prop_id, regr in ml_model.items(): # production

        if d_dim < regr.n_features_:
            continue
        elif d_dim > regr.n_features_:
            d_input = descriptor[:regr.n_features_]
        else:
            d_input = descriptor[:]

        try:
            prediction = regr.predict([d_input])[0]
        except Exception as e:
            return None, str(e)

        result[prop_id] = {
            'value': round(prediction, human_names[prop_id]['rounding']),
            'mae': round(regr.metadata['mae'], human_names[prop_id]['rounding']),
            'r2': regr.metadata['r2']
        }

    return result, None
