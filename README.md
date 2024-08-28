# Chunky DL

**Chunky DL** is a user-friendly, ready to roll library for downloading files. It incorporates many common setups and 
patterns for downloading files all with little setup or configuration required.

Chunky DL supports multipart download out of the box.  Simply set your size threshold and any file over that size will 
be downloaded in multiple parts and joined together at the end of download.  No further work is on your end is required.

Chunky DL also supports multithreaded download for downloading multiple files at a time.  Simply supply a list of urls, 
the number of downloads you wish to run simultaneously, and the output path and no further configuration is required.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![GitHub License](https://img.shields.io/github/license/MalloyDelacroix/chunkydl?color=FFC000)

[//]: # (![GitHub Tag]&#40;https://img.shields.io/github/v/tag/MalloyDelacroix/chunkydl?color=FFC000&#41;)

------------

## Installation

ChunkyDL is available on PyPi:


```console
$ python -m pip install chunkydl
```

## Usage
Downloading a single file is easy.  The only requirements are a url and an output directory:
```python
import chunkydl

chunkydl.download('http://example.com/path/to/file.mp4', 'C:/Users/User/Downloads')
```

To download multiple files simultaneously:
```python
import chunkydl

urls = [
    'http://example.com/path/to/file_one.mp4',
    'http://example.com/path/to/file_two.mp4',
    'http://example_site_two.com/path/to/file_three.mp4',
]

chunkydl.download_list(urls, 'C:/Users/User/Downloads')
```

By default, ChunkyDL is configured to download up to 4 files simultaneously and to split files with a size of over 100MB 
into parts and download up to 4 parts simultaneously.  Of course, this can be configured by supplying these values to 
either function above:
```python
import chunkydl

chunkydl.download(
    url='http://example.com/path/to/file.mp4', 
    output_path='C:/Users/User/Downloads',
    size_threshold='50mb',  # 50MB
    multipart_threads=6
)
```

The download configuration object can be accessed directly, allowing you to set up individual download configurations for 
each url in a list.  To do this, define a `DownloadConfig` object with your desired settings and supply the url, 
output path, and configuration for each url that you wish to download:
```python
import chunkydl
from chunkydl import DownloadConfig, DLGroup

dl_list = [
    DLGroup(
        url='http://example.com/path/to/file_one.mp4', 
        output_path='C:/Users/User/Downloads/new_file_one.mp4',
        config=DownloadConfig(size_threshold='200mb', multipart_threads=3)
    ),
    DLGroup(
        url='http://example.com/path/to/file_two.mp4',
        output_path='C:/Users/User/Downloads/new_file_two.mp4',
        config=DownloadConfig(size_threshold='20mb', headers={'Referer': 'http://example.com/'})
    ),
    DLGroup(
        url='http://example_site_two.com/path/to/file_three.mp4',
        output_path='C:/Users/User/Documents/SuperSpecialFolder/',
        config=DownloadConfig()  # use default configuration
    ),
]

chunkydl.download_list(dl_list)
```

## Features

* **Multipart downloads:** Large files are downloaded in multiple parts simultaneously to increase download speed.
* **Multiple concurrent downloads:** Download multiple files simultaneously without having to set up a custom framework.
* **Perpetual download queue:** Queue downloader can be run perpetually in its own thread.  The download queue stays running
    until you are ready for it to stop.  Simply keep adding urls to the queue to keep downloading.
* **Highly configurable:** Downloads can be configured exactly how you need them. You control the thread counts, size thresholds, 
    headers, retries, and more all with simple configuration parameters.