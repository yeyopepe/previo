"""Computes the text part (slug) of a new feature's filename -- the final
filename is '{number}-{slug}.md'; the number (see next-feature-number.py)
guarantees no collision, this slug doesn't need to check anything itself.

Usage:
    python slugify.py "Feature name"
"""
import argparse

from _slug import slugify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    args = parser.parse_args()

    print(slugify(args.title) or "feature")


if __name__ == "__main__":
    main()
