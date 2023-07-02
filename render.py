from jinja2 import Environment, FileSystemLoader, select_autoescape
from yaml import safe_load
from typing import TypedDict
from os import makedirs

env = Environment(
    loader=FileSystemLoader(searchpath="src"), autoescape=select_autoescape()
)


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


def main():
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
    template = env.get_template("index.html")
    makedirs(".out", exist_ok=True)
    with open(".out/index.html", "wt") as file:
        file.write(template.render(students=students))


if __name__ == "__main__":
    main()
