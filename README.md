![BagOnKey Logo](assets/icon.png)
# BagOnKey

BagOnKey is a Python application that allows users to create and manage custom keyboard shortcuts and profiles while providing a graphical user interface for easy interaction. This software has been designed to be used with those cheap USB/Bluetooth keypads that have a set of programmable keys and knobs. 

## Features

- Drag-and-drop support for assigning shortcuts
- Create and manage multiple profiles
- Assign custom shortcuts to keys and knobs
- Switch profiles based on the foreground process
- System tray integration for quick access
- Popup notifications for profile changes
- More features to come!

## Installation

Download the latest release from the [Releases](https://github.com/Tizzu/BagOnKey/releases) page, unzip it and run it, that's it!
Updating from a previous version? Look for the "update" version, which will be safe to overwrite on the previous one.

### Notices

In order to use the application, you need to be able to bind the keypad keys to F13-F24 keys (depending on how many keys you have) and alt+shift+1 to alt+shift+6 for the knobs. This can be done using the software that comes with the keypad, or using tools like [Kriomant's ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool).

The application currently can show two layouts:
- 3 keys, 1 knob
- 12 keys, 2 knobs

If you have less keys or knobs, you can still use the application using the 12 keys, 2 knobs layout, for now keep track of the keys you are using and ignore the rest. Future plans will try to support custom/different layouts.

### Settings

Settings are saved automatically and can be found in the `settings` module.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. I keep track of the backlog in this [Notion page](https://tizzu.notion.site/bagonkey-roadmap?v=1467bdd4065080c3b8f2000c6340f844). You want to suggest a feature? Open an issue and we can discuss it!

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

This project uses the following libraries:
- Keyboard - Copyright (c) 2016 BoppreH (under MIT License)
- logging, threading, time, sys, os - Python Software Foundation License (PSF)
- psutil - Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola (under BSD-3-Clause License)
- PySide6 - Copyright (c) The Qt Company Ltd (under LGPL-3.0 License)
