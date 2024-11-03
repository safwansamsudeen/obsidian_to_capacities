"""
Import all non-daily notes through X-Callback-URL
"""

import pyautogui as gui
from collections import namedtuple
from datetime import datetime
import dotenv
import os
import time

PATH = dotenv.get_key('./.env', 'NOTES_PATH')
coord = namedtuple('coord', ['x', 'y'])
def pause(): time.sleep(1)
def type(content): gui.write(content, 0.03)
def enter(): gui.press('enter')
def locate(file, confidence=0.5):
    x, y = gui.locateCenterOnScreen(f'./images/{file}.png', confidence=confidence)
    return coord(x=x/2, y=y/2)

## Open Capacities
gui.hotkey('command') # Initializes
gui.hotkey('command', 'space')
gui.write('capacities')
enter()
pause()

def main():
    for path, folders, files in os.walk(PATH):
        c = 0
        for file in files:
            if not file.endswith('.md'): continue
            c += 1
            gui.hotkey('command', 'p')
            gui.write('Page')
            enter()
            pause()

            type(file[:-3])
            with open(path + '/' + file) as f:
                type_file(f.read())
                print('Imported', file)
            if c == 1: break
        if c == 1: break

def type_file(content):
    lines = content.split('\n')
    lines = add_properties(lines)
    lines = remove_formulae(lines)
    gui.press('enter')
    COMMANDS = {'**': 'b', '_': 'i', '```': '```', '*': 'i'}
    for line in lines[:10]:
        for word in line.split():
            cleant_word = word.strip(' :.,')
            print('b', cleant_word)

            for c, k in COMMANDS.items():
                if cleant_word.startswith(c):
                    gui.hotkey('command', k)
                    break
            typed_word = "".join(c for c in word if c not in '*_')
            if word.startswith('[['):
                type(typed_word[:-2])
                enter()
            else:
                type(typed_word)

            for c, k in COMMANDS.items():
                if cleant_word.endswith(c):
                    gui.hotkey('command', k)
                    break

        enter()

def add_properties(lines):
    if lines[0] != '---': return lines
    property = None
    coords = {
        'tags': locate('tags'),
        'sidebar': locate('sidebar', 0.7)
    }
    first_tag = True
    new_content = ''

    for i, line in enumerate(lines[1:]):
        if line == '---': break
        if line.endswith(':'):
            property = line.strip(' :')
            gui.press('escape')
        elif ':' in line:
            property, line = line.split(':')
            new_content += analyze_properties(property, line, coords, first_tag)
        else:
            new_content += analyze_properties(property, line, coords, first_tag)
            if property == 'tags': first_tag = False

    return new_content.split('\n') + lines[i:]

def remove_formulae(lines):
    return [line for line in lines if not line.startswith('> [!') and line.strip(' >')]

def analyze_properties(property: str, line: str, coords: dict, first_tag: bool):
    line = line.strip(' -"')
    new_content = ""
    # if property == 'tags':
    #     if first_tag:
    #         gui.moveTo(coords["tags"].x, coords["tags"].y + 100)
    #         gui.click()
    #     type(line)
    #     # Note that if two tags share a beginning, this is a bug
    #     enter()
    # elif property == 'created':
    #     gui.moveTo(coords["sidebar"].x, coords["sidebar"].y + 80 , tween=gui.easeInOutQuad, duration=1)
    #     if not "created_at" in coords:
    #         d = gui.locateOnScreen('./images/stats.png', confidence=0.9)
    #         coords["created_at"] = coord((d.left + d.width + 20) /2, (d.top + d.height) / 2 - 10)
    #     gui.moveTo(coords["created_at"].x, coords["created_at"].y)
    #     gui.click()
    #     gui.write(datetime.strptime(line, '%Y-%m-%d').strftime('%Y-%d-%m'))
    #     enter()
    if property in ['up', 'related']:
        new_content += f'*{property.capitalize()}*: {line}'
    return new_content + '\n'

main()
