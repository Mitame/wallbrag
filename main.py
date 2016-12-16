import os
import subprocess
import sys
import io

from flask import Flask, make_response, send_file, request, jsonify

TEMP_DIR = "/tmp"
FIFO_BASE_PATH = TEMP_DIR  + "/wallpaper_brag"
THUMBNAIL_HEIGHT = 128
IMAGE_EXT_FILTER = [".png", ".jpg", ".jpeg", ".jpe"]

app = Flask(__name__)

base_dir = None

temp_index = 0

original_isabs = os.path.isabs
def new_isabs(path):
    if isinstance(path, str):
        original_isabs(path)
    else:
        return True
os.path.isabs = new_isabs

def get_full_path(rel_path):
    full_path = os.path.abspath(os.path.join(base_dir, rel_path))
    if full_path.startswith(base_dir):
        return full_path
    else:
        raise PermissionError("Not allowed to access directory")

def create_temp():
    global temp_index

    created = False
    while not created:
        try:
            temp_path = FIFO_BASE_PATH + ".%i" % temp_index
            temp_index += 1
            # os.mkfifo(temp_path)
            # open(temp_path, "w").close() # create the file
            created = True
        except FileExistsError:
            created = False

    return temp_path

def delete_temp(path):
    os.remove(path)


def get_thumbnail_data(file_path):
    # out_file = create_temp()
    # print("Made FIFO")

    args = [
        "/usr/bin/convert",
        file_path,
        "-resize", str(THUMBNAIL_HEIGHT),
        "jpg:-"
    ]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    parsed_data = io.BytesIO()
    parsed_data.write(stdout)
    parsed_data.seek(0)


    # print(thumb.name)
    return parsed_data

def is_image(image_path):
    for ext in IMAGE_EXT_FILTER:
        if image_path.endswith(ext):
            return True
    else:
        return False

@app.route("/.thumb/<path:path>")
def thumbnail(path):
    full_path = get_full_path(path)

    data = get_thumbnail_data(full_path)

    res = send_file(data, mimetype="image/jpeg")

    return res

@app.route("/")
@app.route("/<path:path>")
def main(path="."):
    full_path = get_full_path(path)
    if os.path.isdir(full_path):
        return send_file("static/index.html")
    else:
        return send_file(full_path)

@app.route("/api/images/list")
def images_list():
    search_directory = request.args.get("dir", "")
    full_path = get_full_path(search_directory)

    # Get the root paths file and folders
    try:
        path, dirs, files = next(os.walk(full_path))
    except StopIteration:
        path, dirs, files = (full_path, [], [])

    data = {
        "dirs": [],
        "images": []
    }

    for directory in dirs:
        print(directory)
        if directory in [".", ".."]:
            continue

        dir_full_path = os.path.join(path, directory)
        dir_rel_path = os.path.relpath(dir_full_path, base_dir)
        data["dirs"].append(dir_rel_path)

    for image in files:
        if not is_image(image):
            continue
        img_full_path = os.path.join(path, image)
        img_rel_path = os.path.relpath(img_full_path, base_dir)
        data["images"].append(img_rel_path)

    return jsonify(data)

@app.route("/api/images/view")
def images_view():
    req_image_path = request.args.get("path")
    image_path = get_full_path(req_image_path)

    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return 404


def main():
    global base_dir
    if len(sys.argv) == 2:
        base_dir = os.path.abspath(sys.argv[1])
    else:
        base_dir = os.getcwd()

    app.run()

if __name__ == "__main__":
    main()
