# Coverage

## Description

Coverage is a program written in Python to generate both statement and branch coverage report for your python program against your own test suite in your local files. This is similar to coverage library, however we don't use coverage library to generate coverage report but instead using ast, trace, and inspect library to scan through your code line by line and run it agains the test suite like a white-box testing process. *Note: This program doesn't aim to test it against your output to show whether your program is working properly, as it only show how much your input covered all the aspect of your program.

## About

Coverage program is dedicated for educational purpose only. Since this is only a part for university project at USYD - SOFT3202 Software Construction and Design 2 given by the task:
> This component requires the development of a comprehensive tool to analyse a provided test suite for a piece of software. The analysis must cover two key white-box testing metrics: statement coverage and branch coverage. The aim is to assess the efficacy and thoroughness of the test suite in detecting faults and ensuring robustness in the software. - USYD

Only student at USYD can see the [scaffold](https://edstem.org/au/courses/15196/lessons/51934/slides/353592)

There's a different between statement and branch coverage that's the output of this program. That is statement coverage is the percentage of executable statements in the software that are executed by all the test cases in the test suite. Where branch coverage is the percentage of every path for each condition that had been covered through (for example if and while statement had at least 2 branch).

## Goals and Knowledge outcome

During the development of Coverage program I had gain an understanding of
- The different between statment and branch coverage
- Deep understand on how coverage library can be made
- White-box testing using ast, trace, and inspect for internal code testing

## How to use the program

1. Make sure that you had ```coverage.py``` in your working directory (which contains your python program and directory of input files)
2. Run the coverage program against your Python program and test suite. For example:
```
python coverage.py <python_program> <input_file_dir>
```
3. See the output that generated through the terminal. It would looks something like this:
```
Statement Coverage: 100%
Branch Coverage: 100%
```
*Note: The percent number is different from the example because it depends on your test suite.

## Contributor

USYD: https://www.sydney.edu.au/

## Credit

Programmer: Phanuwish Chamnivigaiwech (Best)