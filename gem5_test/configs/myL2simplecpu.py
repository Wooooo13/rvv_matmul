import m5
from m5.objects import *

m5.util.addToPath("../../")

import argparse

from myl2caches import *

thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "tests/test-progs/hello/bin/riscv/linux/hello",
)

parser = argparse.ArgumentParser(description="A simple system with 2-level cache.")
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
parser.add_argument("--l1i_size", help=f"L1 instruction cache size. Default: 32kB.")
parser.add_argument("--l1d_size", help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size", help="L2 cache size. Default: 256kB.")

options = parser.parse_args()


# create the system
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# Create a simple CPU
system.cpu = RiscvTimingSimpleCPU()

# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)

# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus
system.l2bus = L2XBar()

# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)

# Create a memory bus
system.membus = SystemXBar()

# Connect the L2 cache to the membus
system.l2cache.connectMemSideBus(system.membus)

# create the interrupt controller for the CPU
system.cpu.createInterruptController()

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(options.cmd)

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
if options.options:
    process.cmd = [options.cmd, options.options]
else:
    process.cmd = [options.cmd]
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
