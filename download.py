from httpx import Client, TransportError
from bs4 import BeautifulSoup, Tag
from os import environ
from typing import TypedDict
from time import sleep
from random import randint
from yaml import safe_dump, safe_load
from os.path import exists
from datetime import timedelta
from traceback import print_exc

SAML_LOGIN_URL = "https://unigepass.unige.it/idp/module.php/core/loginuserpass.php"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"


class Student(TypedDict):
    name: str
    email: str


def get_form(page: str) -> tuple[str, dict[str, str]]:
    soup = BeautifulSoup(page, features="html.parser")
    form_tag: Tag
    (form_tag,) = soup("form")
    url = form_tag["action"]
    assert isinstance(url, str)
    input_tags: list[Tag]
    input_tags = soup("input")
    data: dict[str, str] = {}
    for input_tag in input_tags:
        if input_tag.has_attr("name") and input_tag.has_attr("value"):
            key = input_tag["name"]
            value = input_tag["value"]
            assert isinstance(key, str)
            assert isinstance(value, str)
            data[key] = value
    return url, data


def unigepass_login(url: str, username: str, password: str) -> Client:
    client = Client(headers={"User-Agent": USER_AGENT})
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    _, data = get_form(response.text)
    auth_state = data["AuthState"]
    response = client.post(
        SAML_LOGIN_URL,
        data={
            "username": username,
            "password": password,
            "RelayState": "",
            "AuthState": auth_state,
        },
    )
    response.raise_for_status()
    url, data = get_form(response.text)
    response = client.post(url, data=data, follow_redirects=True)
    response.raise_for_status()
    return client


AULAWEB_LOGIN = "https://2022.aulaweb.unige.it/login/index.php"

STUDENTS_PAGE = "https://2022.aulaweb.unige.it/user/index.php?id=6138"
AJAX_URL = "https://2022.aulaweb.unige.it/lib/ajax/service.php?sesskey={}&info=core_table_get_dynamic_table_content"
STUDENTS_AJAX_DATA = '[{"index":0,"methodname":"core_table_get_dynamic_table_content","args":{"component":"core_user","handler":"participants","uniqueid":"user-index-participants-6138","sortdata":[{"sortby":"lastname","sortorder":4}],"jointype":2,"filters":{"courseid":{"name":"courseid","jointype":1,"values":[6138]}},"firstinitial":"","lastinitial":"","pagenumber":"1","pagesize":"5000","hiddencolumns":[],"resetpreferences":false}}]'

FILE = "students.yml"
MIN_SLEEP = 1
MAX_SLEEP = 10


def get_students(client: Client, sesskey: str) -> list[str]:
    response = client.post(AJAX_URL.format(sesskey), content=STUDENTS_AJAX_DATA)
    response.raise_for_status()
    json = response.json()
    assert not json[0]["error"]
    html = json[0]["data"]["html"]
    soup = BeautifulSoup(html, features="html.parser")
    tbody: Tag
    (tbody,) = soup("tbody")
    row: Tag
    result: list[str] = []
    for row in tbody("tr"):
        classes = row["class"]
        assert isinstance(classes, list)
        if "emptyrow" in row["class"]:
            continue
        a: Tag
        (a,) = row("a")
        href = a["href"]
        assert isinstance(href, str)
        result.append(href)
    return result


def get_sesskey(page: str) -> str:
    soup = BeautifulSoup(page, features="html.parser")
    sesskey_tag: Tag
    (sesskey_tag,) = soup("input", {"name": "sesskey"})
    sesskey = sesskey_tag["value"]
    assert isinstance(sesskey, str)
    return sesskey


def get_student_info(client: Client, student_link: str) -> Student | None:
    while True:
        try:
            response = client.get(student_link)
            break
        except TransportError:
            print_exc()
            sleep(20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, features="html.parser")
    name: Tag
    (name,) = soup("h2")
    dts: list[Tag] = soup("dt", string="Indirizzo email")
    if not dts:
        return None
    (dt,) = dts
    a: Tag
    parent = dt.parent
    assert parent is not None
    (a,) = parent("a")
    return {"email": a.text, "name": name.text}


def main():
    client = unigepass_login(
        AULAWEB_LOGIN, environ["UNIGEPASS_USERNAME"], environ["UNIGEPASS_PASSWORD"]
    )
    response = client.get(STUDENTS_PAGE)
    response.raise_for_status()
    sesskey = get_sesskey(response.text)
    students: dict[str, Student] = {}
    if exists(FILE):
        with open("students.yml", "rt") as file:
            students = safe_load(file)
    new_students = {*get_students(client, sesskey)}
    new_students -= {*students}
    for i, student_link in enumerate(sorted(new_students)):
        remainig = len(new_students) - i
        print(
            "Remaining:",
            remainig,
            "current:",
            student_link,
            "estimated time:",
            timedelta(seconds=(MIN_SLEEP + MAX_SLEEP) * remainig / 2),
        )
        student = get_student_info(client, student_link=student_link)
        if student is None:
            continue
        students[student_link] = student
        with open(FILE, "wt") as file:
            try:
                safe_dump(students, file)
            except:
                safe_dump(students, file)
                raise
        sleep(randint(MIN_SLEEP, MAX_SLEEP))


if __name__ == "__main__":
    main()
