from dataclasses import dataclass
from typing import Iterator, List

from event_model import StreamDatum, StreamResource, compose_stream_resource

from ophyd_async.core import SignalR, SignalRW
from ophyd_async.core.device import Device


class DataBlock(Device):
    filepath: SignalRW[str]
    filename: SignalRW[str]
    fullfilename: SignalR[str]
    numcapture: SignalRW[int]
    flushnow: SignalRW[bool]
    capture: SignalRW[bool]
    capturing: SignalR[bool]
    numwritten_rbv: SignalR[int]


@dataclass
class _HDFDataset:
    device_name: str
    block: str
    name: str
    path: str
    shape: List[int]
    multiplier: int


class _HDFFile:
    def __init__(self, full_file_name: str, datasets: List[_HDFDataset]) -> None:
        self._last_emitted = 0
        self._bundles = [
            compose_stream_resource(
                spec="AD_HDF5_SWMR_SLICE",
                root="/",
                data_key=f"{ds.device_name}-{ds.name}",
                resource_path=full_file_name,
                resource_kwargs={
                    "name": ds.name,
                    "block": ds.block,
                    "path": ds.path + ".Value",
                    "multiplier": ds.multiplier,
                },
            )
            for ds in datasets
        ]

    def stream_resources(self) -> Iterator[StreamResource]:
        for bundle in self._bundles:
            yield bundle.stream_resource_doc

    def stream_data(self, indices_written: int) -> Iterator[StreamDatum]:
        # Indices are relative to resource
        if indices_written > self._last_emitted:
            indices = dict(
                start=self._last_emitted,
                stop=indices_written,
            )
            self._last_emitted = indices_written
            for bundle in self._bundles:
                yield bundle.compose_stream_datum(indices)
        return None