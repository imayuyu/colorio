# -*- coding: utf-8 -*-
#
import numpy
import pytest

import colorio

numpy.random.seed(0)


@pytest.mark.parametrize('cls', [
    colorio.CAM02_LCD,
    colorio.CAM02_SCD,
    colorio.CAM02_UCS,
    ])
@pytest.mark.parametrize('xyz', [
    numpy.random.rand(3),
    numpy.random.rand(3, 7),
    ])
def test_conversion(cls, xyz):
    # test with srgb conditions
    L_A = 64 / numpy.pi / 5
    cam02 = cls(0.69, 20, L_A)
    out = cam02.to_xyz(cam02.from_xyz(xyz))
    assert numpy.all(abs(xyz - out) < 1.0e-14)
    return


@pytest.mark.parametrize('cls', [
    colorio.CAM02_LCD,
    colorio.CAM02_SCD,
    colorio.CAM02_UCS,
    ])
def test_srgb_gamut(cls, n=10):
    L_A = 64 / numpy.pi / 5
    cam02_ucs = cls(0.69, 20, L_A)
    cam02_ucs.srgb_gamut(n=n)
    return


if __name__ == '__main__':
    test_srgb_gamut(colorio.CAM02_LCD, n=50)
