# Whitespace Calculator

A fully functional calculator written in the Whitespace esoteric programming language.

This project turns a tiny arithmetic program into real Whitespace source code, then executes it with a custom interpreter. It also includes a simple web interface for running the calculator in a browser.

## What it does

The calculator accepts:

- two integer inputs
- one operator
- and returns the result of the operation

Supported operations:

- `+` (1)
- `-` (2)
- `*` (3)
- `/` (4)
- `%` (5)

It reads the numbers and operation from standard input and prints the computed result.

## Features

- Built in Whitespace, an esoteric language that uses only spaces, tabs, and line breaks
- Includes an assembler to generate Whitespace bytecode from readable instructions
- Includes a standalone interpreter for executing `.ws` files
- Includes a simple web UI to run calculations in the browser
- Handles invalid operators safely

## Repository contents

- `assembler.py` - converts a readable instruction list into Whitespace source
- `calc.ws` - the generated Whitespace calculator program
- `ws_interpreter.py` - interpreter for Whitespace programs
- `web_calc.py` - small local web frontend

## Run the calculator

### 1) Using the interpreter

```bash
python3 ws_interpreter.py calc.ws
```

Then provide input in this order:

```text
10
3
1
```

Where:

- `10` = first number
- `3` = second number
- `1` = operator (`1 = +`, `2 = -`, `3 = *`, `4 = /`, `5 = %`)

Example output:

```text
13
```

### 2) Using the web interface

```bash
python3 web_calc.py
```

Then open:

```text
http://localhost:8000
```

## Notes

This project is primarily an experiment in writing a working calculator in Whitespace and understanding how an esoteric language can still be used to build real functionality.

## License

This project is provided as-is for educational and experimental purposes.
