import argparse
import os

import m5
from m5.objects import *

m5.util.addToPath("../../")

thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "tests/test-progs/hello/bin/riscv/linux/hello",
)

parser = argparse.ArgumentParser(
    description="A RISC-V O3CPU system with NO caches (direct memory access)."
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

options = parser.parse_args()

# Create the system
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# Create a O3CPU
system.cpu = RiscvO3CPU()

# Create memory bus (NO CACHES - direct to memory)
system.membus = SystemXBar()

# Connect CPU directly to membus (no caches!)
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

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
print(f"[config] RISC-V O3CPU (NO CACHE)")
print(f"[config] CPU: RiscvO3CPU, 1 core")
print(f"[config] NO L1 cache (direct memory access)")
print(f"[binary] {options.cmd}\n")

print("Beginning simulation...")
exit_event = m5.simulate()
print(f"\n[gem5] Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
