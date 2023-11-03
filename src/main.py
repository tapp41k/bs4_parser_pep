# main.py
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm
from bs4 import BeautifulSoup

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={
                                                  'class': 'toctree-l1'})
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python,
                        desc='Выполнение цикла парсинга'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text,
                             features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append(
            (version_link, h1.text, dl_text)
        )
    return result


def latest_versions(session):
    if __name__ == '__main__':
        response = get_response(session, MAIN_DOC_URL)
        if response is None:
            return
        soup = BeautifulSoup(response.text, 'lxml')

        sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
        ul_tags = sidebar.find_all('ul')

        for ul in ul_tags:

            if 'All versions' in ul.text:
                a_tags = ul.find_all('a')
                break
        else:
            raise Exception('Ничего не нашлось')

        results = [('Ссылка на документацию', 'Версия', 'Статус')]
        pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
        # Цикл для перебора тегов <a>, полученных ранее.
        for a_tag in a_tags:
            # Извлечение ссылки.
            link = a_tag['href']
            # Поиск паттерна в ссылке.
            text_match = re.search(pattern, a_tag.text)
            if text_match is not None:
                version, status = text_match.groups()
            else:
                version, status = a_tag.text, ''
            results.append(
                (link, version, status)
            )
        # Печать результата.
        return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = soup.find('div', {'role': 'main'})
    table_tag = main_tag.find('table', {'class': 'docutils'})

    pdf_a4_tag = table_tag.find('a',
                                {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    test_file = open('test.txt', 'w')
    test_file.write('Hello, world!')
    test_file.close()

    response_down = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response_down.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    peps_row = main_tag.find_all('tr')
    count_status_in_card = defaultdict(int)
    result = [('Статус', 'Количество')]
    for i in tqdm(range(1, len(peps_row))):
        pep_href_tag = peps_row[i].a['href']
        pep_link = urljoin(PEP_URL, pep_href_tag)
        response = get_response(session, pep_link)
        soup = BeautifulSoup(response.text, 'lxml')
        main_card_tag = find_tag(soup, 'section', {'id': 'pep-content'})
        main_card_dl_tag = find_tag(main_card_tag, 'dl',
                                    {'class': 'rfc2822 field-list simple'})
        for tag in main_card_dl_tag:
            if tag.name == 'dt' and tag.text == 'Status:':
                card_status = tag.next_sibling.next_sibling.string
                count_status_in_card[card_status] += 1
                if len(peps_row[i].td.text) != 1:
                    table_status = peps_row[i].td.text[1:]
                    if card_status[0] != table_status:
                        logging.info(
                            '\n'
                            'Несовпадающие статусы:\n'
                            f'{pep_link}\n'
                            f'Статус в карточке: {card_status}\n'
                            f'Ожидаемые статусы: '
                            f'{EXPECTED_STATUS[table_status]}\n'
                                )
    total_count = sum(count_status_in_card.values())
    result.extend(count_status_in_card.items())
    result.append(('Total', str(total_count)))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
