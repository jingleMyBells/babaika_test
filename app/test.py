from app.services import HostService


def test():
    hosts = HostService.multi_from_db_as_dict()
    print(hosts)


test()