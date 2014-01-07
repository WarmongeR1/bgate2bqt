####bgate2bqt

Скрипт для генерация модулей для программы Цитата из Библии с сайта http://www.biblegateway.com/

###Требования

* Python требования: yandex_translater
* Другие требования: enca

###Использование

Использование просто:
* опция `-u` или `--url`  - ссылка на модуль, например http://www.biblegateway.com/versions/English-Standard-Version-ESV-Bible
* опция `-o` или `--output`  - путь до попки куда положить, значение по умолчанию в папку "output" в директории скрипта

И выглядит примерно так вызов:
`python bgate2bqt.py -u "http://www.biblegateway.com/versions/English-Standard-Version-ESV-Bible" -o ./ESV`

###Автор

Sapronov Alexander 

*e-mail:* sapronov.alexander92 on gmail.com

###Лицензия

GNU GPLv2
