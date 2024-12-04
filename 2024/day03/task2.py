#!/usr/bin/env python3
#
# This is getting out of hand. Now there's three of them!
#
# Along with mul(X,Y), we also need to support do() and don't().
#
# don't() disables mul(X,Y) instructions, while do() re-enables them.
#
# This simple change adds some complexity. Now:
#
# 1. We need to track additional state (whether a mul(X,Y) can be executed).
#    This is the easy part.
#
# 2. We need to handle instructions that have different argument expectations.
#    Honestly I'm surprisesd they didn't throw another variant other than
#    "no arguments" at us for this.
#
# 3. Corruption means a seamingly-correct-at-first-but-nope-not-really
#    instruction could be hiding an actually-correct instruction within it.
#
# Since we're going to probably be developing some form of CPU eventually,
# let's start thinking about how we'll do this now. I'm going to be introducing
# a container object for the state we care about, and a simple class hierarchy
# for instructions.
#
# Each instruction defines its name, a regex for arguments, and a function to
# execute.
#
# We still use regexes to find instructions, but we don't define the whole
# grammar at once. Instead, we're looking for the beginning of the
# instructions (e.g., "instruction("), looking ahead for the ")" ending the
# call, and then checking if the instruction can parse the argument contents.
#
# If so, good.
#
# If not, we move on from the end of that opening "instruction(", looking for
# the next.

import re


class State:
    mul_enabled: bool = True
    answer: int = 0


class BaseInstruction:
    name: str = ''
    args_re: re.Pattern = re.compile(r'^$')

    @classmethod
    def execute(
        cls,
        state: State,
        m: re.Match,
    ) -> None:
        raise NotImplementedError


class DoInstruction(BaseInstruction):
    name = 'do'

    @classmethod
    def execute(
        cls,
        state: State,
        m: re.Match,
    ) -> None:
        state.mul_enabled = True


class DontInstruction(BaseInstruction):
    name = "don't"

    @classmethod
    def execute(
        cls,
        state: State,
        m: re.Match,
    ) -> None:
        state.mul_enabled = False


class MulInstruction(BaseInstruction):
    name = 'mul'
    args_re = re.compile(r'^(\d{1,3}),(\d{1,3})$')

    @classmethod
    def execute(
        cls,
        state: State,
        m: re.Match,
    ) -> None:
        if state.mul_enabled:
            state.answer += int(m.group(1)) * int(m.group(2))


# A mapping of all instruction names to the implementation classes.
INSTRUCTIONS = {
    instruction.name: instruction
    for instruction in (
        DoInstruction,
        DontInstruction,
        MulInstruction,
    )
}


# A regex matching the beginning of a supported instruction call.
INSTRUCTION_RE = re.compile(r'(?P<name>%s)\('
                            % '|'.join(INSTRUCTIONS.keys()))


def safely_run_instructions(
    filename: str,
) -> int:
    state = State()

    with open(filename, 'r') as fp:
        for line in fp:
            ip: int = 0
            line_len = len(line)

            while ip < line_len:
                m = INSTRUCTION_RE.search(line, ip)

                if not m:
                    # We're done with the line.
                    break

                instruction = INSTRUCTIONS[m.group('name')]

                # Find out the range of the arguments list, if any.
                i1 = m.end()
                i2 = line.find(')', i1)

                if i2 == -1:
                    # We're done with the line.
                    break

                # Attempt to parse the arguments.
                args_m = instruction.args_re.match(line[i1:i2])

                if not args_m:
                    # This is an invalid instruction. searching after the
                    # end of this current instruction name + (.
                    ip = i1
                    continue

                # Execute the instruction and advance our instruction pointer.
                instruction.execute(state, args_m)
                ip = i2 + 1

    return state.answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = safely_run_instructions('sample-input2')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = safely_run_instructions('input')
    print(f'Task answer: {answer}')
