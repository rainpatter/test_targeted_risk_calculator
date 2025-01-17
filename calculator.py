
import pandas as pd
import numpy as np
import pprint

# input file from ECETOC to calculate lookup values

file = 'ECETOC-TRAworker-version3.2-final.XLSX - TRAlookup.csv'

df = pd.read_csv(
    file)

np.set_printoptions(legacy='1.25')

# ------------------------------------------------------------------- #

# CHANGE DICTIONARY VALUES HERE
# - dictionary below called 'example_user_inputs' is for calculation - constraints are detailed below in comments
# - if there is a list of options, please copy-paste the text string exactly as it is shown into the dictionary
# - once you have changed the values in the dictionary, please run the program

example_user_inputs = {
    # any substance name
    'substance_name': 'ethanol',
    # any cas number
    'cas_number': '64-17-5',
    # any decimal - g/mol
    'mol_weight': 46.069,
    # any decimal - DNEL or OEL (mg/m3)
    'long_term_inhalation': 950,
    # any decimal - DNEL or OEL (mg/kg/day)
    'long_term_dermal': 206,
    # any decimal - DNEL or OEL (mg/m3)
    'short_term_inhalation': 1900,
    # any decimal - DNEL or OEL (ug/cm2)
    'local_dermal': 10000,
    # any decimal - Pascal
    'vap_pressure_at_operating_temp': 7832.4225,
    # can be PROC1 to PROC25
    'proc': 'PROC7',
    # can be 'ind' or 'prof'
    'ind_prof': 'ind',
    # can be 'solid' or 'liquid'
    'phys_state': 'solid',
    # can be:
    # - 'very low'
    # - 'low'
    # - 'medium'
    # - 'high'
    'fugacity': 'low',
    # can be:
    # - 'outdoors'
    # - 'indoors - no or basic ventilation'
    # - 'indoors - good ventilation'
    # - 'indoors - enhanced ventilation'
    'ventilation': 'indoors - good ventilation',
    # can be:
    # - '<15min'
    # - '15min-1hr'
    # - '1-4hr'
    # - '>4hr'
    'duration': '15min-1hr',
    # can be:
    # - '<1%'
    # - '1-5%'
    # - '5-25%'
    # - '>25%'
    'concentration': '>25%',
    # can be:
    #  - 'yes'
    #  - 'no'
    'lev': 'no',
    # can be:
    #  - 'no RPE'
    #  - 'RPE90%'
    #  - 'RPE95%'
    'rpe_mask': 'no RPE',
    # can be:
    # - 'no PPE'
    # - 'PPE80%'
    # - 'PPE90%'
    # - 'PPE95%'
    'ppe_gloves': 'PPE95%',
    # can be:
    # - 'yes'
    # - 'no'
    'lev_dermal': 'yes'
}

# ------------------------------------------------------------------- #


def calc_fugacity_band(dict):
    vap = dict['vap_pressure_at_operating_temp']
    if vap < 0.01:
        fugacity_band = 'very low'
    elif 500 > vap >= 0.01:
        fugacity_band = 'low'
    elif 10000 >= vap >= 500:
        fugacity_band = 'medium'
    else:
        fugacity_band = 'high'
    return fugacity_band


def calculate_ventilation_reduction_factor(dict):
    vent = dict['ventilation']
    if vent == 'outdoors' or 'indoors - good ventilation':
        vrf = 0.7
    elif vent == 'indoors - enhanced ventilation':
        vrf = 0.3
    else:
        vrf = 1
    dict['ventilation_reduction_factor'] = vrf
    return vrf


def calculate_duration_reduction_factor_inhalation(dict):
    dur = dict['duration']
    if dur == '<15min':
        drfi = 0.1
    elif dur == '15min-1hr':
        drfi = 0.2
    elif dur == '1-4hr':
        drfi = 0.6
    else:
        drfi = 1
    dict['duration_reduction_factor_inhalation'] = drfi
    return drfi


def calculate_duration_reduction_factor_dermal(dict):
    phys = dict['phys_state']
    fug = dict['fugacity']
    vrf = dict['ventilation_reduction_factor']
    if (phys == 'solid') and (fug == 'medium' or 'high'):
        drfd = 1
    elif (phys == 'liquid') and (fug == 'very low' or 'low'):
        drfd = 1
    else:
        drfd = vrf
    dict['duration_reduction_factor_dermal'] = drfd
    return drfd


def calculate_concentration_reduction_factor(dict):
    conc = dict['concentration']
    if conc == '<1%':
        crf = 0.1
    elif conc == '1-5%':
        crf = 0.2
    elif conc == '5-25%':
        crf = 0.2
    else:
        crf = 1
    dict['concentration_reduction_factor'] = crf
    return crf


