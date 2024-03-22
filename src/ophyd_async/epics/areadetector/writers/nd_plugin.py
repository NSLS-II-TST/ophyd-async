from enum import Enum

from ophyd_async.core import Device
from ophyd_async.epics.signal import epics_signal_rw

from ..utils import ad_r, ad_rw


class Callback(str, Enum):
    Enable = "Enable"
    Disable = "Disable"


class DataType(str, Enum):
    Int8 = "Int8"
    UInt8 = "UInt8"
    Int16 = "Int16"
    UInt16 = "UInt16"
    Int32 = "Int32"
    UInt32 = "UInt32"
    Int64 = "Int64"
    UInt64 = "UInt64"
    Float32 = "Float32"
    Float64 = "Float64"


class ColorMode(str, Enum):
    Mono = "Mono"
    Bayer = "Bayer"
    RGB1 = "RGB1"
    RGB2 = "RGB2"
    RGB3 = "RGB3"
    YUV444 = "YUV444"
    YUV422 = "YUV422"
    YUV421 = "YUV421"


class NDArrayBase(Device):
    def __init__(self, prefix: str, name: str = "") -> None:
        self.unique_id = ad_r(int, prefix + "UniqueId")
        self.nd_attributes_file = epics_signal_rw(str, prefix + "NDAttributesFile")
        super().__init__(name)


class NDPluginBase(NDArrayBase):
    def __init__(self, prefix: str, name: str = "") -> None:
        self.nd_array_port = ad_rw(str, prefix + "NDArrayPort")
        self.enable_callback = ad_rw(Callback, prefix + "EnableCallbacks")
        self.nd_array_address = ad_rw(int, prefix + "NDArrayAddress")
        self.array_size0 = ad_r(int, prefix + "ArraySize0")
        self.array_size1 = ad_r(int, prefix + "ArraySize1")
        self.array_size2 = ad_r(int, prefix + "ArraySize2")
        self.data_type = ad_r(DataType, prefix + "DataType")
        self.color_mode = ad_r(ColorMode, prefix + "ColorMode")
        super().__init__(prefix, name)


class NDPluginStats(NDPluginBase):
    pass
