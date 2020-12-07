import re
import requests
import shutil
from collections import OrderedDict
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .exceptions import (
    InvalidIDError,
    InvalidURLError,
    NotFetchedError,
    NotFoundError
)


class Thumbnail:

    _id_re = re.compile(r'^[\w-]{11}$')
    _size = OrderedDict([
        (0, 'maxresdefault'),
        (1, 'sddefault'),
        (2, 'hqdefault'),
        (3, 'mqdefault'),
        (4, 'default'),
    ])
    _format = OrderedDict([
        (0, ('vi', 'jpg')),
        (1, ('vi_webp', 'webp'))
    ])

    def __init__(self, url: str = None, id: str = None):
        self._url = url
        self._id = id

        if self._url is None and self._id is None:
            raise ValueError('Must provide video URL or ID')

        self._ext = None
        self.video_id: str = None
        self.image: BytesIO = None

    def fetch(
        self,
        size: int = 0,
        webp: bool = False,
        fallback: bool = True,
        timeout: float = 3.0
    ):
        if self.image:
            return self.image

        if not self.video_id:
            self.video_id = self._parse_id() if self._id else self._parse_url()

        url_template = 'https://i.ytimg.com/{}/{}/{}.{}'
        fmt = self._format[1] if webp else self._format[0]

        for size_id, size_name in self._size.items():
            if size > size_id:
                continue

            url = url_template.format(fmt[0], self.video_id, size_name, fmt[1])
            h = requests.head(url, timeout=timeout)
            if h.ok:
                r = requests.get(url, timeout=timeout)
                if r.ok:
                    self.image = BytesIO(r.content)
                    self._ext = fmt[1]
                    return self.image

            if not fallback:
                break

        raise NotFoundError(
            "Failed to find thumbnail for video ID "
            f"'{self.video_id}' with size '{self._size[size]}'"
        )

    def save(
        self,
        dir: str,
        filename: str = None,
        overwrite: bool = False,
        mkdir: bool = True
    ):
        if self.image is None:
            raise NotFetchedError('Must fetch before saving')

        file = f'{filename}.{self._ext}' if filename else f'{self.video_id}.{self._ext}'
        path = Path(dir)

        if mkdir:
            path.mkdir(parents=True, exist_ok=True)

        dest = path.joinpath(file)
        if dest.exists() and not overwrite:
            raise FileExistsError(dest)

        with open(dest, 'wb') as f:
            shutil.copyfileobj(self.image, f)

    def _parse_url(self):
        base_url = self._url if self._url.startswith(('http://', 'https://')) else 'https://' + self._url

        url = urlsplit(base_url)

        if all(url.netloc != n for n in ('www.youtube.com', 'youtube.com', 'youtu.be')):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL")

        id = ''
        if url.path.startswith('/embed/'):
            id = url.path.split('/')[2][:11]
        elif url.netloc == 'youtu.be':
            id = url.path[1:12]
        else:
            query = parse_qs(url.query)
            if 'v' in query:
                id = query['v'][0][:11]

        if not self._id_re.fullmatch(id):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL")
        return id

    def _parse_id(self):
        if not self._id_re.fullmatch(self._id):
            raise InvalidIDError(f"'{self._id}' is not a valid YouTube video ID")
        return self._id
