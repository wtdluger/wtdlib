import sys
from pathlib import Path
import os
import numpy as np
import pandas as pd

from scipy import interpolate as interp, integrate
import skimage as ski
from skimage import color


def spectra2xyz(df, observer=10, illuminant='D65'):
    """
    Integrates Spectra into XYZ Color Space using CMFS and SPD functions
    download from the CIE website on 25 April 2023 and saved into the
    repository.
    
    df: must be a dataframe with the following columns: 'nm' and '%R'
    
    parameters:
    observer: default 10.  CIE Standard Observer Can be either '2' or 
    '10' following skimage.color convention or input as integers 2 or 10
    illuminant: default 'D65'.  Can be 'A', 'D50', 'D65', or 'D75'
    """
    
    # Calculate Color Matching Function
    if (observer == 10) or (observer=='10'):
        # https://doi.org/10.25039/CIE.DS.sqksu2n5
        cmfs = pd.read_csv(
            Path(__file__).parent.joinpath('standards_cie', 'CIE_xyz_1964_10deg.csv'),
            names=['nm', 'xbar','ybar','zbar'],
        )
    elif (observer == 2) or (observer == '2'):
        # https://doi.org/10.25039/CIE.DS.xvudnb9b
        cmfs = pd.read_csv(
            Path(__file__).parent.joinpath('standards_cie', 'CIE_xyz_1931_2deg.csv'), 
            names=['nm', 'xbar','ybar','zbar'],
        )
    else:
        cmfs = pd.read_csv(
            Path(__file__).parent.joinpath('standards_cie', 'CIE_xyz_1964_10deg.csv'),
            names=['nm', 'xbar','ybar','zbar'],
        )
    cmfs = cmfs.sort_values(by='nm', ascending=True).set_index("nm")
    
    
    # Calculate Spectral Power Distribution Function
    # http://files.cie.co.at/204.xls
    if illuminant == 'D65':
        # https://doi.org/10.25039/CIE.DS.hjfjmt59
        spd = pd.read_csv(Path(__file__).parent.joinpath('standards_cie', 'd65.csv'))
    elif illuminant == 'A':
        # https://doi.org/10.25039/CIE.DS.8jsxjrsn
        spd = pd.read_csv(Path(__file__).parent.joinpath('standards_cie', 'a.csv'))
    elif illuminant == 'D50':
        # https://doi.org/10.25039/CIE.DS.etgmuqt5
        spd = pd.read_csv(Path(__file__).parent.joinpath('standards_cie', 'CIE_std_illum_D50.csv'))
    elif illuminant == 'D75':
        # https://doi.org/10.25039/CIE.DS.9fvcmrk4
        spd = pd.read_csv(Path(__file__).parent.joinpath('standards_cie', 'CIE_illum_D75.csv'))
    else:
        spd = pd.read_csv(Path(__file__).parent.joinpath('standards_cie', 'd65.csv'))
    spd = spd.sort_values(by='nm', ascending=True).set_index("nm")

    # Align SPD, CMFS, and Spectra to wavelength
    df_concat_x = pd.concat([df, cmfs.xbar, spd], axis=1).dropna()
    df_concat_y = pd.concat([df, cmfs.ybar, spd], axis=1).dropna()
    df_concat_z = pd.concat([df, cmfs.zbar, spd], axis=1).dropna()
    df_concat_n = pd.concat([cmfs.ybar, spd], axis=1).dropna()
    
    # Integrate SPD, CMFS, and Spectra, calculating CIE XYZ Color
    K = 1
    N = integrate.simpson(
        df_concat_n.ybar*df_concat_n.spd, x=df_concat_n.index, 
        dx=5, axis=-1
    )
    X = (K/N)*integrate.simpson(
        df_concat_x.xbar*df_concat_x.spd*df_concat_x['%R'], x=df_concat_n.index,
        dx=5, axis=-1
    )
    Y = (K/N)*integrate.simpson(
        df_concat_y.ybar*df_concat_y.spd*df_concat_y['%R'], x=df_concat_n.index,
        dx=5, axis=-1
    )
    Z = (K/N)*integrate.simpson(
        df_concat_z.zbar*df_concat_z.spd*df_concat_z['%R'], x=df_concat_n.index,
        dx=5, axis=-1
    )
    
    return np.array([X, Y, Z])
    
