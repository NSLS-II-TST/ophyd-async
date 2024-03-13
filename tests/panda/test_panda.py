"""Test file specifying how we want to eventually interact with the panda..."""

import copy
from typing import Dict

import numpy as np
import pytest

from ophyd_async.core import DeviceCollector
from ophyd_async.core.utils import NotConnected
from ophyd_async.panda import PandA, PVIEntry, SeqTable, SeqTrigger
from ophyd_async.panda.panda import _remove_inconsistent_blocks


class DummyDict:
    def __init__(self, dict) -> None:
        self.dict = dict

    def todict(self):
        return self.dict


class MockPvi:
    def __init__(self, pvi: Dict[str, PVIEntry]) -> None:
        self.pvi = pvi

    def get(self, item: str):
        return DummyDict(self.pvi)


class MockCtxt:
    def __init__(self, pvi: Dict[str, PVIEntry]) -> None:
        self.pvi = copy.copy(pvi)

    def get(self, pv: str, timeout: float = 0.0):
        return MockPvi(self.pvi)


@pytest.fixture
async def sim_panda():
    async with DeviceCollector(sim=True):
        sim_panda = PandA("PANDAQSRV:", "sim_panda")

    assert sim_panda.name == "sim_panda"
    yield sim_panda


def test_panda_names_correct(sim_panda: PandA):
    assert sim_panda.seq[1].name == "sim_panda-seq-1"
    assert sim_panda.pulse[1].name == "sim_panda-pulse-1"


def test_panda_name_set():
    panda = PandA("", "panda")
    assert panda.name == "panda"


async def test_inconsistent_blocks():
    dummy_pvi = {
        "pcap": {},
        "pcap1": {},
        "pulse1": {},
        "pulse2": {},
        "sfp3_sync_out1": {},
        "sfp3_sync_out": {},
    }

    _remove_inconsistent_blocks(dummy_pvi)
    assert "sfp3_sync_out1" not in dummy_pvi
    assert "pcap1" not in dummy_pvi


async def test_panda_children_connected(sim_panda: PandA):
    # try to set and retrieve from simulated values...
    table = SeqTable(
        repeats=np.array([1, 1, 1, 32]).astype(np.uint16),
        trigger=(
            SeqTrigger.POSA_GT,
            SeqTrigger.POSA_LT,
            SeqTrigger.IMMEDIATE,
            SeqTrigger.IMMEDIATE,
        ),
        position=np.array([3222, -565, 0, 0], dtype=np.int32),
        time1=np.array([5, 0, 10, 10]).astype(np.uint32),  # TODO: change below syntax.
        outa1=np.array([1, 0, 0, 1]).astype(np.bool_),
        outb1=np.array([0, 0, 1, 1]).astype(np.bool_),
        outc1=np.array([0, 1, 1, 0]).astype(np.bool_),
        outd1=np.array([1, 1, 0, 1]).astype(np.bool_),
        oute1=np.array([1, 0, 1, 0]).astype(np.bool_),
        outf1=np.array([1, 0, 0, 0]).astype(np.bool_),
        time2=np.array([0, 10, 10, 11]).astype(np.uint32),
        outa2=np.array([1, 0, 0, 1]).astype(np.bool_),
        outb2=np.array([0, 0, 1, 1]).astype(np.bool_),
        outc2=np.array([0, 1, 1, 0]).astype(np.bool_),
        outd2=np.array([1, 1, 0, 1]).astype(np.bool_),
        oute2=np.array([1, 0, 1, 0]).astype(np.bool_),
        outf2=np.array([1, 0, 0, 0]).astype(np.bool_),
    )
    await sim_panda.pulse[1].delay.set(20.0)
    await sim_panda.seq[1].table.set(table)

    readback_pulse = await sim_panda.pulse[1].delay.get_value()
    readback_seq = await sim_panda.seq[1].table.get_value()

    assert readback_pulse == 20.0
    assert readback_seq == table


async def test_panda_with_missing_blocks(pva):
    panda = PandA("PANDAQSRVI:")
    with pytest.raises(AssertionError):
        await panda.connect()


async def test_panda_with_extra_blocks_and_signals(pva):
    panda = PandA("PANDAQSRV:")
    del panda.__annotations__["data"]  # This block isn't included in the test ioc
    await panda.connect()
    assert panda.extra  # type: ignore
    assert panda.extra[1]  # type: ignore
    assert panda.extra[2]  # type: ignore
    assert panda.pcap.newsignal  # type: ignore


async def test_panda_block_missing_signals(pva):
    panda = PandA("PANDAQSRVIB:")

    with pytest.raises(Exception) as exc:
        await panda.connect()
        assert (
            exc.__str__
            == "PandA has a pulse block containing a width signal which has not been "
            + "retrieved by PVI."
        )


async def test_panda_unable_to_connect_to_pvi():
    panda = PandA("NON-EXISTENT:")

    with pytest.raises(NotConnected) as exc:
        await panda.connect(timeout=0.01)

    assert exc.value._errors == "pva://NON-EXISTENT:PVI"
