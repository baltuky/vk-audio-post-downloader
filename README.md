## vk_apd.py (vk.com audio post content downloader)

```
██╗   ██╗██╗  ██╗ █████╗ ██████╗ ██████╗
██║   ██║██║ ██╔╝██╔══██╗██╔══██╗██╔══██╗
██║   ██║█████╔╝ ███████║██████╔╝██║  ██║
╚██╗ ██╔╝██╔═██╗ ██╔══██║██╔═══╝ ██║  ██║
 ╚████╔╝ ██║  ██╗██║  ██║██║     ██████╔╝
  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═════╝
version: 1.0 | vk.com api version: 5.52
```

## Git

To download the latest version of script from the Git server do this:

    git clone https://github.com/boltuho/vk-audio-post-downloader.git

## Dependencies installation

    $ pip install clint requests

## Usage
```
python vk_apd.py --help

usage: ./vk_apd.py [-h] [-s] -u post_url -o directory

optional arguments:
  -h, --help                         show this help message and exit
  -s, --secured                      download audio from closed group
  -u post_url, --url post_url        audio post url
  -o directory, --output directory   path to output directory

```

## LICENSE

MIT
