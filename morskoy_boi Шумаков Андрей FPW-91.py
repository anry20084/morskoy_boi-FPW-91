from random import randint  # импорт модуля случайных генераций ходов игрока-компьютера

import time  # импорт модуля времени

class Dot: # класс точек
    def __init__(self, x, y):  # задание координат точек
        self.x = x
        self.y = y
    
    def __eq__(self, other):  # сравнение точек с точками корабля
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):  #  вывод точек в консоль
        return f"({self.x}, {self.y})"


class BoardException(Exception):  # родительский класс исключений
    pass

class BoardOutException(BoardException): # класс исключений при выстреле за границы доски
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException): # класс исключений при повторном выстреле в точку
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException): # исключение для вывода короюлей на доску
    pass

class Ship:  # класс корабля
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    
    @property
    def dots(self):  # метод отрисовки корабля на игровом поле
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot): #  метод проверки попадания в корабль
        return shot in self.dots

class Board:  #  класс игрового поля
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0  # подсчет количества пораженных кораблей
        
        self.field = [ ["O"]*size for _ in range(size) ]  # отрисовка игрового поля
        
        self.busy = []  # хранение занятых точек
        self.ships = []  # список кораблей доски
    
    def add_ship(self, ship):  #  метод добавления кораблей на игровое поле
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:  #  если точка занята или вне поля, то вывод исключения
                raise BoardWrongShipException()
        for d in ship.dots:  # добавление координат точек корабля
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):  # метод определения границ корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0 , 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "-"
                    self.busy.append(cur)
    
    def __str__(self):  # метод отображения доски
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:  # скрытие кораблей противника на доске
            res = res.replace("■", "O")
        return res
    
    def out(self, d):  # определение точки в границах доски
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):  # метод выстрелов
        if self.out(d):  # проверка выстрела на границы поля
            raise BoardOutException()
        
        if d in self.busy:  # проверка выстрела на свободную клетку
            raise BoardUsedException()
        
        self.busy.append(d)  # если клетка свободна, то добавляем в список
        
        for ship in self.ships:  # цикл проверки точек кораблей
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True
        
        self.field[d.x][d.y] = "T"
        print("Промах!")
        return False
    
    def begin(self):  # метод очистки списка занятых точек перед началом игры
        self.busy = []

class Player:  # класс игрока
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):  # метод выполнения выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class Comp(Player):  # класс игрока-компьютера
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))

        time.sleep(5)  # задержка 5 секунд для компьютера "чтобы подумать"
        print(f"Ход компьютера: {d.x+1} {d.y+1}")

        return d

class User(Player):  # класс игрока-человека
    def ask(self):
        while True:
            cords = input("Сделайте ход: ").split()
            
            if len(cords) != 2:  # проверка хода на длину координат
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):  # проверка координат на цифры
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

class Game:  # класс Игра
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.comp = Comp(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):  # метод создания доски
        board = None
        while board is None:
            board = self.try_board()
        return board
    
    def try_board(self):  # метод добавления кораблей на доску
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0

        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))

                try:
                    board.add_ship(ship)
                    break

                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def merge_boards(first, second):
        first_lines = first.split("\n")
        second_lines = second.split("\n")

        result = ""
        for i in range(len(first_lines)):
            result_line = f"{first_lines[i]:30}   ||      {second_lines[i]} \n"
            result += result_line

        return result

    def greet(self):  # приветствие и правила игры
        print('             -----------------------------------\n'
              '               Приветствую в игре Морской бой!\n'
              '             -----------------------------------\n'
              '                        Правила игры \n'
              '                 Для того, чтобы сделать ход \n'
              '             необходимо ввести 2 координаты: x y\n'
              '                      х - номер строки\n'
              '                     у - номер столбца\n'
              '                    первым ходит - игрок\n'
              '                   затем ходит - компьютер\n'
              '         попадание в корабль обозначается символом - "Х"\n'
              '             промах обозначается символом - "T"\n'
              '    клетки вокруг подбитого корабля обозначаются символом - "-"\n')
        print("-"*68)

    def print_boards(self):
        print()
        user_board = "Доска игрока:\n" + str(self.us.board)
        comp_board = "Доска компьютера:\n" + str(self.comp.board)
        print(Game.merge_boards(user_board, comp_board))


    def loop(self):  # игровой цикл
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-"*68)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-"*68)
                print("Ходит компьютер!")
                repeat = self.comp.move()

            if repeat:
                num -= 1
            
            if self.comp.board.count == len(self.comp.board.ships):
                self.print_boards()
                print("-"*68)
                print("Игрок выиграл!")
                break
            
            if self.us.board.count == len(self.us.board.ships):
                self.print_boards()
                print("-"*68)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()