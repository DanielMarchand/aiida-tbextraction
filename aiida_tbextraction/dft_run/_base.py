from fsc.export import export

from aiida.work.workchain import WorkChain

from .reference_bands import ReferenceBandsBase
from .wannier_input import WannierInputBase


@export  # pylint: disable=abstract-method
class DFTRunBase(WorkChain):
    """
    """

    @classmethod
    def define(cls, spec):
        super(DFTRunBase, cls).define(spec)

        spec.expose_inputs(ReferenceBandsBase)
        spec.expose_inputs(WannierInputBase)

        spec.expose_outputs(ReferenceBandsBase)
        spec.expose_outputs(WannierInputBase)
