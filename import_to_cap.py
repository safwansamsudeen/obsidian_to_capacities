import os
import pyautogui as gui
import time

def pause(): time.sleep(1)



## Open Capacities
gui.hotkey('command') # Initializes
gui.hotkey('command', 'space')
gui.write('capacities')
gui.press('enter')
pause()

for name in os.listdir('import_data'):
    with open('import_data/' + name) as f:
        if not name.endswith('.md'): continue
        date, _ = name.split('.md')
        x, y = gui.locateCenterOnScreen('/Users/safwan/Downloads/Daily note.png', confidence=0.9)
        gui.moveTo(x, y + 75)
        gui.click()
        for line in f.readlines():
            links = line.split('[[')
            gui.write(links[0])
            for link in links[1:]:
                link = link.split(']]')[0]
                gui.write(link)
                gui.press('enter')
                gui.press('enter')
                gui.write(date)
