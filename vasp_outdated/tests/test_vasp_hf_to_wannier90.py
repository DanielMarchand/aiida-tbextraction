# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>
"""
Tests for the workflow that calculates the Wannier90 input from VASP with hybrid functionals.
"""

import pytest

from insb_sample import get_insb_input  # pylint: disable=unused-import


@pytest.mark.vasp
def test_vasp_hf_wannier_input(
    configure_with_daemon,  # pylint: disable=unused-argument
    assert_finished,
    get_insb_input  # pylint: disable=redefined-outer-name
):
    """
    Runs the workflow that calculates Wannier90 inputs from VASP + hybrids on InSb with a coarse grid.
    """
    from aiida import orm
    from aiida.engine import run_get_node
    from aiida_tbextraction.fp_run.wannier_input import VaspWannierInput

    kpoints_mesh = orm.KpointsData()
    kpoints_mesh.set_kpoints_mesh([2, 2, 2])

    wannier_projections = orm.List()
    wannier_projections.extend(['In : s; px; py; pz', 'Sb : px; py; pz'])

    result, node = run_get_node(
        VaspWannierInput,
        kpoints_mesh=kpoints_mesh,
        wannier_parameters=orm.Dict(
            dict=dict(num_wann=14, num_bands=36, spinors=True)
        ),
        wannier_projections=wannier_projections,
        **get_insb_input
    )
    assert node.is_finished_ok
    assert all(
        key in result for key in
        ['wannier_input_folder', 'wannier_parameters', 'wannier_bands']
    )
    folder_list = result['wannier_input_folder'].get_folder_list()
    assert all(
        filename in folder_list
        for filename in ['wannier90.amn', 'wannier90.mmn', 'wannier90.eig']
    )
