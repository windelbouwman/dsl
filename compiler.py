
import argparse
import logging
from bytecode import Bytecode
import textx
from textx.export import model_export

def cname(o):
    return o.__class__.__name__


class CodeGenerator:
    logger = logging.getLogger('compiler')

    def __init__(self, lst_file, output_filename):
        self._var_number = 0
        self._opcodes = []
        self._list_file = lst_file
        self.output_filename = output_filename

    def compile(self, m):
        self._opcodes = []
        self.compile_program(m)
        print(self._opcodes)

        code = Bytecode()
        code._mem_pool_size = self._mem_pool_offset
        code._opcodes = self._opcodes
        with open(self.output_filename, 'wb') as f:
            code.save(f)

    def compile_program(self, m):
        self._mem_pool_offset = 0
        self._var_offsets = {}
        for declaration in m.declarations:
            self.logger.info('declaration: %s', declaration)

            typ = cname(declaration)
            if typ == 'Variable':
                self.compile_variable(declaration)
            elif typ == 'Function':
                self.compile_function(declaration)
            else:
                raise NotImplementedError(typ)

    var_sizes = {
        's8': 1,
        'u8': 1,
        's16': 2,
        'u16': 2,
        's32': 4,
        'u32': 4,
    }

    def compile_variable(self, variable):
        self.logger.info('Variable: %s', variable.name)
        var_size = self.var_sizes[variable.typ]
        offset = self._mem_pool_offset
        self.emit_listing('Placing variable {} at {}'.format(variable.name, offset))
        self._var_offsets[variable.name] = offset
        self._mem_pool_offset += var_size

    def compile_function(self, function):
        self.logger.info('Function: %s', function.name)
        self.emit_listing('Function {}'.format(function.name))

        for statement in function.statements:
            self.compile_statement(statement)

    def compile_statement(self, statement):
        self.logger.info('Statement: %s', statement)
        typ = cname(statement)
        if typ == 'Assignment':
            self.compile_expression(statement.value)
            varname = statement.variable_name
            offset = self._var_offsets[varname]
            print(offset)
            opcode = Bytecode.OP_STORE
            typ = 1
            self.emit(opcode, (offset, typ))
        else:
            raise NotImplementedError(typ)

    def compile_expression(self, expression):
        self.logger.info('Expression: %s', expression)
        typ = cname(expression)
        if typ == 'Expression':
            ops = expression.op
            if len(ops) == 1:
                self.compile_expression(ops[0])
            elif len(ops) == 3:
                self.compile_expression(ops[0])
                self.compile_expression(ops[2])
                opcode = Bytecode.OP_ADD
                typ = 1
                self.emit(opcode, (typ,))
            else:
                error
        elif typ == 'Term':
            self.compile_expression(expression.op[0])
        elif typ == 'VariableRef':
            varname = expression.name
            offset = self._var_offsets[varname]
            print('offset', offset)
            opcode = Bytecode.OP_LOAD
            typ = 1
            self.emit(opcode, (offset, typ))
        elif typ == 'Constant':
            opcode = Bytecode.OP_CONST
            self.emit(opcode, (expression.value,))
        else:
            raise NotImplementedError(typ)

    def emit(self, opcode, operands):
        self.emit_listing(' Opcode: {} {}'.format(opcode, operands))
        self._opcodes.append((opcode, operands))

    def emit_listing(self, txt):
        print(txt, file=self._list_file)
        self.logger.info(txt)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('dsl_file')
    args = parser.parse_args()

    # source_filename = 'example.dsl'
    source_filename = args.dsl_file
    mm = textx.metamodel_from_file('grammar.tx')
    m = mm.model_from_file(source_filename)
    model_export(m, source_filename + '.dot')

    print(m)

    filename = source_filename + '.bin'
    list_filename = source_filename + '.lst'
    with open(list_filename, 'w') as lst_file:
        cgen = CodeGenerator(lst_file, filename)
        cgen.compile(m)


if __name__ == '__main__':
    main()
