"""
Mini-Assembler fuer die Sprache Whitespace.
Wandelt eine lesbare Mnemonic-Liste in echten Whitespace-Quellcode um
(nur die drei Zeichen Space ' ', Tab '\t', Newline '\n' sind relevant).
"""

IMP_STACK = ' '
IMP_ARITH = '\t '
IMP_HEAP  = '\t\t'
IMP_FLOW  = '\n'
IMP_IO    = '\t\n'


def encode_number(n: int) -> str:
    """Vorzeichen (Space=positiv, Tab=negativ) + Binaerziffern (Space=0, Tab=1) + Newline."""
    sign = ' ' if n >= 0 else '\t'
    n = abs(n)
    bits = bin(n)[2:]  # z.B. 0 -> '0', 5 -> '101'
    body = ''.join('\t' if b == '1' else ' ' for b in bits)
    return sign + body + '\n'


def encode_label(idx: int) -> str:
    """Label als eindeutige Bitfolge (Space=0, Tab=1) + Newline, ohne Vorzeichen."""
    bits = bin(idx)[2:] if idx > 0 else '0'
    body = ''.join('\t' if b == '1' else ' ' for b in bits)
    return body + '\n'


def assemble(program):
    label_ids = {}

    def lid(name):
        if name not in label_ids:
            label_ids[name] = len(label_ids)
        return label_ids[name]

    out = []
    for instr in program:
        op = instr[0]
        if op == 'push':
            out.append(IMP_STACK + ' ' + encode_number(instr[1]))
        elif op == 'dup':
            out.append(IMP_STACK + '\n ')
        elif op == 'swap':
            out.append(IMP_STACK + '\n\t')
        elif op == 'discard':
            out.append(IMP_STACK + '\n\n')
        elif op == 'copy':
            out.append(IMP_STACK + '\t ' + encode_number(instr[1]))
        elif op == 'slide':
            out.append(IMP_STACK + '\t\n' + encode_number(instr[1]))
        elif op == 'add':
            out.append(IMP_ARITH + '  ')
        elif op == 'sub':
            out.append(IMP_ARITH + ' \t')
        elif op == 'mul':
            out.append(IMP_ARITH + ' \n')
        elif op == 'div':
            out.append(IMP_ARITH + '\t ')
        elif op == 'mod':
            out.append(IMP_ARITH + '\t\t')
        elif op == 'store':
            out.append(IMP_HEAP + ' ')
        elif op == 'retrieve':
            out.append(IMP_HEAP + '\t')
        elif op == 'label':
            out.append(IMP_FLOW + '  ' + encode_label(lid(instr[1])))
        elif op == 'call':
            out.append(IMP_FLOW + ' \t' + encode_label(lid(instr[1])))
        elif op == 'jmp':
            out.append(IMP_FLOW + ' \n' + encode_label(lid(instr[1])))
        elif op == 'jz':
            out.append(IMP_FLOW + '\t ' + encode_label(lid(instr[1])))
        elif op == 'jn':
            out.append(IMP_FLOW + '\t\t' + encode_label(lid(instr[1])))
        elif op == 'ret':
            out.append(IMP_FLOW + '\t\n')
        elif op == 'end':
            out.append(IMP_FLOW + '\n\n')
        elif op == 'outchar':
            out.append(IMP_IO + '  ')
        elif op == 'outnum':
            out.append(IMP_IO + ' \t')
        elif op == 'readchar':
            out.append(IMP_IO + '\t ')
        elif op == 'readnum':
            out.append(IMP_IO + '\t\t')
        else:
            raise ValueError(f"Unbekannter Befehl: {op}")
    return ''.join(out)


# ---------------------------------------------------------------------------
# Der eigentliche Taschenrechner (in lesbarer Whitespace-"Assembler"-Notation)
# ---------------------------------------------------------------------------
# Ablauf:
#   1. liest Zahl A von stdin -> heap[0]
#   2. liest Zahl B von stdin -> heap[1]
#   3. liest Operationscode  -> heap[2]   (1=+, 2=-, 3=*, 4=/, 5=%)
#   4. rechnet A op B und gibt das Ergebnis + Zeilenumbruch aus
CALCULATOR_PROGRAM = [
    ('push', 0), ('readnum',),   # A -> heap[0]
    ('push', 1), ('readnum',),   # B -> heap[1]
    ('push', 2), ('readnum',),   # op -> heap[2]

    ('push', 2), ('retrieve',),  # Op-Code auf den Stack

    ('dup',), ('push', 1), ('sub',), ('jz', 'do_add'),
    ('dup',), ('push', 2), ('sub',), ('jz', 'do_sub'),
    ('dup',), ('push', 3), ('sub',), ('jz', 'do_mul'),
    ('dup',), ('push', 4), ('sub',), ('jz', 'do_div'),
    ('dup',), ('push', 5), ('sub',), ('jz', 'do_mod'),

    # ungueltiger Op-Code -> Ergebnis -1
    ('discard',), ('push', -1), ('jmp', 'print_result'),

    ('label', 'do_add'), ('discard',),
    ('push', 0), ('retrieve',), ('push', 1), ('retrieve',),
    ('add',), ('jmp', 'print_result'),

    ('label', 'do_sub'), ('discard',),
    ('push', 0), ('retrieve',), ('push', 1), ('retrieve',),
    ('sub',), ('jmp', 'print_result'),

    ('label', 'do_mul'), ('discard',),
    ('push', 0), ('retrieve',), ('push', 1), ('retrieve',),
    ('mul',), ('jmp', 'print_result'),

    ('label', 'do_div'), ('discard',),
    ('push', 0), ('retrieve',), ('push', 1), ('retrieve',),
    ('dup',), ('jz', 'div_zero'),
    ('div',), ('jmp', 'print_result'),

    ('label', 'do_mod'), ('discard',),
    ('push', 0), ('retrieve',), ('push', 1), ('retrieve',),
    ('dup',), ('jz', 'div_zero'),
    ('mod',), ('jmp', 'print_result'),

    ('label', 'div_zero'), ('discard',), ('discard',),
    ('push', 0), ('jmp', 'print_result'),

    ('label', 'print_result'),
    ('outnum',),
    ('push', 10), ('outchar',),   # Zeilenumbruch ausgeben
    ('end',),
]


if __name__ == '__main__':
    from pathlib import Path
    out_path = Path(__file__).resolve().parent / 'calc.ws'
    src = assemble(CALCULATOR_PROGRAM)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)
    print(f"calc.ws geschrieben: {len(src)} Zeichen "
          f"({src.count(' ')} Space, {src.count(chr(9))} Tab, {src.count(chr(10))} Newline)")
