# Парсер документации python и PEP
## Описание

Учебный проект для практики создания парсеров.

Парсится документация Python: PEP, версии, обновления, архив с документацией.

В проекте реализован парсинг аргументов командной строки для выбора режима работы программы. Всего доступно четыре режима:
- **whats-new** (получение списка ссылок на перечень изменений в версиях Python)
- **latest-versions** (получение списка ссылок на документацию для всех версий Python)
- **download** (скачивание архива с документацией для последней версии Python)
- **pep** (получение данных о статусах всех PEP и вывод информации о несоответствиях статусов в общем списке и в карточках отдельных PEP)

Реализована возможность выбора формата вывода:
- стандартный вывод в терминал;
- вывод в терминал в табличной форме (prettytable);
- запись результатов работы в файл .csv.
### Перед использованием
Клонируйте репозиторий к себе на компьютер при помощи команд:
```
git clone https://github.com/tapp41k/bs4_parser_pep.git
```
или
```
git clone git@github.com:tapp41k/bs4_parser_pep.git
```
или
```
git clone gh repo clone tapp41k/bs4_parser_pep
```

В корневой папке нужно создать виртуальное окружение и установить зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
### смените директорию на папку ./src/
```
cd src/
```
### запустите файл main.py выбрав необходимый парсер и аргументы(приведены ниже)
```
python main.py [вариант парсера] [аргументы]
```
### Встроенные парсеры
- whats-new   
Парсер выводящий спсок изменений в python.
```
python main.py whats-new [аргументы]
```
- latest_versions
Парсер выводящий список версий python и ссылки на их документацию.
```
python main.py latest-versions [аргументы]
```
- download   
Парсер скачивающий zip архив с документацией python в pdf формате.
```
python main.py download [аргументы]
```
- pep
Парсер выводящий список статусов документов pep
и количество документов в каждом статусе. 
```
python main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```

### Автор
- [Осадчий Илья](https://github.com/tapp41k "GitHub аккаунт")
