# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>
"""
Tests the workflow that optimizes a DFT-based tight-binding model for different strain values.
"""

import pytest


@pytest.mark.qe
def test_strained_fp_tb(
    configure_with_daemon,  # pylint: disable=unused-argument
    get_optimize_fp_tb_input,
):
    """
    Run the DFT tight-binding optimization workflow with strain on an InSb sample for three strain values.
    """
    from aiida.engine import run
    from aiida import orm
    from aiida_tbextraction.optimize_strained_fp_tb import OptimizeStrainedFirstPrinciplesTightBinding
    inputs = get_optimize_fp_tb_input()

    inputs['strain_kind'] = orm.Str('three_five.Biaxial001')
    inputs['strain_parameters'] = orm.Str('InSb')

    strain_list = [-0.1, 0, 0.1]
    inputs['strain_strengths'] = orm.List(list=strain_list)

    inputs['symmetry_repr_code'] = orm.Code.get_from_string('symmetry_repr')

    result = run(OptimizeStrainedFirstPrinciplesTightBinding, **inputs)
    print(result)
    for value in strain_list:
        suffix = '_{}'.format(value).replace('.', '_dot_').replace('-', 'm_')
        assert all(
            key + suffix in result
            for key in ['cost_value', 'tb_model', 'window']
        )
