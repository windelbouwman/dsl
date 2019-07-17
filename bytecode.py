
import struct

OPCODES = [
    ('OP_LOAD', 1, ('offset', 'typ')),
    ('OP_STORE', 2, ('offset', 'typ')),
    ('OP_CONST', 3, ('s16',)),
    ('OP_ADD', 4, ('ty',)),
]

NUM_OPERANDS = {
    x[1]: len(x[2])
    for x in OPCODES
}

class Bytecode:
    OP_LOAD = 1
    OP_STORE = 2
    OP_ADD = 3
    OP_CONST = 4

    def __init__(self):
        self._mem_pool_size = 0
        self._opcodes = []

    @classmethod
    def load(cls, f):
        f = Reader(f)
        marker = f.read(3)
        if marker != b'DSL':
            raise ByteCodeError("Incorrect filetype, expected DSL marker")

        version = f.read(1)

        # Create bytecode object:
        code = cls()
        code._mem_pool_size = f.read_u16()
        opcode_amount = f.read_u16()
        for _ in range(opcode_amount):
            opcode = f.read_u8()
            num_operands = NUM_OPERANDS[opcode]
            operands = []
            for _ in range(num_operands):
                operand = f.read_s16()
                operands.append(operand)
            code._opcodes.append((opcode, operands))
        return code

    def save(self, f):
        # Header:
        writer = Writer(f)
        writer.write(b'DSL')
        writer.write(bytes([1]))  # version
        writer.write_u16(self._mem_pool_size)
        writer.write_u16(len(self._opcodes))

        for opcode, operands in self._opcodes:
            writer.write_u8(opcode)
            num_operands = NUM_OPERANDS[opcode]
            assert len(operands) == num_operands
            for operand in operands:
                writer.write_s16(operand)


class Writer:
    def __init__(self, f):
        self.f = f

    def write_u8(self, value):
        self.write_fmt('B', value)

    def write_s16(self, value):
        self.write_fmt('h', value)

    def write_u16(self, value):
        self.write_fmt('H', value)

    def write_fmt(self, fmt, value):
        data = struct.pack(fmt, value)
        self.write(data)

    def write(self, data):
        self.f.write(data)


class Reader:
    def __init__(self, f):
        self.f = f

    def read(self, amount):
        data = self.f.read(amount)
        if len(data) != amount:
            pos = self.f.tell()
            raise ByteCodeError('Expected {} bytes at offset {}!'.format(amount, pos))
        return data

    def read_u8(self):
        return self.read_fmt('B')[0]

    def read_s16(self):
        return self.read_fmt('h')[0]

    def read_u16(self):
        return self.read_fmt('H')[0]

    def read_u32(self):
        return self.read_fmt('I')[0]

    def read_fmt(self, fmt):
        size = struct.calcsize(fmt)
        data = self.read(size)
        return struct.unpack(fmt, data)


class ByteCodeError(Exception):
    pass

