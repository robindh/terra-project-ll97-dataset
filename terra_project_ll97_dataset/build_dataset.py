#!/usr/bin/python3

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    args = parser.parse_args()
    if args.verbose:
        print("verbosity turned on")

    print("Ok")


if __name__ == '__main__':
    main()
