declare function ui(selector: string, timeout: number): void;

function assert(condition: boolean): asserts condition {
    if (!condition) {
        show_error();
        throw Error();
    }
}

function is_input(elem: HTMLElement): elem is HTMLInputElement {
    return elem.tagName === "INPUT";
}

function is_table(elem: HTMLElement): elem is HTMLTableElement {
    return elem.tagName === "TABLE";
}

function is_div(elem: HTMLElement): elem is HTMLDivElement {
    return elem.tagName === "DIV";
}

function not_null<T>(elem: T | null): elem is T {
    return elem !== null;
}

function set_visibility(elem: HTMLElement, visible: boolean) {
    elem.style.display = visible ? "" : "none";
}

function get_elem<T extends HTMLElement>(
    id: string,
    check: (elem: HTMLElement) => elem is T
): T {
    let element = document.getElementById(id);
    assert(not_null(element));
    assert(check(element));
    return element;
}

const ERROR = get_elem("error", is_div);

function show_error() {
    ui("#error", 3000);
}

const SEARCH = get_elem("search", is_input);
const TABLE = get_elem("table", is_table);

interface Student {
    name: string;
    matricola: string;
}

function load_students(): Student[] {
    let result: Student[] = [];
    for (let row of TABLE.tBodies[0].rows) {
        result.push({
            name: row.cells[0].innerText.toLowerCase(),
            matricola: row.cells[1].innerText.toLowerCase(),
        });
    }
    return result;
}

const STUDENTS = load_students();

function search(text: string): boolean[] {
    let keywords = text.toLowerCase().split(" ");
    return STUDENTS.map((student) => match(student, keywords));
}

function match(student: Student, keywords: string[]): boolean {
    for (let keyword of keywords) {
        if (student.name.includes(keyword)) return true;
        if (student.matricola.includes(keyword)) return true;
    }
    return false;
}

function on_search() {
    let text = SEARCH.value;
    let result = search(text);
    for (let i = 0; i < result.length; i++) {
        set_visibility(TABLE.tBodies[0].rows[i], result[i]);
    }
}

function main() {
    SEARCH.oninput = on_search;
    assert(false);
}

main();
