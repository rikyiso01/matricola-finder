from __future__ import annotations
from yaml import safe_load
from typing import TypedDict


def render_elm(data: list[OutputStudent]):
    array = [
        f'{{name="{student["name"].lower()}", matricola="{student["matricola"]}"}}'
        for student in data
    ]
    return f"""module Data exposing (data)
data=[{','.join(array)}]"""


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


def data():
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
    return students


def main():
    with open("src/Data.elm", "wt") as file:
        file.write(render_elm(data()))


if __name__ == "__main__":
    main()
