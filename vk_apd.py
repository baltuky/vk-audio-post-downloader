#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import requests
import json
import os
import webbrowser
import re
from clint.textui import progress, colored, puts
import argparse
import sys

APPLICATION_ID = "4817939"
ACCESS_TOKEN_PATTERN = r"access_token=(?P<access_token>\w*)&expires_in=(?P<expires_in>\d*)&user_id=(?P<user_id>\d*)"
VK_API_PREFIX = r"https://api.vk.com/method/"
VK_API_VERSION = "5.52"
MAX_FILE_NAME_LENGTH = 64
ENCODING = "cp866"
VERSION = 0.1


def print_logo():
    print("")
    puts(colored.green("██╗   ██╗██╗  ██╗ █████╗ ██████╗ ██████╗ "))
    puts(colored.green("██║   ██║██║ ██╔╝██╔══██╗██╔══██╗██╔══██╗"))
    puts(colored.green("██║   ██║█████╔╝ ███████║██████╔╝██║  ██║"))
    puts(colored.green("╚██╗ ██╔╝██╔═██╗ ██╔══██║██╔═══╝ ██║  ██║"))
    puts(colored.green(" ╚████╔╝ ██║  ██╗██║  ██║██║     ██████╔╝"))
    puts(colored.green("  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═════╝ "))
    puts(colored.green("version: %s | vk.com api version: %s" % (VERSION, VK_API_VERSION)))
    print("")


def cut_file_name(name):
    return name[:MAX_FILE_NAME_LENGTH - 3] + "..." if len(name) > MAX_FILE_NAME_LENGTH else name


def get_auth_url():
    return r"https://oauth.vk.com/authorize?client_id=%s&display=page&redirect_uri=" \
           r"https://oauth.vk.com/blank.html&scope=wall,audio&response_type=token&v=5.52" % APPLICATION_ID


def get_post_by_id_url(post_id, auth_data):
    return (VK_API_PREFIX + "wall.getById?posts=%s&extended=1&v=%s&access_token=%s") % (
        post_id, VK_API_VERSION, auth_data["access_token"] if auth_data and auth_data["access_token"] else "")


def download_and_save_to_file(audio_info, file_path, label=""):
    if audio_info[0] == "":
        return False
    if file_path[-1] == r"/":
        file_path = file_path[:-1]
    local_filename = "%s/%s.mp3" % (file_path, audio_info[1])

    print(cut_file_name(audio_info[1].encode(ENCODING, "ignore").decode(ENCODING)))
    response = requests.get(audio_info[0], stream=True)
    with open(local_filename, 'wb') as audio_file:
        total_length = int(response.headers.get('content-length'))
        for chunk in progress.bar(response.iter_content(chunk_size=1024),
                                  label=label, expected_size=(total_length / 1024) + 1):
            if chunk:
                audio_file.write(chunk)
                audio_file.flush()
    return True


def get_auth_data():
    webbrowser.open_new_tab(get_auth_url())
    print("[*] Click \"Accept\" button")
    token_url = raw_input("Copy url from browser window and put it here\n:")
    token_regular_expression = re.compile(ACCESS_TOKEN_PATTERN)
    parsed_token_url = token_regular_expression.search(token_url)
    if parsed_token_url.group("access_token"):
        return {"access_token": parsed_token_url.group("access_token"), "user_id": parsed_token_url.group("user_id"),
                "expires_in": parsed_token_url.group("expires_in")}
    else:
        raise ValueError("Wrong access token.")


def get_post_id(url):
    post_id_regular_expression = re.compile(r"-?\d*_\d*", re.DOTALL)
    url_post_id_re = re.compile(r"(\w*)=([\w-]*)", re.DOTALL)

    result = None
    if post_id_regular_expression.match(url):
        result = url
    elif url_post_id_re.findall(url):
        result = url_post_id_re.findall(url)
        for i in result:
            if i[0] == "w":
                result = post_id_regular_expression.findall(i[1])[0]
        if not result:
            raise ValueError("Wrong audio post url.")
    else:
        raise ValueError("Wrong audio post url.")
    return result


def collect_attachments(post_data, type):
    if not len(post_data["response"]["items"]):
        raise ValueError("No one audio track has been found, check post url and try again")
    item = post_data["response"]["items"][0]
    attachments = item["copy_history"][0]["attachments"] if "copy_history" in item.keys() else item["attachments"]
    return filter(lambda attachment: attachment["type"] == type, attachments)


if __name__ == '__main__':
    try:
        print_logo()
        parser = argparse.ArgumentParser(prog=__file__)
        parser.add_argument("-s", "--secured", action="store_true", help="download audio post from closed group")
        parser.add_argument("-u", "--url", required=True, help="audio post url", metavar="post_url")
        parser.add_argument("-o", "--output", required=True, help="path to output directory", metavar="directory")
        args = parser.parse_args()

        auth_data = get_auth_data() if args.secured else {}
        post_id = get_post_id(args.url)
        response = requests.get(get_post_by_id_url(post_id, auth_data))
        post_data = json.loads(response.text)

        audio_info_list = []
        audio_attachments = collect_attachments(post_data, "audio")

        for attachment in audio_attachments:
            audio_info_list.append(
                [attachment["audio"]["url"], attachment["audio"]["artist"] + " - " + attachment["audio"]["title"]])

        output_directory = args.output
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        failed_downloads_count = 0
        for i in range(len(audio_info_list)):
            if not download_and_save_to_file(audio_info_list[i], output_directory,
                                             "Track %d/%d " % (i + 1, len(audio_info_list))):
                failed_downloads_count += 1
            print("")
        print("[*] Successfully downloaded %d audio track(s), %d with errors" % (
            len(audio_info_list) - failed_downloads_count, failed_downloads_count))
    except ValueError as ex:
        sys.stderr.write("[x] %s\n" % ex.message)
        sys.exit(1)
    except:
        sys.exit(1)
