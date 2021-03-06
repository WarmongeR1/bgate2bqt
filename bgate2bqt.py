#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sapronov Alexander
sapronov.alexander92@gmail.com

2014.
"""

import sys
from lxml.html import parse, tostring
import urlparse
from HTMLParser import HTMLParser
from time import gmtime, strftime
import argparse
import os
import urllib2
from lxml import html
import random
import re
from yandex_translate import *
import subprocess
import datetime

GL_SCRIPT_NAME = "bgate2bqt"
GL_SCRIPT_VERSION = "0.0.2"
API_YANDEX_KEY = ''
DEBUG = False


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return self.fed
        # return ' '.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def to_log(text):
    #todo
    print u"{0}: {1}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), text)


class ShortNameDetector():

    ShortNames_ENG = {
        1: 'Ge. Ge Gen. Gen Gn. Gn Genesis',
        2: 'Ex. Ex Exo. Exo Exod. Exod Exodus',
        3: 'Lev. Lev Le. Le Lv. Lv Levit. Levit Leviticus',
        4: 'Nu. Nu Num. Num Nm. Nm Numb. Numb Numbers',
        5: 'De. De Deut. Deut Deu. Deu Dt. Dt  Deuteron. Deuteron Deuteronomy',
        6: 'Jos. Jos Josh. Josh Joshua',
        7: 'Jdg. Jdg Judg. Judg Judge. Judge Judges',
        8: 'Ru. Ru Ruth Rth. Rth Rt. Rt',
        9: '1Sa. 1Sa 1S. 1S 1Sam. 1Sam 1Sm. 1Sm 1Sml. 1Sml 1Samuel',
        10: '2Sa. 2Sa 2S. 2S 2Sam. 2Sam 2Sm. 2Sm 2Sml. 2Sml 2Samuel',
        11: '1Ki. 1Ki 1K. 1K 1Kn. 1Kn 1Kg. 1Kg 1King. 1King 1Kng. 1Kng 1Kings',
        12: '2Ki. 2Ki 2K. 2K 2Kn. 2Kn 2Kg. 2Kg 2King. 2King 2Kng. 2Kng 2Kings',
        13: '1Chr. 1Chr 1Ch. 1Ch 1Chron. 1Chron',
        14: '2Chr. 2Chr 2Ch. 2Ch 2Chron. 2Chron',
        15: 'Ezr. Ezr Ezra',
        16: 'Ne. Ne Neh. Neh Nehem. Nehem Nehemiah',
        17: 'Esth. Esth Est. Est Esther Es Es.',
        18: 'Job. Job Jb. Jb',
        19: 'Ps. Ps Psa. Psa Psal. Psal Psalm Psalms',
        20: 'Pr. Pr Prov. Prov Pro. Pro Proverb Proverbs',
        21: 'Ec. Ec Eccl. Eccl Ecc. Ecc Ecclesia. Ecclesia',
        22: 'Song. Song Songs SS. SS Sol. Sol',
        23: 'Isa. Isa Is. Is Isaiah',
        24: 'Je. Je Jer. Jer Jerem. Jerem Jeremiah',
        25: 'La. La Lam. Lam Lament. Lament Lamentation Lamentations',
        26: 'Ez. Ez Eze. Eze Ezek. Ezek Ezekiel',
        27: 'Da. Da Dan. Dan Daniel',
        28: 'Hos. Hos Ho. Ho Hosea',
        29: 'Joel. Joel Joe. Joe',
        30: 'Am. Am Amos Amo. Amo',
        31: 'Ob. Ob Obad. Obad. Obadiah Oba. Oba',
        32: 'Jon. Jon Jnh. Jnh. Jona. Jona Jonah',
        33: 'Mi. Mi Mic. Mic Micah',
        34: 'Na. Na Nah. Nah Nahum',
        35: 'Hab. Hab Habak. Habak Habakkuk',
        36: 'Zeph. Zeph  Zep. Zep Zephaniah',
        37: 'Hag. Hag Haggai',
        38: 'Ze. Ze Zec. Zec Zech. Zech Zechariah',
        39: 'Mal. Mal Malachi',
        40: 'Mt. Mt Ma. Ma Matt. Matt Mat. Mat Matthew',
        41: 'Mk. Mk Mar. Mar Mr. Mr Mrk. Mrk Mark',
        42: 'Lk. Lk Lu. Lu Luk. Luk Luke',
        43: 'Jn. Jn Jno. Jno Joh. Joh John',
        44: 'Ac. Ac Act. Act Acts',
        45: 'Ro. Ro Rom. Rom Romans',
        46: '1Co. 1Co 1Cor. 1Cor 1Corinth. 1Corinth 1Corinthians',
        47: '2Co. 2Co 2Cor. 2Cor 2Corinth. 2Corinth 2Corinthians',
        48: 'Ga. Ga Gal. Gal Galat. Galat Galatians',
        49: 'Eph. Eph Ep. Ep Ephes. Ephes Ephesians',
        50: 'Php. Php Ph. Ph Phil. Phil Phi. Phi. Philip. Philip Philippians',
        51: 'Col. Col Colos. Colos Colossians',
        52: '1Th. 1Th 1Thes. 1Thes 1Thess. 1Thess 1Thessalonians',
        53: '2Th. 2Th 2Thes. 2Thes 2Thess. 2Thess 2Thessalonians',
        54: '1Ti. 1Ti 1Tim. 1Tim 1Timothy',
        55: '2Ti. 2Ti 2Tim. 2Tim 2Timothy',
        56: 'Tit. Tit Ti. Ti Titus',
        57: 'Phm. Phm Phile. Phile Phlm. Phlm Philemon',
        58: 'He. He Heb. Heb Hebr. Hebr Hebrews',
        59: 'Jas. Jas Ja. Ja Jam. Jam Jms. Jms James',
        60: '1Pe. 1Pe 1Pet. 1Pet 1Peter',
        61: '2Pe. 2Pe 2Pet. 2Pet 2Peter',
        62: '1Jn. 1Jn 1Jo. 1Jo 1Joh. 1Joh 1Jno. 1Jno 1John',
        63: '2Jn. 2Jn 2Jo. 2Jo 2Joh. 2Joh 2Jno. 2Jno 2John',
        64: '3Jn. 3Jn 3Jo. 3Jo 3Joh. 3Joh 3Jno. 3Jno 3John',
        65: 'Jud. Jud Jude Jd. Jd',
        66: 'Rev. Rev Re. Re Rv. Rv Revelation',
        67: '1maccabees 1Mac. 1Mac 1Maccabees',
        68: '2maccabees 2Mac. 2Mac 2Maccabees',
        69: '3maccabees 3Mac. 3Mac 3Maccabees',
        70: 'baruch Bar. Bar Baruch',
        71: '2esdras 2Esd. 2Esd 2Es. 2Es 2Esdr. 2Esdr 2Esdras',
        72: '3esdras 3Esd. 3Esd 3Es. 3Es 3Esdr. 3Esdr 3Esdras',
        73: 'judith Judith',
        74: 'epistle Ep. Ep Epistle Посл.Иеремии',
        75: 'wisdom Wis. Wis Wisd. Wisd Wisdom',
        76: 'sirach Sir. Sir Sirach',
        77: 'tobit Tob. Tob Tobit'
    }

    ShortNames_RUS = {
        1: 'Быт. Быт Бт. Бт Бытие',
        2: 'Исх. Исх Исход',
        3: 'Лев. Лев Лв. Лв Левит',
        4: 'Чис. Чис Чс. Чс Числ. Числ Числа',
        5: 'Втор. Втор Вт. Вт Втрзк. Втрзк Второзаконие',
        6: 'Иис.Нав. Иис.Нав Нав. Нав Иисус Навин',
        7: 'Суд. Суд Сд. Сд Судьи',
        8: 'Руф. Руф Рф. Рф Руфь',
        9: '1Цар. 1Цар 1Цр. 1Цр 1Ц 1Царств. 1Царств',
        10: '2Цар. 2Цар 2Цр. 2Цр 2Ц 2Царств. 2Царств',
        11: '3Цар. 3Цар 3Цр. 3Цр 3Ц 3Царств. 3Царств',
        12: '4Цар. 4Цар 4Цр. 4Цр 4Ц 4Царств. 4Царств',
        13: '1Пар. 1Пар 1Пр. 1Пр',
        14: '2Пар. 2Пар 2Пр. 2Пр',
        15: 'Ездр. Ездр Езд. Езд Ез. Ез',
        16: 'Неем. Неем. Нм. Нм Неемия',
        17: 'Есф. Есф Ес. Ес Есфирь',
        18: 'Иов. Иов Ив. Ив',
        19: 'Пс. Пс Псалт. Псалт Псал. Псал Псл. Псл Псалом Псалтирь Псалмы',
        20: 'Прит. Прит Притч. Притч Пр. Пр Притчи Притча',
        21: 'Еккл. Еккл Ек. Ек Екк. Екк Екклесиаст',
        22: 'Песн. Песн Пес. Пес Псн. Псн Песн.Песней Песни',
        23: 'Ис. Ис Иса. Иса Исаия Исайя',
        24: 'Иер. Иер Иерем. Иерем Иеремия',
        25: 'Плач. Плач Плч. Плч Пл. Пл Пл.Иер. Пл.Иер Плач Иеремии',
        26: 'Иез. Иез Из. Иезек. Иезек Иезекииль',
        27: 'Дан. Дан Дн. Дн Днл. Днл Даниил',
        28: 'Ос. Ос Осия Hos. Hos Ho. Ho Hosea',
        29: 'Иоил. Иоил Ил. Ил Иоиль',
        30: 'Ам. Ам Амс. Амс Амос',
        31: 'Авд. Авд Авдий',
        32: 'Ион. Ион. Иона',
        33: 'Мих. Мих Мх. Мх Михей',
        34: 'Наум. Наум',
        35: 'Авв. Авв Аввак. Аввак Аввакум',
        36: 'Соф. Соф Софон. Софон Софония',
        37: 'Агг. Агг Аггей',
        38: 'Зах. Зах Зхр. Зхр Захар. Захар Захария',
        39: 'Мал. Мал Малах. Малах Млх. Млх Малахия',
        40: 'Матф. Матф Мтф. Мтф Мф. Мф Мт. Мт Матфея Матфей Мат Мат.',
        41: 'Мар. Мар Марк. Марк Мрк. Мрк Мр. Мр Марка Мк Мк.',
        42: 'Лук. Лук Лк. Лк Лукa Луки',
        43: 'Иоан. Иоан Ин. Ин Иоанн Иоанна',
        44: 'Деян. Деян Дея. Дея Д.А. Деяния',
        45: 'Иак. Иак Ик. Ик Иаков Иакова',
        46: '1Пет. 1Пет 1Пт. 1Пт 1Птр. 1Птр 1Петр. 1Петр 1Петра',
        47: '2Пет. 2Пет 2Пт. 2Пт 2Птр. 2Птр 2Петр. 2Петр 2Петра',
        48: '1Иоан. 1Иоан 1Ин. 1Ин 1Иоанн 1Иоанна',
        49: '2Иоан. 2Иоан 2Ин. 2Ин 2Иоанн 2Иоанна',
        50: '3Иоан. 3Иоан 3Ин. 3Ин 3Иоанн 3Иоанна',
        51: 'Иуд. Иуд Ид. Ид Иуда Иуды',
        52: 'Рим. Рим Римл. Римл Римлянам',
        53: '1Кор. 1Кор 1Коринф. 1Коринф 1Коринфянам 1Коринфянам',
        54: '2Кор. 2Кор 2Коринф. 2Коринф 2Коринфянам 2Коринфянам',
        55: 'Гал. Гал Галат. Галат Галатам',
        56: 'Еф. Еф Ефес. Ефес Ефесянам',
        57: 'Фил. Фил Флп. Флп Филип. Филип Филиппийцам',
        58: 'Кол. Кол Колос. Колос Колоссянам',
        59: '1Фесс. 1Фесс 1Фес. 1Фес 1Фессалоникийцам',
        60: '2Фесс. 2Фесс 2Фес. 2Фес 2Фессалоникийцам',
        61: '1Тим. 1Тим  1Тимоф. 1Тимоф 1Тимофею',
        62: '2Тим. 2Тим 2Тимоф. 2Тимоф 2Тимофею',
        63: 'Тит. Тит Титу',
        64: 'Флм. Флм Филимон. Филимон Филимону',
        65: 'Евр. Евр Евреям',
        66: 'Откр. Откр Отк. Отк Откровен. Откровен Апок. Апок Откровение Апокалипсис',
        67: '1Макк. 1Макк. 1Маккав. 1Маккав 1Мак. 1Мак 1Маккавейская',
        68: '2Макк. 2Макк. 2Маккав. 2Маккав 2Мак. 2Мак 2Маккавейская',
        69: '3Макк. 3Макк. 3Маккав. 3Маккав 3Мак. 3Мак 3Маккавейская',
        70: 'Вар. Вар Варух',
        71: '2Ездр. 2Ездр 2Езд. 2Езд 2Ездра 2Ездры 2Ез 2Ез.',
        72: '3Ездр. 3Ездр 3Езд. 3Езд 3Ездра 3Ездры 3Ез 3Ез.',
        73: 'Иудиф. Иудиф Иудифь Judith',
        74: 'Посл.Иер. Посл.Иер Посл.Иерем. Посл.Иерем Посл.Иеремии Посл.Иеремии',
        75: 'Прем.Сол. Премудр.Соломон. Премудр.Сол. Премудр. Премудр.Соломона Премудрость Премудрости',
        76: 'Сир. Сир Сирах',
        77: 'Тов. Тов Товит'
    }

    BookNames = {}
    ShortNames = {}

    def __init__(self):
        self.__fill_ShortNames()
        self.__generate_BookNames()

    def __fill_ShortNames(self):
        self.ShortNames["rus"] = self.ShortNames_RUS
        self.ShortNames["eng"] = self.ShortNames_ENG

    def __generate_BookNames(self):

        list_tables = []

        for key, value in self.ShortNames.items():
            list_tables.append(value)

        for table in list_tables:
            for key, value in table.items():
                try:
                    self.BookNames[key] += value
                except KeyError:
                    self.BookNames[key] = value

    def get_short_name(self, fullname, options=None):
        return self.__get_short_name(self.__get_number_of_table(fullname), options)

    def __get_number_of_table(self, fullname):
        table = self.BookNames
        # сделать таблицу названия книг
        book_number = 0
        max_percent = 0
        for key, value in table.items():
            current_cnt = 0
            list_shortnames = value.split()
            for shortname in list_shortnames:
                if shortname in fullname or fullname in shortname:
                    current_cnt += 1
            current_percent = float(current_cnt) / len(list_shortnames)
            if current_percent > max_percent:
                book_number = key
                max_percent = current_percent
        return book_number

    def __get_short_name(self, book_number, options):
        result_data = ""
        for language in options.get("language"):
            result_data += " " + self.__get_shortname_from_table(book_number, self.ShortNames[language])
        return result_data

    def __get_shortname_from_table(self, book_number, table, options=None):
        result = ""
        if options is None:
            result = table.get(book_number)
        return result


class EncodingDetector():

    def getEncoding(self, t_path):
        FileEncoding = 'utf-8'
        try:

            # get encoding from enca
            p = subprocess.Popen("enca" + " '%s'" % t_path, shell=True,
                stdout = subprocess.PIPE)
            EncaResult = p.stdout.read()

            if EncaResult < 0:
                to_log("enca завершил работу некорректно, ошибка: %s" % -retcode)
            else:
                # save encoding
                if (EncaResult.find("Universal transformation format 8 bits;") >= 0):
                    FileEncoding = 'utf-8'
                if (EncaResult.find("Universal transformation format 16 bits;") >= 0):
                    FileEncoding = 'utf-16'
                if (EncaResult.find("Universal transformation format 32 bits;") >= 0):
                    FileEncoding = 'utf-32'
                if (EncaResult.find("Universal character set 2 bytes; UCS-2; BMP") >= 0):
                    FileEncoding = 'ucs-2'
                if (EncaResult.find("MS-Windows code page 1251") >= 0):
                    FileEncoding = "windows-1251"
                if (EncaResult.find("MS-Windows code page 1252") >= 0):
                    FileEncoding = "windows-1252"
                if (EncaResult.find("MS-Windows code page 1253") >= 0):
                    FileEncoding = "windows-1253"
                if (EncaResult.find("MS-Windows code page 1254") >= 0):
                    FileEncoding = "windows-1254"
                if (EncaResult.find("MS-Windows code page 1255") >= 0):
                    FileEncoding = "windows-1255"
                if (EncaResult.find("MS-Windows code page 1256") >= 0):
                    FileEncoding = "windows-1256"
                if (EncaResult.find("MS-Windows code page 1257") >= 0):
                    FileEncoding = "windows-1257"
                if (EncaResult.find("MS-Windows code page 1258") >= 0):
                    FileEncoding = "windows-1258"
                if (EncaResult.find("7bit ASCII characters") >= 0):
                    FileEncoding = "ascii"
                if (EncaResult.find("KOI8-R Cyrillic") >= 0):
                    FileEncoding = "koi8-r"
                if (EncaResult.find("KOI8-U Cyrillic") >= 0):
                    FileEncoding = "koi8-u"
                if (EncaResult.find("Unrecognized encoding") >= 0):
                    #FileEncoding = "utf-8";
                    FileEncoding = "Unrecognized encoding"

                #print ("Определение кодировки успешно выполнено.\n").decode('utf-8')

        except OSError, Error:
            print ("Запуск enca не удался:").decode('utf-8'), Error
        #print FileEncoding, t_path

        return FileEncoding


class LanguageDetector():
    GL_LANGUAGES = [
        ["ru", "rus"],
        ["en", "eng"],
        ["pl", "pol"],
        ["uk", "ukr"],
        ["de", "deu"],
        ["fr", "fra"],
        ["es", "esl"],
        ["it", "ita"],
        ["bg", "bul"],
        ["cs", "ces"],
        ["tr", "tur"],
        ["ro", "rum"],
        ["sr", "sr"]
    ]

    def detect(self, path, encoding=None):
        translate = YandexTranslate(API_YANDEX_KEY)
        #print('Current languages:', translate.langs)
        # print('Detect language:', translate.detect('Привет, мир!'))

        n = 10
        m = 50
        fragments = self.__getNfragmentsTextbyMletters(path, n, m, encoding)
        results = {}

        results["rus"] = 0
        results["eng"] = 0
        results["pol"] = 0
        results["ukr"] = 0
        results["deu"] = 0
        results["fra"] = 0
        results["esl"] = 0
        results["ita"] = 0
        results["bul"] = 0
        results["ces"] = 0
        results["tur"] = 0
        results["rum"] = 0
        results["sr"] = 0
        results["unknown"] = 0

        for fragment in fragments:
            try:
                textlanguage = translate.detect(fragment)
                for Pair in self.GL_LANGUAGES:
                    if Pair[0] == textlanguage:
                        #print Pair[1]
                        results[Pair[1]] = results[Pair[1]] + 1
                        break
            except YandexTranslateException as e:
                print e

        max = results['eng']
        max2 = 'unknown'
        for elem in results:
            if results[elem] >= max:
                max = results[elem]
                max2 = elem

        return max2

    def __getNfragmentsTextbyMletters(self, path, n, m, encoding):
        if encoding is None:
            encoding = EncodingDetector().getEncoding(path)
        file = open(path, 'r')
        str = file.read().decode(encoding).encode('utf_8').strip()
        file.close()
        rtext = []
        i = 0
        p = re.compile(r'<.*?>')
        str = p.sub('', str)
        while i < n:
            value = random.randint(0, len(str))
            text = str[value : value + m]
            if text:
                rtext.append(text)
                i += 1
        return rtext


class ProxyGenerator():

    # urls = [
    #         'http://spys.ru/en/http-proxy-list/',
    #         'http://spys.ru/en/http-proxy-list/1/',
    #         'http://spys.ru/en/http-proxy-list/2/',
    #         'http://spys.ru/en/http-proxy-list/3/',
    #     ]

    def __getproxy(self, url):
        try:
            rs = urllib2.urlopen(url).read()
        except Exception as e:
            to_log(e)
            return
        tree = html.fromstring(rs)
        ip = tree.xpath('//td/font[@class="spy14"]')
        list_proxy = []
        for i in ip:
            list_proxy.append(i.next.text)
        self.__save_list_proxy(list_proxy)

    def generate_proxy_list(self):
        self.__getproxy('http://spys.ru/en/http-proxy-list/')

    def __save_list_proxy(self, list_proxy):
        PROXY_FILE_LIST_NAME = "proxy_list"
        f = open(os.path.abspath(PROXY_FILE_LIST_NAME))
        f.writelines(list_proxy)
        f.close()


class ProxyChecker():
    pass


class ParseBiblegateway():

    class CCurrentSettingsBook():
        TableBooks = [
            ['Genesis',         'Gen'],
            ['Exodus',          'Exod'], ['Leviticus',       'Lev'],
            ['Numbers',         'Num'], ['Deuteronomy',     'Deut'],
            ['Joshua',          'Josh'], ['Judges',          'Judg'],
            ['Ruth',            'Ruth'], ['1Samuel',         '1Sam'],
            ['2Samuel',         '2Sam'], ['1Kings',          '1Kgs'],
            ['2Kings',          '2Kgs'], ['1Chron',          '1Chr'],
            ['2Chron',          '2Chr'], ['Ezra',            'Ezra'],
            ['Nehemiah',        'Neh'], ['Esther',          'Esth'],
            ['Job',             'Job'], ['Psalm',           'Ps'],
            ['Proverbs',        'Prov'], ['Ecclesia',        'Eccl'],
            ['Song',            'Song'], ['Isaiah',          'Isa'],
            ['Jeremiah',        'Jer'], ['Lament',          'Lam'],
            ['Ezekiel',         'Ezek'], ['Daniel',          'Dan'],
            ['Hosea',           'Hos'], ['Joel',            'Joel'],
            ['Amos',            'Amos'], ['Obadiah',         'Obad'],
            ['Jonah',           'Jonah'], ['Micah',           'Mic'],
            ['Nahum',           'Nah'], ['Habakkuk',        'Hab'],
            ['Zephaniah',       'Zeph'], ['Haggai',          'Hag'],
            ['Zechariah',       'Zech'],
            ['Malachi',         'Mal'],
            ['Matthew',         'Matt'],
            ['Mark',            'Mark'], ['Luke',            'Luke'],
            [' John',           'John'], ['Acts',            'Acts'],
            ['James',           'Jas'], ['1Peter',          '1Pet'],
            ['2Peter',          '2Pet'], ['1John',           '1John'],
            ['2John',           '2John'], ['3John',           '3John'],
            ['Jude',            'Jude'], ['Romans',          'Rom'],
            ['1Corinthians',    '1Cor'], ['2Corinthians',    '2Cor'],
            ['Galatians',       'Gal'], ['Ephesian',        'Eph'],
            ['Philippians',     'Phil'], ['Colossians',      'Col'],
            ['1Thessalonians',  '1Thess'], ['2Thessalonians',  '2Thess'],
            ['1Timothy',        '1Tim'], ['2Timothy',        '2Tim'],
            ['Titus',           'Titus'], ['Philemon',        'Phlm'],
            ['Hebrews',         'Heb'],
            ['Revelation',      'Rev'],
            ['1Мак',            '1Mac'], ['2Мак',            '2Mac'],
            ['3Мак',            '3Mac'], ['Варух',           'Bar'],
            ['2Ездр',           '2Esd'], ['3Ездр',           '3Esd'],
            ['Иудиф',           'Judith'], ['Посл.Иер.',       'EpJer'],
            ['Прем.Сол.',       'WSo'], ['Сир',             'Sir'],
            ['Тов.',            'Tob'], ['Прим.',           'Prim'],
        ]

        def __init__(self):
            self.PathName = ""
            self.FullName = ""
            self.ShortName = ""
            self.ChapterQty = ""

        def generate_ini_text(self):
            def write_line(text, line):
                RN_SYMBOL = "\r\n"
                return "{0}{1}{2}".format(text, RN_SYMBOL, line)

            result_text = ""
            result_text = write_line(result_text, "{0} = {1}".format("PathName", self.PathName))
            result_text = write_line(result_text, "{0} = {1}".format("FullName", self.FullName))
            result_text = write_line(result_text, "{0} = {1}".format("ShortName",
                ShortNameDetector().get_short_name(self.FullName, {"language": ["eng"]}))
            )
            result_text = write_line(result_text, "{0} = {1}".format("ChapterQty", self.ChapterQty))
            result_text = write_line(result_text, "")

            return result_text

    class CIniSettings():
        def __init__(self, output_folder):
            self.output_folder = output_folder
            self.BibleName = ""
            self.BibleShortName = ""
            if not API_YANDEX_KEY:
                self.Language = "eng"
            else:
                self.Language = ""
            self.BookQty = 0
            self.ini_path = "default_value.ini"
            self.BookSettings = []

        def __generate_head_ini_file(self):
            def write_line(text, line):
                RN_SYMBOL = "\r\n"
                return u"{0}{1}{2}".format(text, line, RN_SYMBOL)

            def write_head(text):
                head = """//// Download from biblegateway.com
