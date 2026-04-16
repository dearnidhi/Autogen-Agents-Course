"""
Sample code: Messy, hard-to-maintain functions.
Style reviewer targets: PEP 8, naming, complexity, magic numbers.
"""

import math, os, sys  # Multiple imports on one line (PEP 8 violation)
from datetime import *  # Wildcard import (anti-pattern)

# Magic numbers everywhere, no constants
def calc(x, y, z, t, m):  # Single-letter args, cryptic name
    r = x * y
    if r > 1000:  # Magic number
        r = r * 0.85  # What is 0.85? (Magic number — discount rate?)
    if t == 1:
        r = r + (r * 0.18)  # GST? VAT? Unexplained
    elif t == 2:
        r = r + (r * 0.05)
    if m == True:  # Should be "if m:"
        r = r - 50  # Magic number
    return r  # Returns... what exactly?


# Way too long, does too many things (violates Single Responsibility)
def process(data):
    """Does stuff with data."""  # Useless docstring
    result = []
    temp = []
    count = 0
    total = 0
    avg = 0
    mx = 0
    mn = 999999  # Magic number
    flag = False

    for i in range(len(data)):  # Should use enumerate or direct iteration
        x = data[i]
        if x != None:  # Should be "is not None"
            if x > 0:
                result.append(x)
                total = total + x  # Should be total += x
                count = count + 1
                if x > mx:
                    mx = x
                if x < mn:
                    mn = x
                if x > 100:  # Magic number
                    temp.append(x)
                    flag = True

    if count > 0:
        avg = total / count
    else:
        avg = 0

    # Printing inside a function that should just return data (side effect)
    print("Total items processed:", count)
    print("Sum:", total)
    print("Average:", avg)
    print("Max:", mx)
    print("Min:", mn)
    print("Items over threshold:", len(temp))

    # Returning multiple unrelated things in a tuple
    return result, total, avg, mx, mn, flag, temp


# String concatenation in loop (performance + style issue)
def build_report(items):
    report = ""
    for item in items:
        report = report + str(item) + ", "  # Should use join()
    report = report + "END"
    return report


# Inconsistent naming (some camelCase, some snake_case)
def getData():  # Should be get_data()
    myList = []  # Should be my_list
    myDict = {}  # Should be my_dict
    return myList, myDict


class dataProcessor:  # Should be DataProcessor (PascalCase)
    def __init__(self):
        self.Data = []  # Should be self.data
        self.processedFlag = False  # Should be self.processed_flag

    def Process(self):  # Should be process()
        for i in self.Data:
            pass  # Empty body — why is this here?

    def GetData(self):  # Should be get_data()
        return self.Data


# Redundant comments that just repeat the code
def add_numbers(a, b):
    # Add a and b together
    result = a + b  # Add a and b
    # Return the result
    return result  # Return result


# Nested function doing the same thing multiple times (duplication)
def calculate_stats(numbers):
    total = 0
    for n in numbers:
        total += n
    average = total / len(numbers)

    total2 = 0
    for n in numbers:
        total2 += n
    average2 = total2 / len(numbers)  # Duplicate of above!

    total3 = 0
    count3 = 0
    for n in numbers:
        total3 += n
        count3 += 1
    average3 = total3 / count3  # Yet another duplicate!

    return average, average2, average3  # All the same value!
