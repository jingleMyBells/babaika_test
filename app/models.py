from . import db


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    protocol = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    domain_zone = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(255), nullable=True)
    last_code = db.Column(db.Integer, nullable=True)
    # не факт что тут не поле
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(255), nullable=False, default='Undefined')
    query_params = db.relationship('HostQueryParams', backref='host')
    # надо добавить datetime последнего опроса
    image = db.Column(db.LargeBinary)


class HostQueryParams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100))
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
