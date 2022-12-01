#!/usr/bin/env python3

"""Generate md event file."""

import os
import sys
from datetime import datetime as dt
from typing import Dict, List

EVENTS = ["Outdated packages", "Updated app version"]
IMAGES = ["redis", "postgres", "mysql", "kafka"]
STEPS = [
    "request build",
    "upload to registry",
    "unit test",
    "docker tag",
    "aws *ubuntu* tag",
    "aws *lts* tag",
]
TAGS = ["20.04", "22.04"]


def _file_name(suffix: str) -> str:
    today = dt.now()
    return f"{today.year}-{today.month:02}-{today.day:02}{suffix}"


def _select_stuff(stuff) -> List:
    for i, s in enumerate(stuff):
        print(f"{i+1}) {s}")
    print("Enter numbers separated by commas:", end=" ")
    selection = input()
    selection_list = selection.split(",")
    selection_index = [int(i) for i in selection_list]
    return [stuff[i - 1] for i in selection_index]


def _select_events() -> List:
    print("\nSelect events to use:")
    return _select_stuff(EVENTS)


def _select_images() -> List:
    print("Select images to use:")
    return _select_stuff(IMAGES)


def _select_tags() -> List:
    return _select_stuff(TAGS)


def _test_commands(tags_per_image: Dict) -> str:
    """Generate test commands for affected images."""
    command_str = (
        "#!/bin/bash\n"
        "\nset -Eeuo pipefail\n"
        'TEST_PATH="/home/paulo/repo/rocks/server-test-scripts/oci-unit-tests"\n'
        "cd ${TEST_PATH}\n"
    )

    for image, tag_list in tags_per_image.items():
        for tag in tag_list:
            if image == "mysql":
                version = "8.0"
            if image == "redis":
                version = "5.0" if tag == "20.04" else "6.0"
            if image == "postgres":
                version = "12" if tag == "20.04" else "14"
            if image == "kafka":
                version = "3.1"

            command_str = (
                command_str + f"DOCKER_IMAGE='docker.io/ubuntu/{image}:{version}-{tag}_edge'"
                f" sh {image}_test.sh\n"
            )
    return command_str


def _tag_commands(images: List) -> str:
    command_str = "#!/bin/bash\n" "\nset -Eeuo pipefail\n"

    for registry in ["aws-ubuntu", "aws-lts", "docker"]:
        if registry.__contains__("lts"):
            images_select = [image for image in images if image not in ["redis", "kafka"]]
        else:
            images_select = images

        if registry == "aws-ubuntu":
            command_str = (
                command_str + "/home/paulo/repo/rocks/utils/tag-images.sh"
                f" -f -d -n ubuntu -r aws -- {' '.join(images_select)}\n"
            )
        if registry == "aws-lts" and len(images_select) > 0:
            command_str = (
                command_str + "/home/paulo/repo/rocks/utils/tag-images.sh"
                f" -f -d -n lts -r aws -- {' '.join(images_select)}\n"
            )
        if registry == "docker":
            command_str = (
                command_str + "/home/paulo/repo/rocks/utils/tag-images.sh"
                f" -f -d -n ubuntu -r docker -- {' '.join(images_select)}\n"
            )

    return command_str


def main():
    """Generate md event file."""
    images = _select_images()
    events = _select_events()
    tags_per_image = {}
    with open(_file_name(".md"), "w") as out_file:
        out_file.write("# Event\n")
        for event in events:
            out_file.write(f"{event}\n")
        out_file.write("\n")

        for image in images:
            print(f"\nAffected tags for {image}")
            tags = _select_tags()

            tags_per_image[image] = tags

            out_file.write(f"\n## {image}\n")
            for step in STEPS:
                if image == "redis" and step == "aws lts tag":
                    continue
                out_file.write(f"### {step}\n")
                for tag in tags:
                    out_file.write(f"- [ ] {tag}\n")
                out_file.write("\n")
        out_file.write("\n**[ ] REPLY SEC EMAIL!**\n")

    test_file_name = _file_name("_tests.sh")
    with open(test_file_name, "w") as test_file:
        test_file.write(_test_commands(tags_per_image))
    os.chmod(test_file_name, mode=0o755)

    tag_file_name = _file_name("_tags.sh")
    with open(tag_file_name, "w") as test_file:
        test_file.write(_tag_commands(images))
    os.chmod(tag_file_name, mode=0o755)


if __name__ == "__main__":
    main()
    print("Done!")
    input("Press Enter to exit...")
    sys.exit(0)
