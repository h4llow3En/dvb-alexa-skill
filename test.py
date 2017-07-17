#!/usr/bin/env python3

import sys
sys.path.append('./src')

from src.lambda_function import lambda_handler
import json
from os import listdir
from os.path import isfile, join
from argparse import ArgumentParser

verbose=False


def main():
    tests_passed = True
    testpath = 'tests'
    testfiles = [join(testpath, f)
                 for f in listdir(testpath) if isfile(join(testpath, f))]
    for test in testfiles:
        if test.endswith('.md'):
            continue
        print("Testing:", test)
        try:
            request_obj = json.load(open(test))
            response = lambda_handler(request_obj)
            if verbose:
                print(json.dumps(request_obj, indent=4))
            print("OK")
        except Exception as e:
            print("Fail because of", e)
            tests_passed=False
    if not tests_passed:
        raise Exception("Tests did not pass")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', help="Print response output", action="store_true")
    args = parser.parse_args()
    verbose = True if args.verbose else False
    main()
