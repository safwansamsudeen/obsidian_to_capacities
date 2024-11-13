"""
Import all non-daily notes through X-Callback-URL
"""
import os
import re
from datetime import datetime
import logging

import pyautogui as gui
import dotenv

from helpers import *

NOTES_PATH = dotenv.get_key('./.env', 'NOTES_PATH')
VAULT_PATH = dotenv.get_key('./.env', 'VAULT_PATH')
LINK_PATTERN = r"\[([^\]]+)\]\(([^)]+)\)"
COMMANDS = {'**': 'b', '_': 'i', '*': 'i', '~~': ['shift', 's']}

IGNORED_PATTERNS = {'```dataview': '```',
                    '``` dataview': '```', '> [!Multicolumn]': ''}
REPLACEMENTS = {
    '> '
}
already_created = []

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.txt', filemode='w',
                    format='%(asctime)s (levelname)s:%(message)s', level=logging.INFO)


def main():
    logger.info('Starting importer')
    # Open Capacities
    gui.hotkey('command')  # Initializes
    gui.hotkey('command', 'space')
    gui.write('capacities')
    enter()
    pause()

    logger.info('Capacities opened')
    with open(f'{VAULT_PATH}Efforts/Notes/College 2024/Application Tracking/US College Applications.md') as f:
        gui.hotkey('command', 'p')
        gui.write('Page')
        enter()
        pause()
        f_name = f.name.split('/')[-1][:-3]
        type(f_name)
        already_created.append("Atlas/Maps/Idea Development.md")
        type_file(f.read(), f_name)


def type_file(content, name):
    lines = content.split('\n')
    lines = add_properties(lines)
    lines = remove_formulae(lines)
    gui.press('enter')
    flag_ignored = None
    flag_in_list = False
    list_indent = 0

    logger.info(f'File starting: {name}')

    for line in lines:
        # Handle ignored lines
        for ignored in IGNORED_PATTERNS:
            if ignored in line:
                flag_ignored = ignored
                break
        if flag_ignored:
            if not flag_ignored in line and IGNORED_PATTERNS[flag_ignored] in line:
                flag_ignored = None
            continue

        # Handle quotations
        if line.startswith('>'):
            type('| ', True)
            line = line[1:]

        # Handle lists
        if flag_in_list:
            this_line_indent = count_at_beginning(line, '\t')
            if this_line_indent != list_indent:
                gui.hotkey('shift', 'tab')
            if not line.strip().startswith('- '):
                flag_in_list = False
                for _ in range(list_indent + 1): gui.hotkey('shift', 'tab')
            else:
                line = line.replace('- ', '', 1)
                list_indent = count_at_beginning(line, '\t')
        if line.strip().startswith('- '):
            flag_in_list = True

        SPLITTERS = " -.;:.,"
        words = stitch_links(partition_multi(line, SPLITTERS))

        for word in words:
            if word in SPLITTERS:
                type(word)
                continue

            # Trigger formatting hotkey
            for c, k in COMMANDS.items():
                if word.startswith(c):
                    gui.hotkey('command', k) if isinstance(k, str) else gui.hotkey('command', *k)
                    pause(0.1)
                    break

            # Write out links, and excise them from word
            if m := re.search(LINK_PATTERN, word):
                start, end = m.span()
                word = word[:start] + word[end:]
                manage_links(m, name)

            if (bland := word.strip('*_~')):
                type(bland)

            # Untrigger it
            for c, k in COMMANDS.items():
                if word.endswith(c):
                    gui.hotkey('command', k) if isinstance(k, str) else gui.hotkey('command', *k)
                    pause(0.1)
                    break

            # Handle tags
            if word.startswith('#'):
                enter()

        enter()


def manage_links(match, document_name):
    text, link = match.groups()


    # Weblinks and file links
    if link.startswith('http:/') or link.startswith('https:/'):
        type(text)
        with gui.hold('shift'):
            gui.press('left', presses=len(text))
        gui.hotkey('command', 'k')
        gui.keyUp('fn')
        type(link)
        enter()
    else:
        link = link.replace('%20', ' ')
        file_name = link.split('/')[-1]

        # Manage files without extensions
        if file_name.endswith('.md'):
            file_name = file_name[:-3]

        if file_name == document_name:
            gui.hotkey('command', 'i')
            type('self')
            gui.hotkey('command', 'i')
        elif link not in already_created:
            type('+Page')
            try:
                enter()
                type(file_name)
                with open(VAULT_PATH + link) as f:
                    content = f.read()
                    already_created.append(link)
                    type_file(content, file_name)
                    logger.info(f'File created: {file_name}')
            except FileNotFoundError:
                logger.info(f'Uncreated file: {file_name}, at {VAULT_PATH + link}')
                analyze_property('tags', '- "#uncreated"',
                                 {'tags': locate('tags')}, True)

            gui.press('escape')
            gui.hotkey('command', '[')
            enter()
        else:
            type('[[')
            type(file_name)
            enter()


def add_properties(lines):
    if lines[0] != '---':
        return lines
    property = ""
    coords = {
        'tags': locate('tags'),
        'sidebar': locate('sidebar', 0.7)
    }
    first_tag = True
    new_content = ''

    for i, line in enumerate(lines[1:]):
        if line == '---':
            break
        if line.endswith(':'):
            property = line.strip(' :')
            gui.press('escape')
        elif ':' in line:
            property, line = line.split(':')
            new_content += analyze_property(property,
                                            line, coords, first_tag)
        else:
            new_content += analyze_property(property,
                                            line, coords, first_tag)
            if property == 'tags':
                first_tag = False

    return new_content.split('\n') + lines[i+1:]


def analyze_property(property: str, line: str, coords: dict, first_tag: bool = True):
    line = line.strip(' -"')
    new_content = ""
    if property == 'tags':
        if first_tag:
            gui.moveTo(coords["tags"].x, coords["tags"].y + 90)
            gui.click()
        type(line[1:])
        # Note that if two tags share a beginning, this is a bug
        enter()
    elif property == 'created':
        try:
            if not "created_at" in coords:
                d = gui.locateOnScreen('./images/created.png', confidence=0.7)
                coords["created_at"] = coord(
                    (d.left + d.width) / 2 + 80, (d.top + d.height) / 2 - 10)

            gui.moveTo(coords["sidebar"].x, coords["sidebar"].y +
                       80, tween=gui.easeInOutQuad, duration=1)

            gui.moveTo(coords["created_at"].x, coords["created_at"].y)
            gui.click()
            gui.write(datetime.strptime(line, '%Y-%m-%d').strftime('%Y-%d-%m'))
            enter()
        except gui.ImageNotFoundException:
            logger.error(f'Property {property} not added')

    if property in ['up', 'related']:
        new_content += f'*{property.capitalize()}*: {line}'
    return new_content + '\n'


if __name__ == '__main__':
    main()
