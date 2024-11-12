import time
import pyautogui as gui
from collections import namedtuple


coord = namedtuple('coord', ['x', 'y'])


def stitch_links(words: list[str]) -> list[str]:
    """
    Takes a list of splitted words and stitches together the words that are part of a link.
    """
    results = []
    prev_i = 0
    for i, word in enumerate(words):
        # TOGGLE Handle image links too by adding `.strip('!')`
        if word.strip('*_').startswith('[') and not word.endswith(']'):
            invalid_link, link_opened = False, False
            next_i = i
            while next_i < len(words):
                if "](" in words[next_i]:
                    link_opened = True
                if link_opened and words[next_i].strip('*_').endswith(")"):
                    break
                next_i += 1

            results.extend(words[prev_i:i])
            prev_i = next_i + 1
            results.append(''.join(words[i:prev_i]))
            link_opened = False

    return results + words[prev_i:]


def partition_multi(s, splitters):
    """
    Partitions a string based on multiple splitters.
    """
    prev_i = 0
    res = []
    for i, c in enumerate(s):
        if c in splitters:
            if prev_i != i:
                res.append(s[prev_i:i])
            res.append(c)
            prev_i = i + 1
    res.append(s[prev_i:])
    return res


def pause(seconds: float = 1):
    time.sleep(seconds)


def type(content, should_pause=False):
    gui.keyUp('shift')
    gui.keyUp('fn')
    gui.write(content, 0.02)
    if should_pause:
        pause(0.5)


def enter():
    gui.press('enter')


def locate(file, confidence=0.5):
    x, y = gui.locateCenterOnScreen(
        f'./images/{file}.png', confidence=confidence)
    return coord(x=x/2, y=y/2)


def remove_formulae(lines):
    return [line for line in lines if not line.startswith('> [!') and line.strip(' >')]