def calculate_rpe_reduction_factor(dict):
    rpe = dict['rpe_mask']
    if rpe == 'RPE90%':
        rrf = 0.1
    elif rpe == 'RPE95%':
        rrf = 0.05
    else:
        rrf = 1
    dict['rpe_reduction_factor'] = rrf
    return rrf


def calculate_ppe_reduction_factor(dict):
    ip = dict['ind_prof']
    ppe = dict['ppe_gloves']
    if ppe == 'PPE80%':
        prf = 0.2
    elif ppe == 'PPE90%':
        prf = 0.1
    elif (ip == 'prof') and (ppe == 'PPE95%'):
        prf = 0.1
    elif ppe == 'PPE95%':
        prf = 0.05
    else:
        prf = 1
    dict['ppe_reduction_factor'] = prf
    return prf


def calcule_multiplier_short_term(dict):
    phys = dict['phys_state']
    fug = dict['fugacity']
    proc = dict['proc']
    lev = dict['lev']
    if (phys == 'liquid' and fug == 'very low') and not (proc in ['PROC7', 'PROC11', 'PROC17', 'PROC18'] and (proc == 'PROC10' and lev == 'yes') and (proc == 'PROC19' and lev == 'no')):
        mst = 1
    else:
        mst = 4
    dict['multiplier_short_term'] = mst
    return mst


def generate_lookup_descriptor(dict):
    proc = dict['proc']
    phys = dict['phys_state']
    lev = dict['lev']
    fug = dict['fugacity']
    ip = dict['ind_prof']
    concat_string = proc+phys+lev+fug+ip
    dict['concat_lookup_descriptor'] = concat_string
    return concat_string


def calculate_initial_estimate_inhalation(dict):
    phys = dict['phys_state']
    fug = dict['fugacity']
    concat_string = dict['concat_lookup_descriptor']
    if phys == 'solid' and fug == 'very low':
        iei = 'n/a'
    elif phys == 'solid':
        try:
            iei = df.loc[df['descriptor/look-up term inhalation']
                         == concat_string, 'init exp inhalation'].iloc[0]
        except:
            # verify this
            iei = 'n/a'
    else:
        iei = 'n/a'
    dict['initial_estimate_inhalation'] = iei
    return iei


def calculate_initial_estimate_dermal(dict):
    phys = dict['phys_state']
    fug = dict['fugacity']
    concat_string = dict['concat_lookup_descriptor']
    if phys == 'solid' and fug == 'very low':
        ied = 'n/a'
    else:
        try:
            ied = df.loc[df['descriptor/look-up term inhalation']
                         == concat_string, 'init exp dermal'].iloc[0]
        except:
            # verify this
            ied = 'n/a'
    dict['initial_estimate_dermal'] = ied
    return ied


def calculate_initial_estimate_dermal_local(dict):
    phys = dict['phys_state']
    fug = dict['fugacity']
    concat_string = dict['concat_lookup_descriptor']
    if phys == 'solid' and fug == 'very low':
        iedd = 'n/a'
    else:
        try:
            iedd = df.loc[df['descriptor/look-up term inhalation']
                          == concat_string, 'init exp local dermal'].iloc[0]
        except:
            # verify this
            iedd = 'n/a'
    dict['initial_estimate_dermal_local'] = iedd
    return iedd


def calc_predicted_8hr_inhalatory_exposure(dict):
    iei = dict['initial_estimate_inhalation']
    if iei == 'n/a':
        p8ie = 'change input'
    elif dict['ventilation'] == 'outdoors' and dict['lev'] == 'yes':
        p8ie = 'change input'
    elif dict['ind_prof'] == 'prof' and dict['ventilation'] == 'indoors - enhanced ventilation' and dict['lev'] == 'yes':
        p8ie = 'change input'
    else:
        match = df.loc[df['descriptor/look-up term inhalation'] ==
                       dict['concat_lookup_descriptor'], 'reduction factor lev inhal'].iloc[0]
        print(match)
        p8ie = dict['initial_estimate_inhalation']*dict['ventilation_reduction_factor'] * \
            dict['duration_reduction_factor_inhalation'] * \
            dict['concentration_reduction_factor'] * \
            dict['rpe_reduction_factor']*match

    dict['predicted_8hr_inhalatory_exposure'] = round(p8ie, 4)
    return p8ie


def calc_predicted_8hr_dermal_exposure(dict):
    if dict['initial_estimate_dermal'] == 'n/a' or dict['predicted_8hr_inhalatory_exposure'] == 'change input':
        p8id = 'n/a'
    elif dict['lev_dermal'] == 'yes':
        match = df.loc[df['descriptor/look-up term inhalation'] ==
                       dict['concat_lookup_descriptor'], 'reduction factor LEV dermal'].iloc[0]
        p8id = dict['initial_estimate_dermal'] * dict['duration_reduction_factor_dermal'] * \
            dict['concentration_reduction_factor'] * \
            dict['ppe_reduction_factor'] * match
    else:
        p8id = p8id = dict['initial_estimate_dermal'] * dict['duration_reduction_factor_dermal'] * \
            dict['concentration_reduction_factor'] * \
            dict['ppe_reduction_factor']
    dict['predicted_8hr_dermal_exposure'] = round(p8id, 4)
    return p8id


