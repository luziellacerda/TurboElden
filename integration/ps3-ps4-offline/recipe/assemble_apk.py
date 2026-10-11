"""Build R128 with a closed ten-payload overlay on the preserved R126 base.

Reuses the exact R127 streaming/read-back/preservation/signature-freeze guards.
Adds an offline-only bridge DEX and native launch branches, and renews shared
online runtime identities. Does not package official emulator APKs, games or
firmware, install applications or change any server configuration.
"""
from pipeline_common import assembler

if __name__ == '__main__':
    assembler().main()