def spectra2lab(df, observer=10, illuminant='D65'):
    """
    Integrates Spectra into CIE L*a*b* Color Space using CMFS and SPD functions
    download from the CIE website on 25 April 2023 and saved into the
    repository.
    
    df: must be a dataframe with the following columns: 'nm' and '%R'
    
    parameters:
    observer: default 10.  CIE Standard Observer Can be either '2' or 
    '10' following skimage.color convention or input as integers 2 or 10
    illuminant: default 'D65'.  Can be 'A', 'D50', 'D65', or 'D75'
    """
    
    XYZ = spectra2xyz(df, observer=observer, illuminant=illuminant) / 100
    
    if (observer == '10') or (observer == 10):
        obs = '10'
    elif (observer == '2') or (observer == 2):
        obs = '2'
    else:
        obs = '10'
    if illuminant == 'D65':
        lume = 'D65'
    elif illuminant == 'A':
        lume = 'A'
    elif illuminant == 'D50':
        lume = 'D50'
    elif illuminant == 'D75':
        lume = 'D75'
    else:
        lume = 'D65'
    
    
    lab = color.xyz2lab(XYZ.reshape(-1,1,3), illuminant=lume, observer=obs).reshape(3,)
    
    return lab


def df_am1_5():
    """
    Returns the ASTM G-173 Air Mass 1.5 data as a DataFrame
    Units are as follows:
        Wavelength: nm
        AM 1.5 Spectral Irradiance: W*m-2*nm-1
    Data obtained from NREL
    https://www.nrel.gov/grid/solar-resource/spectra-am1.5.html
    """
    file_loc = Path(__file__).parent.joinpath('standards_cie', 'AM1.5G.xlsx')
    wb = 'ASTM G-173-03 AM1.5'
    df_am = pd.read_excel(file_loc, sheet_name=wb)
    
    df_am = df_am.rename(columns={
        'Wavelength (nm)':'Wavelength',
        'Extraterrestrial W*m-2*nm-1':'AM 1.5E',
        'Global tilt  W*m-2*nm-1':'AM 1.5G',
        'Direct+circumsolar W*m-2*nm-1':'AM 1.5D'
    })
    return df_am

def returnCCT(arr):
    """
    Takes an input color value (either XYZ or xy color), 
    and returns the CCT value as calculated using McCamy’s Approximation.
    Due to conversion to xyY color, XYZ can be in either 0-1 or 0-100 scale.

    Common XYZ values:
    AM1.5G: np.array([155.564, 160.315, 152.232])
    D65: 100*ski.color.xyz_tristimulus_values(illuminant="D65", observer="10")
    """
    if (arr.shape[0] == 3):
        xyz_light = arr.copy()
        xyY_light = xyz_light/xyz_light.sum()
    elif (arr.shape[0] == 2):
        xyY_light = arr.copy()
    else:
        xyY_light = np.array([-1, -1, -1])
    
    n = (xyY_light[0] - 0.3320) / (xyY_light[1] - 0.1858)
    cct = 449*n**3 + 3525*n**2 + 6823.3*n + 5520.33
    return cct


def returnCRI(df_measured, show_work=False):
    """
    Returns the Color Rendering Index of a light source, and optionally a
    dataframe of the Ri values.
    Takes a DataFrame input of L*a*b* color measurements of each of the
    Test Color Sample standards for determining CRI.  Columns of the dataframe
    must be as follows: 'Test Color Sample', 'L*', 'a*', 'b*'. 
    Test Color Sample' names must be: 'TCS01', 'TCS02', 'TCS03', 'TCS04', 
    'TCS05', 'TCS06', 'TCS07', 'TCS08', 'TCS09', 'TCS10', 'TCS11', 'TCS12', 
    'TCS13', 'TCS14','TCS15'.

    parameter: 
    show_work: default False.  If False, function only returns the CRI value.
    If True, function returns the CRI value and a dataframe of the Ri values.
    
    
    Data Obtained From: 
    https://www.waveformlighting.com/tech/cri-ra-test-color-samples-tcs
    """
    cri_path = Path(__file__).parent.joinpath('standards_cie', 'CRI_TCS.xlsx')
    df_cri = pd.read_excel(cri_path)
    df_cri[['L*', 'a*', 'b*']] = ski.color.rgb2lab(
        df_cri[['R','G','B']] / 255.0, illuminant='D65', observer='10'
    )

    dfR = pd.merge(
        df_cri[['Test Color Sample', 'L*','a*','b*']], df_measured,
        how='inner', on='Test Color Sample', suffixes=('_cri', '_test')
    )
    dfR['dL*'] = dfR['L*_cri'] - dfR['L*_test']
    dfR['da*'] = dfR['a*_cri'] - dfR['a*_test']
    dfR['db*'] = dfR['b*_cri'] - dfR['b*_test']
    dfR['dE'] = np.sqrt(dfR['dL*']**2 + dfR['da*']**2 + dfR['db*']**2)
    dfR['R'] = 100 - 4.6*dfR['dE']
    cri = float(dfR['R'].mean())
    
    if show_work:
        return cri, dfR
    else:
        return cri