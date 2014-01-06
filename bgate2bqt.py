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
GL_SCRIPT_VERSION = "0.0.1"
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
    print "{0}: {1}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), text)


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
                for Pair in GL_LANGUAGES:
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

            self.ShortName = self.__generate_short_name()
            result_text = ""
            result_text = write_line(result_text, "{0} = {1}".format("PathName", self.PathName))
            result_text = write_line(result_text, "{0} = {1}".format("FullName", self.FullName))
            result_text = write_line(result_text, "{0} = {1}".format("ShortName", self.ShortName))
            result_text = write_line(result_text, "{0} = {1}".format("ChapterQty", self.ChapterQty))
            result_text = write_line(result_text, "")

            return result_text

        def __generate_short_name(self):
            for Pair in self.TableBooks:
                if Pair[0] == self.FullName:
                    return Pair[1]
            return "{0} (Short name not detect)".format(self.FullName)

    class CIniSettings():
        def __init__(self, output_folder):
            self.output_folder = output_folder
            self.BibleName = ""
            self.BibleShortName = ""
            self.Language = "eng"
            self.BookQty = 0
            self.ini_path = "default_value.ini"
            self.BookSettings = []

        def __generate_head_ini_file(self):
            def write_line(text, line):
                RN_SYMBOL = "\r\n"
                return "{0}{1}{2}".format(text, line, RN_SYMBOL)

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
            result_text = write_line(result_text, "{0} = {1}".format("BookQty", self.BookQty))
            result_text = write_line(result_text, "{0} = {1}".format("Language", self.Language))

            result_text = write_line(result_text, "")

            result_text = write_line(result_text, "{0} = {1}".format("Developer", "Sapronov Alexander"))
            result_text = write_line(result_text, "{0} = {1}".format("DevContact", "sapronov.alexander92@gmail.com"))
            result_text = write_line(result_text, "{0} = {1}".format("Date", datetime.datetime.now().strftime("%Y-%m-%d")))
            result_text = write_line(result_text, "{0} = {1}".format("Type", "B"))
            result_text = write_line(result_text, "{0} = {1}".format("Version", "1.0"))

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
            LanguageDetector().detect(book_path)
        self.CurrentSettingsBook.PathName = os.path.basename(book_path)

    def __write_to_text(self, data):
        self.book_text += data

    def __write_chapter_text(self, verses_dict, chapter_name):
        RN_SYMBOL = "\r\n"
        self.__write_to_text("<h4>{0}</h4>{1}".format(chapter_name.strip(), RN_SYMBOL))
        for key, value in verses_dict.items():
            # print ''.join(value)
            self.__write_to_text("<p>{0} {1}</p>{2}".format(key, ''.join(value).strip(), RN_SYMBOL))

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
        f.write(text)
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
