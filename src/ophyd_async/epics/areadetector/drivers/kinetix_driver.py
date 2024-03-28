from enum import Enum

from ..utils import ad_rw
from .ad_base import ADBase



class KinetixTriggerMode(str, Enum):
    internal = "Internal"
    edge = "Rising Edge"
    gate = "Exp. Gate"



class KinetixDriver(ADBase):
    def __init__(self, prefix: str) -> None:
        super().__init__(prefix)
        # self.pixel_format = ad_rw(PixelFormat, prefix + "PixelFormat")
        self.trigger_mode = ad_rw(KinetixTriggerMode, prefix + "TriggerMode")

