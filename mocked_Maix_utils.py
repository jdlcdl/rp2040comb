try:
    class RandomAccessFlash:
        '''
        provides a random access flash_read() method much like Maix.utils.flash_read()
        so that tools written for the k210 can be used on rp2040 w/ fewest changes
        '''
        def __init__(self):
            self.flash = rp2.Flash()
            self.block_size = self.flash.ioctl(5, 0)

        def flash_read(self, address, length):
            answer = b''
            blocknum = address // self.block_size
            start = address % self.block_size
            while len(answer) < length:
                needed = length - len(answer)
                buf = bytearray(self.block_size)
                self.flash.readblocks(blocknum, buf)
                if start + needed > self.block_size:
                    end = self.block_size
                else:
                    end = start + needed
                answer += buf[start:end]
                blocknum += 1
                start = 0

            return answer
    utils = RandomAccessFlash()
except:
    class MockedMaixUtils:
        def flash_read(self, address, length):
             with open('/tmp/rp2040.flash_dump', 'rb') as f:
              f.seek(address)
              return f.read(length)
    utils = MockedMaixUtils()
