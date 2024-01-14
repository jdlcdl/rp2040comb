'''
    uf2parse.py

    parses a uf2 firmware file (filename as first argument),
    writes binary payload into file (filename as second argument),
    prints binary payload's sequence count, destination address, final size, crc32, sha256

    See https://microsoft.github.io/uf2/
'''

import binascii
import sys
import hashlib
import traceback

class UF2:
    def __init__(self, filename):
        if filename[-4:] == ".uf2":
            self.filename = filename
        self.f = None
        self.index = 0

    def open(self):
        self.f = open(self.filename, "rb")

    def next(self):
        answer = self.f.read(512)
        self.index += 1
        return answer

    def parse(self, bytes_512, last_sequence=None):
        first_magic = int.from_bytes(bytes_512[0:4], 'little')
        second_magic = int.from_bytes(bytes_512[4:8], 'little')
        flags = int.from_bytes(bytes_512[8:12], 'little')
        address = int.from_bytes(bytes_512[12:16], 'little')
        data_size = int.from_bytes(bytes_512[16:20], 'little')
        sequence = int.from_bytes(bytes_512[20:24], 'little')
        total_blocks = int.from_bytes(bytes_512[24:28], 'little')
        fs_bfid_zero = int.from_bytes(bytes_512[28:32], 'little')
        data = bytes_512[32:508]
        final_magic = int.from_bytes(bytes_512[508:512], 'little')

        assert first_magic == 0x0a324655
        assert second_magic == 0x9e5d5157
        if sequence: assert last_sequence + 1 == sequence
        if sequence: assert sequence < total_blocks
        assert final_magic == 0x0ab16f30
        if data[data_size:-24] != b'\x00' * (476 - 24 - data_size):
            print(binascii.hexlify(data))
        assert data[data_size:-24] == b'\x00' * (476 - 24 - data_size)

        if flags & 0x00000001: # not main flash
            return None
        if flags & 0x00001000: # file container
            pass
        if flags & 0x00002000: # familyID present
            assert fs_bfid_zero != 0
        if flags & 0x00004000: # MD5 checksum present
            pass
        if flags & 0x00008000: # extension tags present
            pass

        return (address, data_size, sequence, total_blocks, fs_bfid_zero, data)

    def close(self):
        if self.f:
            self.f.close()
        self.f = None


def parse(uf2_filename, raw_filename = None):

    print(f"UF2: parsing '{uf2_filename}'")
    if raw_filename:
        print(f"  saving payload as '{raw_filename}'...")

    file_size = 0
    file_hash = hashlib.sha256()
    file_crc32 = binascii.crc32(b'')
    try:
         uf2 = UF2(uf2_filename)
         uf2.open()
         if raw_filename:
             raw = open(raw_filename, "wb")
         seq, last_seq, expected_addy = None, -1, None
         while True:
             b512 = uf2.next()
             addy, size, seq, tot, fsize, data = uf2.parse(b512, seq)
             if expected_addy: assert addy == expected_addy
             assert last_seq + 1 == seq
             if raw_filename:
                 raw.write(data[:size])
             file_size += size
             file_hash.update(data[:size])
             file_crc32 = binascii.crc32(data[:size], file_crc32)
             if seq + 1 == tot:
                 break
             last_seq = seq
             expected_addy = addy + size
             
    except Exception as err:
         traceback.print_exception(err)

    finally:
        uf2.close()
        if raw_filename:
            raw.close()

    end_addy = addy + size
    start_addy = end_addy - file_size
    print(f"  crude validation of {tot} 512 byte sequences")
    print(f"  destined for flash address {hex(start_addy)} to {hex(end_addy)}-1")
    print("  file size: {} bytes, {} {}".format(file_size, hex(file_size),
        ", {} 4K blocks".format(file_size // 4096) if file_size % 4096 == 0 else ""
    ))
    print(f"  crc32: {file_crc32}, {hex(file_crc32)}")
    print(f"  sha256: {file_hash.hexdigest()}")


if __name__ == '__main__':
    uf2_filename = sys.argv[1]
    if len(sys.argv) > 2:
        raw_filename = sys.argv[2]
    else:
        raw_filename = None
    parse(uf2_filename, raw_filename)

