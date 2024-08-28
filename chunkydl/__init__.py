"""
Copyright 2024 Kyle Hickey

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from .api import download, download_list
from .models.queue_downloader import QueueDownloader
from .models.download_config import DownloadConfig
from .models.data_models import DLGroup
from .exceptions import RequestFailedException
from .models.size import Size


__all__ = [
    'download',
    'download_list',
    'QueueDownloader',
    'DownloadConfig',
    'RequestFailedException',
    'DLGroup',
    'Size'
]
