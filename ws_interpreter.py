#!/usr/bin/env python3
"""
Ein minimaler, eigenstaendiger Whitespace-Interpreter.

Aufruf:
    python3 ws_interpreter.py calc.ws
Zahlen fuer 'readnum' werden zeilenweise von stdin gelesen.

Befehlssatz (Standard-Whitespace):
  Stack   [Space]        push, dup, swap, discard, copy, slide
  Arith   [Tab][Space]   add, sub, mul, div, mod
  Heap    [Tab][Tab]     store, retrieve
  Flow    [LF]           label, call, jmp, jz, jn, ret, end
  I/O     [Tab][LF]      outchar, outnum, readchar, readnum
"""
import sys


def parse(src: str):
    src = ''.join(c for c in src if c in ' \t\n')
    i = 0
    n = len(src)
    instrs = []

    def rc():
        nonlocal i
        c = src[i]
        i += 1
        return c

    def read_number():
        sign = rc()
        bits = ''
        while True:
            c = rc()
            if c == '\n':
                break
            bits += '1' if c == '\t' else '0'
        val = int(bits, 2) if bits else 0
        return -val if sign == '\t' else val

    def read_label():
        bits = ''
        while True:
            c = rc()
            if c == '\n':
                break
            bits += '1' if c == '\t' else '0'
        return bits

    while i < n:
        c1 = rc()
        if c1 == ' ':
            c2 = rc()
            if c2 == ' ':
                instrs.append(('push', read_number()))
            elif c2 == '\n':
                c3 = rc()
                instrs.append({' ': ('dup',), '\t': ('swap',), '\n': ('discard',)}[c3])
            elif c2 == '\t':
                c3 = rc()
                if c3 == ' ':
                    instrs.append(('copy', read_number()))
                else:
                    instrs.append(('slide', read_number()))
        elif c1 == '\t':
            c2 = rc()
            if c2 == ' ':
                c3, c4 = rc(), rc()
                instrs.append({(' ', ' '): ('add',), (' ', '\t'): ('sub',), (' ', '\n'): ('mul',),
                                ('\t', ' '): ('div',), ('\t', '\t'): ('mod',)}[(c3, c4)])
            elif c2 == '\t':
                c3 = rc()
                instrs.append(('store',) if c3 == ' ' else ('retrieve',))
            elif c2 == '\n':
                c3, c4 = rc(), rc()
                instrs.append({(' ', ' '): ('outchar',), (' ', '\t'): ('outnum',),
                                ('\t', ' '): ('readchar',), ('\t', '\t'): ('readnum',)}[(c3, c4)])
        elif c1 == '\n':
            c2 = rc()
            if c2 == ' ':
                c3 = rc()
                if c3 == ' ':
                    instrs.append(('label', read_label()))
                elif c3 == '\t':
                    instrs.append(('call', read_label()))
                else:
                    instrs.append(('jmp', read_label()))
            elif c2 == '\t':
                c3 = rc()
                if c3 == ' ':
                    instrs.append(('jz', read_label()))
                elif c3 == '\t':
                    instrs.append(('jn', read_label()))
                else:
                    instrs.append(('ret',))
            elif c2 == '\n':
                rc()  # dritte LF fuer 'end'
                instrs.append(('endprog',))
    return instrs


def run(instrs, input_text: str, out=sys.stdout):
    labels = {ins[1]: idx for idx, ins in enumerate(instrs) if ins[0] == 'label'}
    stack = []
    heap = {}
    callstack = []
    pos = [0]

    def read_number_input():
        s = input_text[pos[0]:]
        j = s.find('\n')
        line, adv = (s, len(s)) if j == -1 else (s[:j], j + 1)
        pos[0] += adv
        try:
            return int(line.strip())
        except ValueError:
            return 0

    def read_char_input():
        if pos[0] >= len(input_text):
            return 0
        c = input_text[pos[0]]
        pos[0] += 1
        return ord(c)

    ip = 0
    while ip < len(instrs):
        op, *arg = instrs[ip]
        a = arg[0] if arg else None
        if op == 'push':
            stack.append(a)
        elif op == 'dup':
            stack.append(stack[-1])
        elif op == 'swap':
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op == 'discard':
            stack.pop()
        elif op == 'copy':
            stack.append(stack[-1 - a])
        elif op == 'slide':
            top = stack.pop()
            del stack[len(stack) - a:]
            stack.append(top)
        elif op in ('add', 'sub', 'mul', 'div', 'mod'):
            b = stack.pop(); x = stack.pop()
            if op == 'add':
                stack.append(x + b)
            elif op == 'sub':
                stack.append(x - b)
            elif op == 'mul':
                stack.append(x * b)
            elif op in ('div', 'mod'):
                if b == 0:
                    raise RuntimeError("Fehler: Division durch Null")
                # Trunkierung gegen Null (C-Logik), nicht Python-Floor,
                # damit z.B. -7 / 3 == -2 und -7 % 3 == -1 ergibt.
                q = abs(x) // abs(b)
                if (x < 0) ^ (b < 0):
                    q = -q
                stack.append(q if op == 'div' else x - q * b)
        elif op == 'store':
            v = stack.pop(); addr = stack.pop(); heap[addr] = v
        elif op == 'retrieve':
            addr = stack.pop(); stack.append(heap.get(addr, 0))
        elif op == 'label':
            pass
        elif op == 'call':
            callstack.append(ip + 1); ip = labels[a]; continue
        elif op == 'jmp':
            ip = labels[a]; continue
        elif op == 'jz':
            v = stack.pop()
            if v == 0:
                ip = labels[a]; continue
        elif op == 'jn':
            v = stack.pop()
            if v < 0:
                ip = labels[a]; continue
        elif op == 'ret':
            ip = callstack.pop(); continue
        elif op == 'endprog':
            break
        elif op == 'outchar':
            out.write(chr(stack.pop()))
        elif op == 'outnum':
            out.write(str(stack.pop()))
        elif op == 'readchar':
            addr = stack.pop(); heap[addr] = read_char_input()
        elif op == 'readnum':
            addr = stack.pop(); heap[addr] = read_number_input()
        ip += 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Aufruf: python3 ws_interpreter.py <datei.ws>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        source = f.read()
    program = parse(source)
    run(program, sys.stdin.read())