def calc_predicted_short_term_inhalatory_exposure(dict):
    if dict['predicted_8hr_inhalatory_exposure'] == ('n/a' or 'change input'):
        pstie = 'n/a'
    else:
        pstie = dict['predicted_8hr_inhalatory_exposure'] * \
            dict['multiplier_short_term'] / \
            dict['duration_reduction_factor_inhalation']
    dict['predicted_short_term_inhalatory_exposure'] = round(pstie, 4)
    return pstie


def calc_predicted_local_dermal_exposure(dict):
    if dict['initial_estimate_dermal'] == 'n/a' or dict['predicted_8hr_inhalatory_exposure'] == 'change input':
        plde = 'n/a'
    elif dict['lev_dermal'] == 'yes':
        match = df.loc[df['descriptor/look-up term inhalation'] ==
                       dict['concat_lookup_descriptor'], 'reduction factor LEV dermal'].iloc[0]
        plde = dict['initial_estimate_dermal'] * dict['duration_reduction_factor_dermal'] * \
            dict['concentration_reduction_factor'] * \
            dict['ppe_reduction_factor'] * match
    else:
        plde = dict['initial_estimate_dermal'] * dict['duration_reduction_factor_dermal'] * \
            dict['concentration_reduction_factor'] * \
            dict['ppe_reduction_factor']
    dict['predicted_local_dermal_exposure'] = round(plde, 4)
    return plde


def calc_predicted_rcr_long_term_inhalation(dict):
    if dict['predicted_8hr_inhalatory_exposure'] == ('n/a' or 'change input'):
        prlti = 'n/a'
    else:
        prlti = dict['predicted_8hr_inhalatory_exposure'] / \
            dict['long_term_inhalation']
    dict['predicted_RCR_long_term_inhalation'] = round(prlti, 4)
    return prlti


def calc_predicted_rcr_long_term_dermal(dict):
    if dict['predicted_8hr_dermal_exposure'] == 'n/a':
        prltd = 'n/a'
    else:
        prltd = dict['predicted_8hr_dermal_exposure']/dict['long_term_dermal']
    dict['predicted_RCR_long_term_dermal'] = round(prltd, 4)
    return prltd


def calc_predicted_rcr_short_term_inhalation(dict):
    if dict['predicted_short_term_inhalatory_exposure'] == 'n/a':
        prsti = 'n/a'
    else:
        prsti = dict['predicted_short_term_inhalatory_exposure'] / \
            dict['short_term_inhalation']
    dict['predicted_rcr_short_term_inhalation'] = round(prsti, 4)
    return prsti


def calc_predicted_rcr_local_dermal(dict):
    if dict['predicted_local_dermal_exposure'] == 'n/a':
        prld = 'n/a'
    else:
        prld = dict['predicted_local_dermal_exposure']/dict['local_dermal']
    dict['predicted_rcr_local_dermal'] = round(prld, 4)
    return prld


def calculate_all(dict):
    calculate_ventilation_reduction_factor(dict)
    calculate_duration_reduction_factor_inhalation(dict)
    calculate_duration_reduction_factor_dermal(dict)
    calculate_concentration_reduction_factor(dict)
    calculate_rpe_reduction_factor(dict)
    calculate_ppe_reduction_factor(dict)
    calcule_multiplier_short_term(dict)
    generate_lookup_descriptor(dict)
    calculate_initial_estimate_inhalation(dict)
    calculate_initial_estimate_dermal(dict)
    calculate_initial_estimate_dermal_local(dict)
    calc_predicted_8hr_inhalatory_exposure(dict)
    calc_predicted_8hr_dermal_exposure(dict)
    calc_predicted_short_term_inhalatory_exposure(dict)
    calc_predicted_local_dermal_exposure(dict)
    calc_predicted_rcr_long_term_inhalation(dict)
    calc_predicted_rcr_long_term_dermal(dict)
    calc_predicted_rcr_short_term_inhalation(dict)
    calc_predicted_rcr_local_dermal(dict)
    return dict


calculated_dict = calculate_all(example_user_inputs)

pprint.pprint(dict((k, calculated_dict[k]) for k in (
    'predicted_8hr_dermal_exposure',
    'predicted_8hr_inhalatory_exposure',
    'predicted_RCR_long_term_dermal',
    'predicted_RCR_long_term_inhalation',
    'predicted_local_dermal_exposure',
    'predicted_rcr_local_dermal',
    'predicted_rcr_short_term_inhalation',
    'predicted_short_term_inhalatory_exposure'
)))
