import argparse
import os

import m5
from m5.objects import *

m5.util.addToPath("../../")

from myl2caches import *

thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "tests/test-progs/hello/bin/riscv/linux/hello",
)

parser = argparse.ArgumentParser(
    description="A simple RISC-V system with only L1 caches (no L2)."
)
parser.add_argument(
    "-c",
    "--cmd",
    type=str,
    required=True,
    dest="cmd",
    help="Path to the binary to execute",
)
parser.add_argument(
    "-o",
    "--options",
    type=str,
    default=None,
    dest="options",
    help="Options to pass to the binary",
)
parser.add_argument(
    "--l1i_size",
    type=str,
    default="32kB",
    help="L1 instruction cache size. Default: 32kB",
)
parser.add_argument(
    "--l1d_size", type=str, default="64kB", help="L1 data cache size. Default: 64kB"
)

options = parser.parse_args()

# Create the system
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# Create a simple CPU
system.cpu = RiscvO3CPU()

# Create L1 caches
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)

# Connect caches to CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create memory bus (直接连接到内存，无L2)
system.membus = SystemXBar()

# Connect L1 caches directly to memory bus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Create interrupt controller
system.cpu.createInterruptController()

# Connect system port
system.system_port = system.membus.cpu_side_ports

# Create memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set workload
system.workload = SEWorkload.init_compatible(options.cmd)

# Create process
process = Process()
if options.options:
    process.cmd = [options.cmd, options.options]
else:
    process.cmd = [options.cmd]
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate and run
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"\n_____________________ Starting simulation ___________________")
print(f"[config] RISCV Simple CPU (L1 Only)")
print(f"[config] CPU: O3CPU")
print(f"[config] L1I: {options.l1i_size}, L1D: {options.l1d_size}")
print(f"[config] No L2 cache (direct to memory)")
print(f"[binary] {options.cmd}\n")

print("Beginning simulation...")
exit_event = m5.simulate()
print(f"\n[gem5] Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
