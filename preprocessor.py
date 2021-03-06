#!/usr/bin/python3

# В комментах к командам символом ">" обозначается состояние памяти перед вызовом, а "<" - после
# Дефисом после треугольной скобки обозначено положение указателя

import os.path

def go(count):
	if count > 0:
		return ">" * count
	else:
		return "<" * -count

def visit(count, instruction):
	return go(count) + instruction + go(-count)

def increase(count):
	if count > 0:
		return "+" * count
	else:
		return "-" * -count

names = {"END", "INCLUDE"}
commands = {}
blocks = {}

def instruction(function):
	name = function.__name__.upper()

	if name.endswith("_COMMAND"):
		category = commands
		name = name[: -8]
	else:
		category = blocks
		name = name[: -6]

	if name in names:
		raise Exception("Имя занято")

	names.add(name)
	category[name] = function

	return function

# Простые команды

@instruction
def go_command(root, count):
	"Переходит на заданное число ячеек влево или вправо"

	return go(count)

@instruction
def input_command(root):
	"Вводит байт"

	return ","

@instruction
def output_command(root):
	"Выводит байт"

	return "."

@instruction
def zero_command(root):
	"Зануляет данную ячейку"

	return "[-]"

@instruction
def increase_command(root, count):
	"Увеличивает или уменьшает данную ячеку на заданное число"

	return increase(count)

@instruction
def visit_block(root, count):
	"Переходит к указанной ячейке на входе и возвращается на выходе"

	return go(count), go(-count)

@instruction
def if_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. После выполнения она зануляется.

		>- a

		<- a

		>- неважно

		<- 0
	"""

	return "[", "[-]]"

@instruction
def bool_if_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. После выполнения она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 1

		>- 1

		<- 0
	"""

	return "[", "-]"

@instruction
def if_l_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Перед выполненем она зануляется.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "[[-]", "]"

@instruction
def bool_if_l_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Перед выполнения она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "[-", "]"

@instruction
def if_save_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется.

		>- a
		>  0
		>  0

		<- a
		<  0
		<  0

		>- x - неважно
		>  0
		>  0

		<- a, если не выполнился, иначе x
		<  0
		<  0
	"""

	return "[", ">>+<]>[-<]<"

@instruction
def if_save_back_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется.

		>  0
		>  0
		>- a

		<  0
		<  0
		<- a

		>  0
		>  0
		>- x - неважно

		<  0
		<  0
		<- a, если не выполнился, иначе x
	"""

	return "[", "<<+>]<[->]>"

@instruction
def if_save_flag_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется. Сохраняет флаг во второй справа ячейке.

		>- a
		>  0
		>  0

		<- a
		<  0
		<  0

		>- x - неважно
		>  0
		>  0

		<- a, если не выполнился, иначе x
		<  0
		<  1, если выполнился, иначе 0
	"""

	return "[", ">>+<]>[<]<"

@instruction
def if_save_back_flag_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется. Сохраняет флаг во второй слева ячейке.

		>  0
		>  0
		>- a

		<  0
		<  0
		<- a

		>  0
		>  0
		>- x - неважно

		<  1, если выполнился, иначе 0
		<  0
		<- a, если не выполнился, иначе x
	"""

	return "[", "<<+>]<[>]>"

@instruction
def else_block(root):
	"""
		Условный блок, выполняется, если предыдущая команда "IF_SAVE_FLAG" не выполнилась.

		>- x - неважно
		>  y - неважно
		>  флаг

		<- x
		<  y
		<  0

		>- z - неважно
		>  w - неважно
		>  0

		<- x, если не выполнился, иначе z
		<  y, если не выполнился, иначе w
		<  0
	"""

	return ">>-[+<<", ">>]<<"

@instruction
def else_back_block(root):
	"""
		Условный блок, выполняется, если предыдущая команда "IF_SAVE_BACK_FLAG" не выполнилась.

		>  флаг
		>  y - неважно
		>- x - неважно

		<  0
		<  y
		<- x

		>  0
		>  w - неважно
		>- z - неважно

		<  0
		<  y, если не выполнился, иначе w
		<- x, если не выполнился, иначе z
	"""

	return "<<-[+>>", "<<]>>"

@instruction
def unless_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Если нет, то она зануляется.

		>- a
		>  0

		<- 0
		<  0

		>- x - неважно
		>  0

		<- 0, если не выполнился, иначе x
		<  0
	"""

	return "[[-]>+<]>-[+<", ">]<"

@instruction
def unless_back_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Если нет, то она зануляется.

		>  0
		>- a

		<  0
		<- 0

		>  0
		>- x - неважно

		<  0
		<- 0, если не выполнился, иначе x
	"""

	return "[[-]<+>]<-[+>", "<]>"

@instruction
def bool_unless_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Если нет, то она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "-[+", "]"

@instruction
def unless_save_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Её значение сохраняется.

		>- a
		>  0
		>  0

		<- 0
		<  0
		<  0

		>- x - неважно
		>  y - неважно
		>  0

		<- a, если не выолнился, иначе x
		<  0, если не выполнился, иначе y
		<  0
	"""

	return "[>>+<]>[<]>-[+<<", ">>]<<"

@instruction
def unless_save_back_block(root):
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Её значение сохраняется.

		>  0
		>  0
		>- a

		<  0
		<  0
		<- 0

		>  0
		>  y - неважно
		>- x - неважно

		<  0
		<  0, если не выполнился, иначе y
		<- a, если не выолнился, иначе x
	"""

	return "[<<+>]<[>]<-[+>>", "<<]>>"

@instruction
def for_block(root):
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём. После каждой итерации она уменьшается на 1.

		>- a

		<- a

		>- x - неважно

		<- 0
	"""

	return "[", "-]"

@instruction
def for_l_block(root):
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём. Перед каждой итерацией она уменьшается на 1.

		>- a

		<- a - 1, если первая итерация, иначе x - 1

		>- x - неважно

		<- 0
	"""

	return "[-", "]"

@instruction
def while_block(root):
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём.

		>- a

		<- a, если первая итерация, иначе x

		>- x - неважно

		<- 0
	"""

	return "[", "]"

@instruction
def forever_block(root):
	"""
		Бесконечный цикл.

		>- 0

		<- 0

		>- 0

		<- 0
	"""

	return "+[-", "+]"

# Команды с несколькими вводами

@instruction
def add_to_command(root, destination):
	"""
		Складывает данную ячейку с указанной.

		>- a
		>  ...
		>  b

		<- 0
		<  ...
		<  b + a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[-" + visit(destination, "+") + "]"

@instruction
def subtract_to_command(root, destination):
	"""
		Отнимает данную ячейку от указанной.

		>- a
		>  ...
		>  b

		<- 0
		<  ...
		<  b - a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[-" + visit(destination, "-") + "]"

@instruction
def add_to_save_command(root, destination, buffer):
	"""
		Складывает с указанной ячейкой данную, сохраняя её значение с помощью временной.

		>- a
		>  ...
		>  b
		>  ...
		>  0

		<- a
		<  ...
		<  b + a
		<  ...
		<  0

		Сдвиги не должны быть нулевыми или одинаковыми.
	"""

	return "[-" + visit(buffer, "+") + visit(destination, "+") +"]" + visit(buffer, "[-" + visit(-buffer, "+") + "]")

@instruction
def subtract_to_save_command(root, destination, buffer):
	"""
		Отнимает от указанной ячейки данную, сохраняя её значение с помощью временной.

		>- a
		>  ...
		>  b
		>  ...
		>  0

		<- a
		<  ...
		<  b - a
		<  ...
		<  0

		Сдвиги не должны быть нулевыми или одинаковыми.
	"""

	return "[-" + visit(buffer, "+") + visit(destination, "-") +"]" + visit(buffer, "[-" + visit(-buffer, "+") + "]")

@instruction
def not_to_command(root, destination):
	"""
		Обаращает значение данной ячейки.

		>- a
		>  ...
		>  0

		<- 0
		<  ...
		<  !a

		Сдвиг может быть любым, но не нулевым.
	"""

	return visit(destination, "+") + "[[-]" + visit(destination, "-") + "]"

@instruction
def bool_not_to_command(root, destination):
	"""
		Обаращает значение данной ячейки.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a
		>  ...
		>  0

		<- 0
		<  ...
		<  !a

		Сдвиг может быть любым, но не нулевым.
	"""

	return visit(destination, "+") + "[-" + visit(destination, "-") + "]"

@instruction
def bool_to_command(root, destination):
	"""
		Конвертирует данную ячейку в булево значение.

		>- a
		> ...
		>  0

		<- 0
		< ...
		<  !!a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[[-]" + visit(destination, "+") + "]"

@instruction
def not_and_to_command(root, destination):
	"""
		Выполняет логическое и с заданной ячейкой и обращённой данной.

		>- a
		>  ...
		>  b

		<- a
		<  ...
		<  b & !a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[[-]" + visit(destination, "[-]") + "]"

@instruction
def not_and_to_save_command(root, destination, buffer):
	"""
		Выполняет логическое и с заданной ячейкой и обращённой данной, сохраняя её значение.

		>- a
		>  ...
		>  b
		>  ...
		>  0

		<- a
		<  ...
		<  b & !a
		<  ...
		<  0

		Сдвиги не должны быть нулевыми или одинаковыми.
	"""

	return "[-" + visit(buffer, "+") + visit(destination, "[-]") + "]" + visit(buffer, "[-" + visit(-buffer, "+") + "]")

@instruction
def split_byte_command(root):
	"""
		Разделяет байт на старшую и младшую половины.

		>- 0
		>  0
		>  a
		>  0
		>  0
		>  0
		>  0

		<- 0
		<  0
		<  0
		<  0
		<  a & 0xf
		<  0
		<  a >> 4
	"""

	return ">>[<<++++++++++++++++>>[<<[->>-<]>]>[>]<<<[>>>>++++++++++++++++>>-<<<<<<[->>>>-<<<<]]>>>>>>+<<<<]<<"

@instruction
def hex_command(root):
	"""
		Конвертирует половину байта в строчную шестнадцатеричную цифру.

		>- 0
		>  0
		>  a
		>  0

		<- цифра
		<  0
		<  0
		<  0
	"""

	return (
		">>[->+<<<+>>]<+++++++++[>>[-<]<[>]<-]>>[[-]<<<+++++++++++++++++++++++++++++++++++++++>>>]" +
		"<<<++++++++++++++++++++++++++++++++++++++++++++++++"
	)

# Сетевые команды

@instruction
def network_accept_command(root):
	"""
		Принимает соединение.

		>- 0

		<- 0, если успешно, иначе 1
	"""

	return ".,"

@instruction
def network_recv_command(root):
	"""
		Принимает данные.

		>- l - требуемая длина данных
		>  0

		<- 0, если успешно, иначе 1
		<  0

		Если вызов успешен, после него надо прочитать 1 байт длины и сами данные. Если длина будет 0, то соединение больше ничего не пошлёт.
	"""

	return ">+.-<.,"

@instruction
def network_send_command(root):
	"""
		Отправляет данные.

		>- l - длина
		>  0

		<- l
		<  0

		После этого надо вывести l байтов и прочитать 1 байт результата: 0, если успешно, иначе 1. В случае успеха надо прочитать ещё один байт - длину отправленного, она может быть меньше l.
	"""

	return ">++.--<."

@instruction
def network_close_command(root):
	"""
		Закрывает соединение.

		>- 0

		<- 0, если успешно, иначе 1
	"""

	return "+++.,"

# Линия

"""
	Последовательность ячеек со значением 1, по краям которой нули.
"""

@instruction
def line_create_command(root, length):
	"Создаёт линию указанной длины, которая не может быть меньше 2"

	length -= 2

	result = ">"

	while length != 0:
		part = min(length, 255)
		length -= part
		result += increase(part) + "[[->+<]+>-]"

	return result

@instruction
def line_go_start_command(root):
	"Переходит к началу линии"

	return "<[<]"

@instruction
def line_go_end_command(root):
	"Переходит к концу линии"

	return ">[>]"

@instruction
def line_clear_command(root):
	"Очищает линию. Указатель должен быть на конце"

	return "<[-<]"

# Массив

"""
	Это структура данных:

	0
	0

	За которыми следуют элементы:

	1
	d - байт данных

	А за ними ещё:

	0
	0

	Например:

	0
	0
	1
	63
	1
	33
	0
	0

	Такую структуру удобно дополнять: с помощью цикла можно проехаться до конца массива и дописать ещё элемент. Или удалить последний.
"""

@instruction
def array_create_command(root, length):
	"Создаёт пустой массив указанной длины"

	result = ">"

	while length != 0:
		part = min(length, 255)
		length -= part
		result += increase(part) + "[>+<[->>+<<]>>-]"

	return result + ">"

@instruction
def array_set_command(root, string):
	"Создаёт массив из указанных байтов. Указатель остаётся на начале"

	if type(string) is str:
		string = string.encode()

	base = list(sorted(string))[len(string) // 2]

	return (
		">>" + "+>>" * len(string) + ">" + increase(base) + "[-<<<[>+<<<]>>[>>]>]" +
		"<<" + "<<".join(increase(i - base) for i in reversed(string)) + "<<<"
	)

@instruction
def array_go_end_command(root):
	"Перемещается в конец массива"

	return ">>[>>]"

@instruction
def array_go_start_command(root):
	"Перемещается в начало массива"

	return "<<[<<]"

@instruction
def array_clear_command(root):
	"Очищает массив. Указатель должен быть на конце"

	return "<<[->[-]<<<]"

@instruction
def array_foreach_block(root):
	"Цикл по каждому элементу массива. Указатель остаётся на конце"

	return ">>[", ">>]"

@instruction
def array_foreach_back_block(root):
	"Цикл по каждому элементу массива в обратном порядке. Указатель остаётся на начале"

	return "<<[", "<<]"

# Пароль

@instruction
def check_password_command(root, string):
	"""
		Сравнивает массив с указанным паролем, удаляя его.

		>- 0
		>  массив

		<- 0
		<  0
		<  0
		<  1, если совпал, иначе 0
		<  нули
	"""

	if type(string) is str:
		string = string.encode()

	return ">>~>>" + ">>".join("-" * i for i in string) + "~>+<<[>[[-]<->]>-[+<<[-]>>]<<<<]<"

# База данных

"""
	База хранится в памяти, как последовательность массивов по 16 байтов длиной. После каждого массива:

	>  0, если это последний массив, иначе 1
	>  0, если это первый массив, иначе 1
	>  0, если в данном массиве начинается пост, иначе 1
	>  x1 - номер поста в этом массиве, либо ноль. Число хранится, как 3 байта, по одной десятичной цифре в каждом, старшая спереди. Цифры хранятся в виде значений от 0 до 9
	>  x2
	>  x3
	>  0, если этот массив не надо отправлять в сеть, иначе 1
	>- 0
	>  0
	>  0
	>  0
	>  0

	Перед базой данных должно быть 5 нулей.

	В результате получается массив массивов, по которому тоже можно перемещаться назад-вперёд.
