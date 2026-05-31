# 交叉编译工具链的常见前缀
# 这些是市面上最常见的交叉编译器前缀，用于自动检测
COMMON_TOOLCHAIN_PREFIXES = [
    "arm-linux-gnueabihf-",       # ARM Linux (硬浮点)
    "arm-linux-gnueabi-",         # ARM Linux (软浮点)
    "arm-buildroot-linux-gnueabihf-",  # Buildroot
    "aarch64-linux-gnu-",         # ARM64
    "arm-none-eabi-",             # ARM 裸机
    "arm-linux-",                 # 通用 ARM Linux
    "riscv64-linux-gnu-",         # RISC-V
    "mips-linux-gnu-",            # MIPS
]

# 构建时常见的目标架构
COMMON_ARCHS = ["arm", "arm64", "x86_64", "riscv", "mips"]

# 环境变量名
ENV_CROSS_COMPILE = "CROSS_COMPILE"
ENV_ARCH = "ARCH"
ENV_CC = "CC"
