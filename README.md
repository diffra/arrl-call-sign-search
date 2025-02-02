# ARRL Ham Radio Call Sign Search Utility

## Intro

`arrl-call-sign-search` is a small utility I wrote to look up ham radio call sign from [ARRL](https://www.arrl.org/advanced-call-sign-search). The utility parses ARRL responses and print call sign details.

## Dependencies

`arrl-call-sign-search` is written in Python3.

Following Python packages are needed:

```
lxml.html
requests
tabulate
```

## Usage

```
$ ./arrl-call-sign-search.py -h
usage: arrl-call-sign-search.py [-h] [--pretty] callsign

Ham Radio Call Sign Search Utility - ARRL

positional arguments:
  callsign    ham radio call sign string

options:
  -h, --help  show this help message and exit
  --pretty    print pretty format
```
