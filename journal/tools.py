import openpyxl
from .models import *

class Import(object):

    def __init__(self, data):
        self.uploaded_file = data.get("file")

    def add_teachers(self):
        file = self.uploaded_file
        wb = openpyxl.load_workbook(filename=file)
        ws = wb.worksheets[0]
        error = []
        headers = self.getting_headers(ws)
        print(headers)

        # for row in range(2, ws.max_row+1):
        #     # print(row)
        #     row_dict = dict()
        #     row_dict2 = dict()
        #     for column in range(s.max_column):
        #         value = s.cell(row, column + 1).value
        #         if value:

            # if value_count > 1:
            #     if a_score == 0:
            #         error.append(f'Невозможно импортировать. Добавьте код в step_id Подбора ПОАКС строка{row}')
            #     if b_score == 0:
            #         error.append(f'Невозможно импортировать. Добавьте код в step_id Выбора ПОАКС строка{row}')
            #     if c_score == 0:
            #         error.append(f'Невозможно импортировать. Добавьте код в step_id Подбора IVR строка{row}')
            #     if d_score == 0:
            #         error.append(f'Невозможно импортировать. Добавьте код в step_id Выбора IVR строка{row}')
            #     if not error:
            # print('Загрузка')
            # ScenarioName.objects.bulk_create(name_objects)
            # ScenarioVersion.objects.bulk_create(version_objects)
            # ScenarioValidTill.objects.bulk_create(till_objects)
            # print('Загрузка завершена')

        return error
