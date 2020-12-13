# PyThumb

![version][shields-version]
![python version][shields-python]
![python wheel][shields-wheel]
![license][shields-license]

Simple command line utility and API for downloading YouTube thumbnails.

Supports JPEG and WebP formats in all sizes.
Previews (animated thumbnails) are not supported due to the lack of direct URL or API access.

Requires Python 3.6+

## Table of contents

- [Installation](#installation)
  - [From source](#from-source)
- [Usage](#usage)
  - [CLI](#cli)
  - [API](#api)
- [License](#license)

## Installation

Install via pip:
```sh
$ pip install pythumb
```

Or get binaries from the [latest release][latest-release].

### From source

###### *Use `python` instead of `python3` on Windows*

Download source code from the [latest release][latest-release], extract and `cd` into it.

(Optional) Create a [virtual environment][virtual-environment] to manage packages easier.

Update pip and setuptools:
```sh
$ python3 -m pip install -U pip setuptools
```

Install this package:
```sh
$ python3 -m pip install .
```

---

Optionally you can build a standalone executable.

Prerequisites:
- [Git Bash][git] (Windows)

On Debian/Ubuntu install python3-dev:
```sh
$ sudo apt install python3-dev
```

Install pyinstaller:
```sh
$ python3 -m pip install pyinstaller
```

Run the build script for your OS:
```sh
$ chmod +x ./scripts/build.sh
$ ./scripts/build.sh <win / linux>
```

You can find the executable in `./pyi-dist/`.

## Usage

### CLI

```sh
$ pythumb [options] <input>
```

To save a thumbnail to the current directory, simply pass the video URL or 11-character ID:
```sh
$ pythumb https://youtu.be/aqz-KE-bpKQ
# or
$ pythumb aqz-KE-bpKQ
```

Use `--help` or go to the [wiki][wiki] for more details.

### API

#### Example

```py
from pythumb import Thumbnail
t = Thumbnail('https://youtu.be/aqz-KE-bpKQ')
t.fetch()
t.save('.')
# ./aqz-KE-bpKQ.jpg
```

Full details about the API in the [wiki][wiki].

## License

MIT license. See [LICENSE][license] for more information. 

[shields-version]: https://img.shields.io/github/v/tag/alexitx/pythumb?color=e65c5c&label=version&style=flat-square
[shields-python]: https://img.shields.io/badge/python-3.6--3.9-2996cc?style=flat-square
[shields-wheel]: https://img.shields.io/pypi/wheel/pythumb?color=7acc29&style=flat-square
[shields-license]: https://img.shields.io/github/license/alexitx/pythumb?color=e67a45&style=flat-square

[latest-release]: https://github.com/alexitx/pythumb/releases
[wiki]: https://github.com/alexitx/pythumb/wiki
[license]: https://github.com/alexitx/pythumb/blob/main/LICENSE
[git]:https://gitforwindows.org
[virtual-environment]: https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux
