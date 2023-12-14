import datetime
import openpyxl
import re
from .models import *

class Import(object):

    def __init__(self, data):
        self.uploaded_file = data.get("file")

    def getting_headers(self, ws):
        data_headers2db_field = {
            'Фамилия': 'surname',
            'Имя': 'name',
            'Родитель': 'guardian',
            'Дата рождения': 'birthday',
            'Адрес': 'address',
            'Контакт': 'mobile_phone'
        }
        return [data_headers2db_field.get(c[0].value, None) for c in ws.columns]
        

    def add_clients(self):
        
        file = self.uploaded_file
        wb = openpyxl.load_workbook(filename=file)
        ws = wb.worksheets[0]
        error = []
        headers = self.getting_headers(ws)
        cls = []
        repl = []
        for r in ws.iter_rows(min_row=2):
            cl = {}
            cont = True
            for cell in r:
                if cell.value:
                    cont = False
            if cont:
                continue
            for k, v in zip(headers,r):
                if k:
                    # валидация
                    if (k == 'surname' or k == 'name' or k == 'guardian') and not v.value:
                        error.append((v.row, 'Не введено имя или фамилия'))
                    if k == 'mobile_phone':
                        mob = str(v.value)
                        mob = re.sub(r'\D', '', mob)
                        mob = re.sub(r'^.', '7', mob)
                        v.value = mob
                        if re.match('^7([0-9]){9}[0-9]$', mob) is None:
                            error.append((v.row, 'Проверьте номер телефона'))
                    if k == 'birthday':
                        if type(v.value) != datetime.datetime:
                            if type(v.value) != int:
                                error.append((v.row, 'введите дату или год рождения'))
                            elif v.value < 1980 or v.value > datetime.datetime.now().year - 4:
                                error.append((v.row, 'некорректно введен год рождения'))
                            else:
                                v.value = datetime.datetime(v.value, 1, 1, 0, 0)
                    cl[k] = v.value
            cl_obj = Client.objects.filter(surname=cl['surname'], name=cl['name'])
            if cl_obj:
                repl.append((cl, cl_obj))
            else:
                cls.append(cl)
        if not error:
            Client.objects.bulk_create(cls)

            # далее чета с дубликатами
            if repl:
                return {'type': 'repl', 'data': repl}

        return {'type': 'error', 'data': error}
