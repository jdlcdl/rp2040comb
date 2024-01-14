# rp2040comb

#### QSPI Flash inspection tools for rp2040 based Raspberry-Pico

---

## Tools in this repository

The following tools may be copy/pasted into the rp2040 console w/`<CTRL>-e`, or they may be run on another computer
against `/tmp/rp2040.flash_dump` assuming that file was previously saved from an rp2040 device.

* [mocked_Maix_utils.py](./mocked_Maix_utils.py):
ensures that `utils.flash_read()` is available, because tools here need it.

* [hash_flash.py](./hash_flash.py):
returns the sha256 hash of bytes in flash.

* [crc32_flash.py](./crc32_flash.py):
returns the crc32 checksum of bytes in flash.

* [hashcrc_flash.py](./hashcrc_flash.py):
returns the sha256 hash and the crc32 checksum of bytes in flash.

* [all_bytes_are.py](./all_bytes_are.py):
returns true if bytes in flash are the same as the one passed in.

* [hex_dump.py](./hex_dump.py):
a kludgy-yet-versatile implementation of hex_dump for visually inspecting bytes in flash.

* [uf2parse.py](./uf2parse.py):
a commandline parser of firmware.uf2 files for validity, size, checksums and/or flashdump.

---

Example usage:
* https://gist.github.com/jdlcdl/a464bc6cb4b8ea8b621a1bb4f57ba436

--- 

Tools here are ~~heavily borrowed~~ lazily stolen from https://github.com/jdlcdl/k210comb

