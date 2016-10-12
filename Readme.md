Факаба 1.3.0
============

![Скриншот](https://s17.postimg.org/dl5afjhtb/Screenshot.png)

Имиджбордный движок на Брейнфаке.

Обслуживает один тред, позволяет постить картинки, предоставляет средства для модерирования.

Преимущества
------------

- Безопасность. Программа выполняется в очень ограниченной виртуальной машине с 8 командами, код интерпретатора и сетевого драйвера занимает считанные десятки строк, его можно изучить за несколько минут. Транслятор в Си использует системный вызов `seccomp` для создания песочницы.

- Переносимость. Используется самый распространённый диалект Брейнфака, для которого существует [огромное количество](https://esolangs.org/wiki/Brainfuck_implementations) интерпретаторов и компиляторов под разные платформы. Интерфейс сетевого драйвера может быть очень легко воспроизведён на множестве языков программирования.

- Совместимость с браузерами. Не требует включённого Джаваскрипта (хотя его наличие расширяет возможности движка), был протестирован в нескольких современных браузерах, включая Елинкс.

Особенности
-----------

Полностью синхронный, поддерживает одно соединение в момент времени, поэтому легко поддаётся ДДОСу кнопкой Ф5.

Системные требования
--------------------

Необходим интерпретатор [стандартного](http://www.muppetlabs.com/~breadbox/bf/standards.html) Брейнфака со следующими свойствами:
- 363 МиБ памяти, состоящей из восьмибитных ячеек;
- беззнаковое заворачивание при увеличении 255 или уменьшении 0;
- падает при выходе за границы памяти, попытке ввести ЕОФ или наличии несбалансированных скобок.

Для взаимодействия с сетью необходим драйвер, который позволит программе вызывать функции `accept`, `recv`, `send` и `close` с помощью стандартного ввода-вывода.

К движку прилагаются драйвер, интерпретатор и транслятор в Си, написанные на Питоне 3.

Запуск
------

Запуск осуществляется с помощью сетевого драйвера:

	$ ./run.py ./fuckaba.bf localhost 8008

По умолчанию файл `fuckaba.bf` будет выполнен интерпретатором `interpreter.py`, поскольку так указано в его шебанге. Но данный интерпретатор крайне медленен, поэтому лучше скомпилировать движок в нативный код:

	$ make fuckaba

Подавать для оптимизации `CFLAGS=-O3` бессмысленно, при том, что это значительно замедляет компиляцию и требует много памяти. Запуск скомпилированного движка выглядит так:

	$ ./run.py ./fuckaba localhost 8008

Администрирование
-----------------

Администратор может удалять посты. Если включен Джаваскрипт, то для этого придётся добавить к адресу страницы якорь `#admin`. Стандартный пароль `password`, может быть изменён в исходном коде в файле `lib/admin.txt` - он должен быть той же длины в 8 байтов. Это действие потребует пересборки файла `fuckaba.bf`:

	$ make

Пароль можно изменить без пересборки, непосредственным редактированием файла `fuckaba.bf`. Специально для этого в нём есть подстрока `Пароль`, после которой следуют 8 строк с минусами. Количество минусов соотвествует коду символа.

В директории `resources` есть три файла:
- `index-head.txt` - ХТТП-заголовки главной страницы;
- `index-body.htm` - главная страница;
- `redirect-head.txt` - ХТТП-заголовки перенаправления на главную страницу.

Их можно изменять, после чего требуется пересобрать движок. ХТТП-заголовки надо разделять однобайтовым переводом строки `\n`, при сборке он будет преобразован в двухбайтовый `\r\n`.

Сохранение состояния
--------------------

Внутренее состояние виртуальной машины Брейнфака состоит из четырёх частей:
- исполняемый код;
- указатель на текущую инструкцию;
- память;
- указатель на текущую ячейку.

Если сохранить эти данные и потом возобновить исполнение, то Факаба продолжит работать с той же точки, где была прервана и все посты останутся на месте. Единственная проблема - сетевой драйвер, который имеет своё внутреннее состояние.

Чтобы можно было сохранить состояние транслированного в Си скрипта, его необходимо собирать с флагом `-g`:

	make CFLAGS=-g fuckaba

Скрипт `dump.sh` сохраняет состояние в файл `dump.bin`. Скрипт принимает аргумент - идентификатор процесса, который можно получить командой `ps -C fuckaba`.

Чтобы восстановить состояние, надо собрать программу из этого дампа:

	$ make CFLAGS=-g awoken
	$ ./run.py ./awoken localhost 8008

При запуске движок начнёт исполнение с того места, где был запечатлён.

Чтобы избежать проблемы с сетевым драйвером, надо делать дамп, когда движок простаивает в ожидании соединения.

Обновление
----------

Движок можно обновить, в том числе и сменить админский пароль или поменять начало главной страницы, сохранив все посты. В пределах одной мажорной версии расположение и формат базы данных в памяти сохраняется, поэтому можно использовать скрипт `transfer.py`. Он создаёт новый дамп из файла `fuckaba.bf`, добавляя к нему посты из старого дампа:

	$ ./transfer.py dump.bin fuckaba.bf new-dump.bin

Потом можно его скомпилировать:

	$ mv new-dump.bin dump.bin
	$ make awoken
