from bs4 import BeautifulSoup
import pymysql.cursors
import io
import os
import re

# Подключаемся к базе данных (подставляем свои значения).
connection = pymysql.connect(host='192.168.5.134',
                             user='root',
                             password='1234',
                             db='simplehr',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


# Создаем новую запись в базе данных
def new_record(row, value):
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `Heroes` (row) VALUES (%s)"
        cursor.execute(sql, value)

    connection.commit()


obr_per = 0
not_obr_per = 0
persons = []
# obr_persons =[]
not_obr_persons = []


# Считываем данные из директории в массив persons
def make_persons(directory):
    for root, dirs, filenames in os.walk(directory):
        for file in filenames:
            log = open(os.path.join(root, file), 'r')
            data = log.read()
            soup = BeautifulSoup(data, 'html.parser')

            tags = soup.p.text
            results = tags.split("\n")

            for result in results:
                if result and result != ' ':
                    result = result.strip()
                    condition = re.search(r"[А-ЯЁ]* \([А-ЯЁ]*\)|[А-ЯЁ]*", result)
                    c = condition.group(0)
                    if condition and len(c) >= 2 and c != 'РВК' and c != 'ГВК':
                        persons.append(result)
                    else:
                        persons[-1] = persons[-1]+result
    return persons


# Ищем данные о месте призыва
def check_p_call(element):
    if 'г.' in element:
        n = element.index('г.')
        # obr_person.append(element[n] + ' ' + element[n + 1])
        new_record(p_call, (element[n] + ' ' + element[n + 1]))
        element.remove(element[n + 1])
        element.remove(element[n])

    if 'р-н' in element:
        n = element.index('р-н')
        # obr_person.append(element[n - 1] + ' ' + element[n])
        new_record(p_call, (element[n - 1] + ' ' + element[n]))
        element.remove(element[n])
        element.remove(element[n - 1])


# Ищем данные о годе рождения
def check_d_birth(data):
    fio_and_date = re.sub('19 19', '1919', data[0])
    data_of_birth = re.findall(r'\d{4}', fio_and_date)
    s = ''
    for j in range(0, len(data_of_birth)):
        s = s + ' ' + data_of_birth[j]
    # obr_person.append(s.lstrip())
    new_record(d_birth, s.lstrip())
    element = re.sub(r'\d{4}', '', fio_and_date).split()
    return element


folder = r'C:\Users\Полина\Downloads\Новая папка'
make_persons(folder)
for person in persons:
    try:
        # obr_person = []
        person_data = re.split(',', re.sub('г.р.', '', re.sub('р-н', ' р-н', person)))
        fio = check_d_birth(person_data)
        check_p_call(fio)
        if len(fio) >= 4:
            not_obr_persons.append(person)
            print('Не обработанно: ', person)
        elif len(fio) == 3:
            # obr_person.append(fio[0].capitalize())
            new_record(f_name, fio[0])
            # obr_person.append(fio[1].capitalize())
            new_record(m_name, fio[1])
            # obr_person.append(fio[2].capitalize())
            new_record(l_name, fio[2])
        else:
            # obr_person.append(fio[0].capitalize())
            new_record(f_name, fio[0])
            # obr_person.append(fio[1].capitalize())
            new_record(m_name, fio[1])

        addition = ''
        for i in range(1, len(person_data)):
            addition = addition + ' ' + person_data[i]
        # obr_person.append(addition.lstrip())
        new_record(addition, addition.lstrip())

        obr_per += 1

        # obr_persons.append(obr_person)

    except Exception as e:
        print(e)
        print(person)
        not_obr_per += 1


print('Обработанные:', obr_per)
print('Не обработанные:', not_obr_per + len(not_obr_persons))
print(not_obr_persons)

