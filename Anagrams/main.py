"""Portable rack solver. Mouse guidance is an explicit, macOS-only opt-in."""
import argparse
import json
import platform
import threading
try:
    from .anagram import normalize_rack, find_anagrams, tile_indices
except ImportError:
    from anagram import normalize_rack, find_anagrams, tile_indices


def create_coords(position, size):
    return [(position[0]+((2*i+1)/12)*size[0], position[1]+.82*size[1]) for i in range(6)]


def plan_word(rack, word, coordinates):
    if len(coordinates) != len(normalize_rack(rack)):
        raise ValueError('One coordinate per rack tile is required')
    return [coordinates[i] for i in tile_indices(rack, word)]


def guide_mouse(rack=None):
    if platform.system() != 'Darwin':
        raise RuntimeError('Mouse guidance requires macOS and iPhone Mirroring. Use the web UI or CLI on this platform.')
    # Optional desktop dependencies are loaded only after explicit opt-in.
    import appscript
    import pyautogui
    from pynput import mouse, keyboard
    from PIL import ImageGrab
    import pytesseract
    app = appscript.app('System Events').application_processes['iPhone Mirroring']
    position, size = app.windows[0].position(), app.windows[0].size()
    if rack is None:
        image = ImageGrab.grab(bbox=(position[0], position[1]+int(size[1]*2/3), position[0]+size[0], position[1]+size[1]))
        raw = pytesseract.image_to_string(image, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        try: rack = normalize_rack(raw)
        except ValueError: rack = normalize_rack(input('OCR could not identify tiles. Enter the six letters: '))
        print('OCR rack:',rack)
        if input('Confirm these six tiles before guidance (yes/no): ').strip().lower() != 'yes': return
    if len(rack) != 6 or '?' in rack:
        raise ValueError('Mouse guidance requires exactly six real letter tiles')
    stop, released = threading.Event(), threading.Event()
    def key_press(key):
        if key == keyboard.Key.esc: stop.set();released.set();return False
    def click(_x,_y,_button,pressed):
        if not pressed: released.set()
    pyautogui.FAILSAFE = True
    print('Guidance only: you click each tile. Esc cancels before the next movement. Move to a screen corner for the PyAutoGUI fail-safe.')
    coords = create_coords(position,size)
    try:
        with keyboard.Listener(on_press=key_press), mouse.Listener(on_click=click):
            for word in find_anagrams(rack):
                if stop.is_set(): break
                print(word)
                targets = plan_word(rack,word,coords)+[(position[0]+size[0]/2,position[1]+size[1]*.6)]
                for target in targets:
                    if stop.is_set(): break
                    released.clear()
                    pyautogui.moveTo(*target,duration=.1)
                    while not stop.is_set() and not released.wait(.1): pass
    except KeyboardInterrupt:
        stop.set()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('letters',nargs='?')
    parser.add_argument('--exact',action='store_true')
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--guide-mouse',action='store_true')
    args=parser.parse_args()
    try:
        if args.guide_mouse:
            guide_mouse(normalize_rack(args.letters) if args.letters else None)
            return
        if not args.letters: parser.error('Enter rack letters, for example: python Anagrams/main.py STREAM')
        words=find_anagrams(args.letters,exact=args.exact)
        print(json.dumps(words) if args.json else '\n'.join(words))
    except (ValueError, RuntimeError, ImportError) as error:
        parser.error(str(error))


if __name__ == '__main__': main()