"""

@instruction
def database_load_command(root, path):
	"Загружает базу данных из файла в память, указатель остаётся на последнем чанке"

	path = os.path.join(root, path)

	with open(path, "rb") as file:
		data = file.read()

	result = ">>>>>"

	for i in range(0, len(data), 16):
		chunk = data[i: i + 16]
		chunk += b"\n" * (16 - len(chunk))

		first = i == 0
		last = i >= len(data) - 16

		result += (
			array_set_command(root, chunk) + ">>[>>]>>" +
			("" if last else "+") + ">" + ("" if first else "+") + ">+>>>>+>>>>>>"
		)

	return result + "<<<<<"

@instruction
def database_go_next_command(root):
	"Переходит к следующему чанку"

	return ">>>>>" + array_go_end_command(root) + ">>>>>>>>>"

@instruction
def database_go_back_command(root):
	"Переходит к предыдущему чанку"

	return "<<<<<<<<<" + array_go_start_command(root) + "<<<<<"

@instruction
def database_go_end_command(root):
	"Переходит к последнему чанку"

	return "<<<<<<<[>>>>>>>" + database_go_next_command(root) + "<<<<<<<]>>>>>>>"

@instruction
def database_go_start_command(root):
	"Переходит к первому чанку"

	return "<<<<<<[>>>>>>" + database_go_back_command(root) + "<<<<<<]>>>>>>"

@instruction
def database_extend_chunk_command(root, string):
	"""
		Добавляет в чанк заданные байты. В нём должно быть достаточно для места, чтобы их вместить.

		См. "lib/append-database.txt".
	"""

	if type(string) is str:
		string = string.encode()

	result = "<<<<<<<<<[<<]"

	for i in string:
		result += "+>" + increase(i) + ">-"

	result += ">>[>>]>>>>>>>" + increase(-len(string))

	return result

@instruction
def database_foreach_block(root):
	"""
		Цикл по каждому чанку. Указатель остаётся на последнем.

		>- 0
		>  0

		<- 0
		<  0

		>- 0
		>  0

		<- 0
		<  0
	"""

	return (
		"+[-",
		"<<<<<<<[>>>>>>>" + database_go_next_command(root) + "+<<<<<<<[->>>>>>>>+<<<<<<<<]]>>>>>>>>[-<<<<<<<<+>>>>>>>>]<]"
	)

# Препроцессор

import json.decoder

JSON_decoder = json.decoder.JSONDecoder()

def parse_instruction(instruction):
	name, tail = (instruction.split(maxsplit = 1) + [""])[: 2]
	arguments = []
	shift = 0

	tail = tail.lstrip()

	while tail != "":
		if tail.startswith("<>"):
			shift = int(tail[2: ])
			tail = ""
		else:
			argument, length = JSON_decoder.raw_decode(tail)
			tail = tail[length: ].lstrip()

			arguments.append(argument)

	return name, arguments, shift

def preprocess_part(code, root, stack):
	result = ""

	for line in code.split("\n"):
		line = line.split("//")[0].strip()

		if line.startswith("#"):
			instruction = line[1: ]

			if instruction == "END":
				code, shift = stack.pop()
				result += go(shift) + code
			else:
				name, arguments, shift = parse_instruction(instruction)

				result += go(shift)

				if name == "INCLUDE":
					path = os.path.join(root, arguments[0])

					with open(path) as file:
						code = file.read()

					result += preprocess_part(code, os.path.split(path)[0], stack)
				elif name in blocks:
					start, end = blocks[name](root, *arguments)

					stack.append((end, shift))

					result += start
				elif name in commands:
					result += commands[name](root, *arguments)
				else:
					raise Exception("Неизвестная команда")

			result += go(-shift)
		else:
			result += line

	return result

def preprocess(code, root = "."):
	stack = []

	result = preprocess_part(code, root, stack)

	if len(stack) != 0:
		raise Exception("Не хватает \"END`")

	return result

import itertools

def format(code):
	def reorder(code):
		shift = 0
		differences = {}

		for i in code:
			if i == "-":
				differences[shift] = differences.get(shift, 0) - 1
			elif i == "+":
				differences[shift] = differences.get(shift, 0) + 1
			elif i == "<":
				shift -= 1
			else:
				shift += 1

		left_moves = list(sorted((i for i in differences if i < 0), reverse = True))
		right_moves = list(sorted(i for i in differences if i >= 0))

		result = ""
		pointer = 0

		def encode(moves):
			nonlocal result, pointer

			for i in moves:
				difference = differences[i] % 256

				result += go(i - pointer)
				result += increase(difference if difference <= 128 else -(256 - difference))
				pointer = i

		if shift > 0:
			encode(left_moves)
			encode(right_moves)
		else:
			encode(right_moves)
			encode(left_moves)

		result += go(shift - pointer)
		pointer = shift

		return result

	reordered = ""
	fragment = ""

	for i in code:
		if i in "-+><":
			fragment += i
		elif i in "[],.~":
			reordered += reorder(fragment) + i
			fragment = ""

	result = ""

	for i, j in zip(reordered.split("~"), itertools.count()):
		if j % 2 == 0:
			result += "\n".join(i[k: k + 80] for k in range(0, len(i), 80)) + "\n"
		else:
			result += "\nПароль:\n" + i.replace(">>", "\n>>") + "\n\n"

	return result

if __name__ == "__main__":
	import sys

	with open(sys.argv[1]) as file:
		sys.stdout.write(format(preprocess(file.read())))