//// Converted with bgate2bqt
//// Author prog: Sapronov Alexander
//// Contact: sapronov.alexander92@gmail.com
"""
                return write_line(text, head)

            #hindi
            result_text = ""
            result_text = write_head(result_text)
            result_text = write_line(result_text, "{0} = {1}".format("BibleName", self.BibleName))
            result_text = write_line(result_text, "{0} = {1}".format("BibleShortName", self.BibleShortName))
            result_text = write_line(result_text, "{0} = {1}".format("Bible", "Y"))
            result_text = write_line(result_text, "{0} = {1}".format("ChapterSign", "<h4>"))
            result_text = write_line(result_text, "{0} = {1}".format("VerseSign", "<p>"))
            result_text = write_line(result_text, "")
            result_text = write_line(result_text, "{0} = {1}".format("Language", self.Language))
            result_text = write_line(result_text, "")

            result_text = write_line(result_text, "{0} = {1}".format("Developer", "Sapronov Alexander"))
            result_text = write_line(result_text, "{0} = {1}".format("DevContact", "sapronov.alexander92@gmail.com"))
            result_text = write_line(result_text, "{0} = {1}".format("Date", datetime.datetime.now().strftime("%Y-%m-%d")))
            result_text = write_line(result_text, "{0} = {1}".format("Type", "B"))
            result_text = write_line(result_text, "{0} = {1}".format("Version", "1.0"))

            result_text = write_line(result_text, "")

            result_text = write_line(result_text, "{0} = {1}".format("BookQty", self.BookQty))

            return result_text

        def make_ini(self):
            self.__make_ini_head_file()
            self.__make_ini_books_file()

        def __make_ini_books_file(self):
            mode = "a"
            for book in self.BookSettings:
                self.__write_to_file(book.generate_ini_text(), mode)

        def __make_ini_head_file(self):
            bibleqt_ini_name = "bibleqt.ini"
            self.ini_path = os.path.join(self.output_folder, bibleqt_ini_name)
            self.__write_to_file(self.__generate_head_ini_file())

        def __write_to_file(self, text, mode="w"):
            f = open(self.ini_path, mode)
            f.write(text)
            f.close()

    def __init__(self, url, output_folder):
        self.url = url
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse_module(self):
        self.book_text = ""
        self.root_of_site = urlparse.urlparse(self.url).hostname
        page = parse(self.url).getroot()
        books_table = page.cssselect("table.infotable")[0]
        books_tr = books_table.cssselect("tr")[1:]

        self.IniSettings = self.CIniSettings(self.output_folder)

        #hindi
        name = page.cssselect("h1")[1].text
        self.IniSettings.BibleName = name.split("(")[0].strip()
        self.IniSettings.BibleShortName = name.split("(")[1].strip().replace(")", '').strip()

        self.IniSettings.BookQty = 0
        for book_tr in books_tr:
            self.IniSettings.BookQty += 1
            self.__clean_data()
            self.CurrentSettingsBook.FullName = book_tr.cssselect("td")[0].text
            to_log("Parse book: %s" % self.CurrentSettingsBook.FullName)
            self.__parse_book(book_tr)
            self.__save_book(self.IniSettings.BookQty)
            self.IniSettings.BookSettings.append(self.CurrentSettingsBook)
            if DEBUG and self.IniSettings.BookQty == 3:
                break

        self.IniSettings.make_ini()

    def __clean_data(self):
        self.CurrentSettingsBook = self.CCurrentSettingsBook()
        self.book_text = ""

    def __save_book(self, number):
        book_path = os.path.join(self.output_folder, "book_%s.html" % str(number).rjust(2, "0"))
        self.__write_to_file(book_path, self.book_text)
        if self.IniSettings.Language == "":
            self.IniSettings.Language = LanguageDetector().detect(book_path)
        self.CurrentSettingsBook.PathName = os.path.basename(book_path)

    def __write_to_text(self, data):
        self.book_text += data

    def __write_chapter_text(self, verses_dict, chapter_name):
        RN_SYMBOL = "\r\n"
        self.__write_to_text(u"<h4>{0}</h4>{1}".format(chapter_name.strip(), RN_SYMBOL))
        for key, value in verses_dict.items():
            # print ''.join(value)
            self.__write_to_text(u"<p>{0} {1}</p>{2}".format(key, ''.join(value).strip(), RN_SYMBOL))

    def __parse_book(self, book_tr):
        chapters_ahref = book_tr.cssselect("a")
        self.CurrentSettingsBook.ChapterQty = len(chapters_ahref)
        i = 1
        for chapter_a in chapters_ahref:
            to_log("Parse {0} chapter".format(i))
            self.__parse_chapter("http://{0}{1}".format(self.root_of_site, chapter_a.get("href")))
            i += 1
            if DEBUG and i == 5:
                break

    def __parse_chapter(self, url):
        page = parse(url).getroot()
        text_block = page.cssselect("div.passage")[0]
        # name_chapter = text_block.cssselect("h3")[0].cssselect("span")[0].text
        # chapter_num = text_block.cssselect("span.chapternum")[0].text
        chapter_name = page.cssselect("div.heading")[0].cssselect("h3")[0].text

        # hindi
        list_values = strip_tags(tostring(text_block))
        verses_id = 0
        verses = {}
        verses[verses_id] = []

        for value in list_values:
            if not value.isdigit():
                # hindi
                if value == "Footnotes:":
                    break
                verses[verses_id].append(value)
            else:
                verses_id += 1
                verses[verses_id] = []

        del verses[0]
        self.__write_chapter_text(verses, chapter_name)

    def __write_to_file(self, file_path, text):
        f = open(file_path, "w")
        f.write(text.encode("utf-8"))
        f.close()

if __name__ == "__main__":
    if sys.stdout.encoding is None:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    output_default_name = "output"
    print "START: Script - " + GL_SCRIPT_NAME + "\nvesion - " + GL_SCRIPT_VERSION
    parser = argparse.ArgumentParser(description='Parse biblegateway.com')
    parser.add_argument('-u', '--url', help='Url to module', required=True)
    parser.add_argument('-o',
        '--output',
        help='Output folder',
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), output_default_name),
        required=False)
    args = parser.parse_args()

    ProxyGenerator().generate_proxy_list()
    parser = ParseBiblegateway(args.url, args.output)

    parser.parse_module()

    # sys.exit(start(args.url, args.output))
