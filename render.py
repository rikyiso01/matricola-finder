from yaml import safe_load
from typing import TypedDict
from staticjinja import Site
from subprocess import Popen, check_call
from argparse import ArgumentParser


class InputStudent(TypedDict):
    name: str
    email: str


class OutputStudent(TypedDict):
    name: str
    matricola: str


def parse_student(student: InputStudent) -> OutputStudent | None:
    name = student["name"].title()
    matricola = student["email"].split("@")[0].strip("s")
    if not matricola.isdigit():
        return None
    return {
        "name": name,
        "matricola": matricola,
    }


def index():
    with open("students.yml", "rt") as file:
        data: dict[str, InputStudent] = safe_load(file)
    students: list[OutputStudent] = []
    for student in data.values():
        new_student = parse_student(student)
        if new_student is None:
            continue
        students.append(new_student)
    students = sorted(
        students,
        key=lambda x: x["matricola"],
    )
    return {"students": students}


def main(dev: bool, public_url: str | None):
    site = Site.make_site(
        contexts=[("index.html", index)], searchpath="src", outpath=".rendered"
    )
    if dev:
        site.render()
        with Popen(["pnpm", "exec", "parcel", "serve"]):
            site.render(use_reloader=True)
    else:
        site.render()
        args = ["pnpm", "exec", "parcel", "build"]
        if public_url is not None:
            args.append("--public-url")
            args.append(public_url)
        check_call(args)


def entry():
    parser = ArgumentParser()
    parser.add_argument("--dev", "-d", action="store_true", default=False)
    parser.add_argument("--public-url")
    main(**vars(parser.parse_args()))


if __name__ == "__main__":
    entry()
