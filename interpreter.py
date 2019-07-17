
import struct
from bytecode import Bytecode
import argparse


class Vm:
    def __init__(self):
        self._pc = 0
        self._memory = None
        self._stack = []

    def run(self):
        # while True:
        for opcode, operands in self.code._opcodes:
            print('Executing:', opcode)
            if opcode == Bytecode.OP_CONST:
                value = operands[0]
                self._stack.append(value)
            elif opcode == Bytecode.OP_LOAD:
                offset, typ = operands
                value = self._load_mem(offset, typ)
                self._stack.append(value)
            elif opcode == Bytecode.OP_STORE:
                offset, typ = operands
                value = self._stack.pop(-1)
                self._store_mem(offset, typ, value)
            elif opcode == Bytecode.OP_ADD:
                lhs = self._stack.pop(-1)
                rhs = self._stack.pop(-1)
                value = lhs + rhs
                self._stack.append(value)
            else:
                raise NotImplementedError(str(opcode))
        print('Memory at end:', self._memory.hex())

    def _load_mem(self, offset, typ):
        size = 2
        data = self._memory[offset:offset+size]
        value = struct.unpack('h', data)[0]
        return value

    def _store_mem(self, offset, typ, value):
        size = 2
        data = struct.pack('h', value)
        self._memory[offset:offset+size] = data

    def load(self, code):
        self.code = code
        self._memory = bytearray(code._mem_pool_size)


def run(code):
    print(code)
    vm = Vm()
    vm.load(code)
    vm.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=argparse.FileType('rb'))

    args = parser.parse_args()
    print(args)

    code = Bytecode.load(args.filename)
    run(code)


if __name__ == '__main__':
    main()

