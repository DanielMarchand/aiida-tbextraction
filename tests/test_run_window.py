# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>
"""
Tests for the workflow which evaluates a single set of energy window values.
"""

import os
import itertools

import pytest
import pymatgen
import numpy as np

from aiida import orm


@pytest.fixture
def run_window_input(sample):
    """
    Returns a function that creates the input for RunWindow tests.
    """
    def inner(window_values, slice_, symmetries):
        from aiida_bands_inspect.io import read_bands
        from aiida_tbextraction.model_evaluation import BandDifferenceModelEvaluation

        inputs = dict()

        input_folder = orm.FolderData()
        input_folder_path = sample('wannier_input_folder')
        for filename in os.listdir(input_folder_path):
            input_folder.put_object_from_file(
                path=os.path.abspath(
                    os.path.join(input_folder_path, filename)
                ),
                key=filename
            )
        inputs['wannier_input_folder'] = input_folder

        inputs['wannier_code'] = orm.Code.get_from_string('wannier90')
        inputs['tbmodels_code'] = orm.Code.get_from_string('tbmodels')
        inputs['model_evaluation_workflow'] = BandDifferenceModelEvaluation
        inputs['reference_bands'] = read_bands(sample('bands.hdf5'))
        inputs['model_evaluation'] = {
            'bands_inspect_code': orm.Code.get_from_string('bands_inspect'),
        }

        window = orm.List(list=window_values)
        inputs['window'] = window

        k_values = [
            x if x <= 0.5 else -1 + x
            for x in np.linspace(0, 1, 6, endpoint=False)
        ]
        k_points = [
            list(reversed(k)) for k in itertools.product(k_values, repeat=3)
        ]
        wannier_kpoints = orm.KpointsData()
        wannier_kpoints.set_kpoints(k_points)
        inputs['wannier_kpoints'] = wannier_kpoints

        wannier_bands = orm.BandsData()
        wannier_bands.set_kpoints(k_points)
        # Just let every energy window be valid.
        wannier_bands.set_bands(
            np.array([[-20] * 10 + [-0.5] * 7 + [0.5] * 7 + [20] * 12] *
                     len(k_points))
        )
        inputs['wannier_bands'] = wannier_bands

        a = 3.2395  # pylint: disable=invalid-name
        structure = orm.StructureData()
        structure.set_pymatgen_structure(
            pymatgen.Structure(
                lattice=[[0, a, a], [a, 0, a], [a, a, 0]],
                species=['In', 'Sb'],
                coords=[[0] * 3, [0.25] * 3]
            )
        )
        inputs['structure'] = structure
        wannier_parameters = orm.Dict(
            dict=dict(
                num_wann=14,
                num_bands=36,
                dis_num_iter=1000,
                num_iter=0,
                spinors=True,
                mp_grid=[6, 6, 6],
            )
        )
        inputs['wannier_parameters'] = wannier_parameters
        inputs['wannier_calculation_kwargs'] = dict(
            options={
                'resources': {
                    'num_machines': 1,
                    'tot_num_mpiprocs': 1
                },
                'withmpi': False
            }
        )
        if symmetries:
            inputs['symmetries'] = orm.SinglefileData(
                file=sample('symmetries.hdf5')
            )
        if slice_:
            slice_idx = orm.List()
            slice_idx.extend([0, 2, 3, 1, 5, 6, 4, 7, 9, 10, 8, 12, 13, 11])
            inputs['slice_idx'] = slice_idx
        return inputs

    return inner


@pytest.mark.parametrize('slice_', [True, False])
@pytest.mark.parametrize('symmetries', [True, False])
def test_run_window(
    configure_with_daemon, run_window_input, slice_, symmetries
):  # pylint:disable=unused-argument,redefined-outer-name
    """
    Runs the workflow which evaluates an energy window.
    """
    from aiida.engine import run
    from aiida_tbextraction.energy_windows.run_window import RunWindow

    result = run(
        RunWindow,
        **run_window_input([-4.5, -4, 6.5, 16],
                           slice_=slice_,
                           symmetries=symmetries)
    )
    assert all(key in result for key in ['cost_value', 'tb_model', 'plot'])


@pytest.mark.parametrize(
    'window_values',
    [
        [-4.5, 6.5, -4, 16],  # unsorted
        [-30, -30, 30, 30],  # inner window too big
        [0, 0, 0, 0],  # outer window too small
    ]
)
def test_run_window_invalid(
    configure_with_daemon, run_window_input, window_values
):  # pylint:disable=unused-argument,redefined-outer-name
    """
    Runs an the run_window workflow with invalid window values.
    """
    from aiida.engine import run
    from aiida_tbextraction.energy_windows.run_window import RunWindow

    result = run(
        RunWindow,
        **run_window_input(window_values, slice_=True, symmetries=True)
    )
    assert result['cost_value'] == float('inf')
