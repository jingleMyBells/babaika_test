import urllib.parse
import uuid
from uuid import uuid4
from base64 import b64encode
import base64

from flask_sqlalchemy import inspect

from app import db
from .models import Host, HostQueryParams


def check_and_create_db():
    check = inspect(db.engine)
    if check.has_table('host') is False:
        db.create_all()


class URL:

    def __init__(self, url):
        self.url = url
        self.protocol = None
        self.domain_zone = None
        self.domain = ''
        self.path = None
        self.query_params = dict()

    def unpack_to_attrs(self):
        parse_result = urllib.parse.urlparse(self.url)
        self.protocol = parse_result.scheme
        self.path = parse_result.path
        if ':' in parse_result.netloc:
            netloc = parse_result.netloc.split(':')[0]
            self.domain_zone = netloc.split('.')[-1]
            self.domain = netloc[0:-(len(self.domain_zone) + 1)]
        else:
            self.domain_zone = parse_result.netloc.split('.')[-1]
            self.domain = parse_result.netloc[0:-(len(self.domain_zone) + 1)]
        if parse_result.query:
            for param in parse_result.query.split('&'):
                param_key = param.split('=')[0]
                param_value = param.split('=')[1]
                self.query_params[param_key] = param_value

    def as_dict(self):
        return {
            'url': self.url,
            'protocol': self.protocol,
            'domain': self.domain,
            'domain_zone': self.domain_zone,
            'path': self.path,
            'query_params': self.query_params
        }

    def _create_params_in_db(self, params, host_id):
        # тут надо сделать добавление в сессию всех параметров
        if params:
            for key, value in params.items():
                new_obj = HostQueryParams(
                    key=key,
                    value=value,
                    host_id=host_id,
                )
                db.session.add(new_obj)
            db.session.commit()

    def create_in_db(self):
        obj = self.as_dict()
        params = obj.pop('query_params')
        # не факт что тут hex
        obj['uuid'] = uuid.uuid4().hex
        # надо подумать надо статусами
        obj['status'] = 'Undefined'
        new_host = Host(**obj)
        db.session.add(new_host)
        db.session.commit()
        host = Host.query.filter_by(url=self.url).first()
        self._create_params_in_db(params, host.id)


def unpack_url(url):
    url_to_unpack = URL(url)
    url_to_unpack.unpack_to_attrs()
    url_to_unpack.create_in_db()
    return url_to_unpack.as_dict()


class HostService:

    @staticmethod
    def get_by_uuid(uuid):
        return Host.query.filter_by(uuid=uuid).first()

    @staticmethod
    def multi_from_db_as_dict(**kwargs):
        hosts = Host.query.filter_by(**kwargs).all()
        result = dict()
        for host in hosts:
            result[host.url] = host.last_code
        return result


def upload_screenshot_by_uuid(file, host):
    if host:
        host.image = file.read()
        db.session.add(host)
        db.session.commit()


def convert_raw_to_render(data):
    return base64.b64encode(data).decode('ascii')


