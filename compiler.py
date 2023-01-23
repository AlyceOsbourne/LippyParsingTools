import subprocess
import pathlib
import jinja2
from components import Variable, Statement

# jinja templates folder
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("structs"),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,
)

rendered_folder = pathlib.Path("rendered")
obj_folder = pathlib.Path("obj")
exe_folder = pathlib.Path("exe")

rendered_folder.mkdir(exist_ok=True)
obj_folder.mkdir(exist_ok=True)
exe_folder.mkdir(exist_ok=True)


def create_asm(path, externals=tuple(), variables=None, statements=None):
    test = jinja_env.get_template("new_script.asm.jinja")
    test_rendered = test.render(
        externals=externals or tuple(),
        variables=variables or tuple(),
        statements=statements or tuple(),
    )
    test_path = rendered_folder / path
    test_path.write_text(test_rendered)
    return test_path


def nasm(_obj_path, _asm_path):
    sp = subprocess.Popen(["nasm", "-f", "win32", "-o", _obj_path, _asm_path])
    sp.wait()
    if sp.returncode != 0:
        raise Exception(f"nasm failed with code {sp.returncode}")


def link(_exe_path, _obj_path):
    sp = subprocess.Popen(f"gcc -o {_exe_path} {_obj_path}".split())
    sp.wait()
    if sp.returncode != 0:
        raise Exception(f"linker failed with code {sp.returncode}")


def run(_exe_path):
    sp = subprocess.Popen(
        [
            _exe_path,
        ],
        stdout=subprocess.PIPE,
    )
    while sp.poll() is None:
        line = sp.stdout.readline()
        if line:
            print(line.decode("utf-8").strip())
    print(sp.stdout.read().decode("utf-8").strip())
    if sp.returncode != 0:
        raise Exception(f"program failed with code {sp.returncode}")
    print("program exited with code 0")


def build(path: pathlib.Path):
    asm = rendered_folder / path
    obj = obj_folder / path.with_suffix(".obj").name
    exe = exe_folder / path.with_suffix(".exe").name

    try:
        nasm(obj, asm)
        link(exe, obj)
    finally:
        # asm.unlink(missing_ok = True)
        obj.unlink(missing_ok=True)
        if exe.exists():
            run(exe)


if __name__ == "__main__":
    path = pathlib.Path("test.asm")

    create_asm(
        path,
        externals=(
            "_printf",
            "_scanf",
        ),
        variables=[
                Variable(
                        "lippy_version",
                        "db",
                        '"Lippy 0.0.0.1", 0x0A, 0',
                ),
        ],
        statements=[
            Statement("print", "lippy_version"),
            Statement("mov", "eax, 0"),
            Statement("ret", None),
        ],
    )
    build(path)
