#!/usr/bin/env python3
"""
Simple CLI app to generate text patterns based on user input.

Usage:
    python main.py [--type TYPE] [--size SIZE] [--char CHAR]

If arguments are omitted, the program will prompt interactively.
"""

import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='Generate text patterns.')
    parser.add_argument('--type', choices=['triangle', 'pyramid', 'diamond', 'square'], help='Pattern type')
    parser.add_argument('--size', type=int, help='Size of the pattern (number of rows)')
    parser.add_argument('--char', default='*', help='Character to use for the pattern')
    return parser.parse_args()

def prompt_missing_args(args):
    if not args.type:
        args.type = input('Enter pattern type (triangle, pyramid, diamond, square): ').strip()
    if not args.size:
        while True:
            size_input = input('Enter size (positive integer): ').strip()
            if size_input.isdigit() and int(size_input) > 0:
                args.size = int(size_input)
                break
            else:
                print('Invalid size. Please enter a positive integer.')
    if not args.char:
        args.char = input('Enter character to use (default *): ').strip() or '*'

def generate_triangle(size, char):
    for i in range(1, size + 1):
        print(char * i)

def generate_pyramid(size, char):
    for i in range(1, size + 1):
        spaces = ' ' * (size - i)
        stars = char * (2 * i - 1)
        print(f"{spaces}{stars}")

def generate_square(size, char):
    for _ in range(size):
        print(char * size)

def generate_diamond(size, char):
    if size % 2 == 0:
        size += 1
    mid = size // 2
    for i in range(mid + 1):
        spaces = ' ' * (mid - i)
        stars = char * (2 * i + 1)
        print(f"{spaces}{stars}")
    for i in range(mid - 1, -1, -1):
        spaces = ' ' * (mid - i)
        stars = char * (2 * i + 1)
        print(f"{spaces}{stars}")

def main():
    args = parse_args()
    prompt_missing_args(args)
    if args.type == 'triangle':
        generate_triangle(args.size, args.char)
    elif args.type == 'pyramid':
        generate_pyramid(args.size, args.char)
    elif args.type == 'square':
        generate_square(args.size, args.char)
    elif args.type == 'diamond':
        generate_diamond(args.size, args.char)
    else:
        print(f"Unsupported pattern type: {args.type}")
        sys.exit(1)

if __name__ == '__main__':
    main()
