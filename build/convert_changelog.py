import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser(description="Script for converting changelog in keepchangelog format into debian changelog")
parser.add_argument('-v', '--version', required=True, help='Target version in X.X.X format')
parser.add_argument('-a', '--author-name', required=True, help='Author\'s name')
parser.add_argument('-e', '--author-email', required=True, help='Author\'s email')
parser.add_argument('-d', '--distribution', default='trusty', help='Debian distribution (default %(default)s)')
parser.add_argument('--dry-run', action='store_true', help='Print only list of commands')
parser.add_argument('changelog', help='Path to CHANGELOG.md file')

if __name__ == "__main__":
    args = parser.parse_args()
    os.environ['DEBFULLNAME'] = args.author_name
    os.environ['DEBEMAIL'] = args.author_email

    version = args.version.split('.', 1)[1]
    changelog = []

    with open(args.changelog) as fh:
        in_version = False
        section = None
        for line in fh:
            if line.strip() == '':
                continue
            if line.startswith('## '):
                if in_version:
                    break
                if f'[{version}]' in line:
                    in_version = True
            elif line.startswith('### '):
                section = line[4:].strip()
            elif line.startswith('* ') and in_version:
                if section is None:
                    print('Section is not recognized. Seems like a wrong file structure.', file=sys.stderr)
                    sys.exit(1)
                changelog.append(f'{section}: {line[2:].strip()}')

    # Process replacements
    changelog = map(lambda x: x.replace('`', ''), changelog)
    changelog = list(changelog)

    if len(changelog) == 0:
        print('Changelog seems to be empty! Please confirm manually and re-run this script', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        subprocess.run = lambda cmd, *args, **kwargs: print(cmd)

    first_entry = True
    for line in changelog:
        if first_entry:
            subprocess.run(['dch', '--newversion', version, '--distribution', args.distribution, line], check=True)
            first_entry = False
        else:
            subprocess.run(['dch', '--append', line], check=True)
