from http import HTTPStatus
import csv
import zipfile
from io import TextIOWrapper
from flask import jsonify, request, url_for

from . import app

from .services import (
    HostService,
    check_and_create_db,
    unpack_url,
    upload_screenshot_by_uuid,
)
from .models import Host, HostQueryParams


@app.route('/url', methods=['POST'])
def create_host_from_body():
    input_url = request.get_json().get('url')
    new_host = unpack_url(input_url)
    return jsonify(new_host), 200


@app.route('/zip', methods=['POST'])
def create_hosts_from_file():
    input_obj = request.files['file'].stream._file
    zipfile_obj = zipfile.ZipFile(input_obj)
    file_path = zipfile_obj.namelist()[0]
    with zipfile_obj as zf:
        with zf.open(file_path, 'r') as csv_file:
            reader = csv.reader(TextIOWrapper(csv_file, 'utf-8'))
            for row in reader:
                unpack_url(row[0])
    # сделать какой-то вывод
    return {'Все': 'Четко'}, 200


@app.route('/screenshot', methods=['POST'])
def upload_screenshot():
    print(request.form['uuid'])
    # print(request.files['image'])
    if 'image' not in request.files:
        return {'Вы': 'не прислали файл'}, 400
    if 'uuid' not in request.form:
        return {'Вы': 'не прислали uuid'}, 400
    host = HostService.get_by_uuid(request.form['uuid'])
    if host:
        upload_screenshot_by_uuid(request.files['image'], host)
    else:
        return {'Нет': 'такого хоста'}, 400
    return {'Все': 'Четко'}, 200


@app.route('/get', methods=['GET'])
def get_all():
    kwargs = dict()
    if request.args:
        for key, value in request.args.items():
            kwargs[key] = value
    return jsonify(HostService.multi_from_db_as_dict(**kwargs)), 200
