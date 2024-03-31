import random
import time


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # переопределение вывода для удобства отслеживания точек
    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


# Все классы исключений:
class BoardException(Exception):
    pass


class BoardShotOutException(BoardException):
    def __str__(self):
        return "Эта координата находится за пределами доски!"


class BoardUsedCellException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли :)"


class BoardWrongPlaceException(BoardException):
    pass


class Ship:
    def __init__(self, init_dot, length, direction):
        self.init_dot = init_dot
        self.length = length
        self.direction = direction
        self.lives = length

    # собираем все точки корабля
    @property
    def dots(self):
        ship_coords = []
        for i in range(self.length):
            x_coord = self.init_dot.x
            y_coord = self.init_dot.y

            # если направление горизонтальное - увеличиваем координату x, иначе - y и записываем их в массив данных
            if self.direction == 'vertical':
                x_coord += i

            elif self.direction == 'horizontal':
                y_coord += i

            ship_coords.append(Dot(x_coord, y_coord))
        return ship_coords



class Board:
    def __init__(self, is_hidden=False, size=6):
        self.is_hidden = is_hidden
        self.count = 0
        self.size = size

        # создание двумерной матрицы и инициализация элементов в символ O - пустые клетки
        self.field = [["O"] * self.size for _ in range(self.size)]

        self.filled = []
        self.ships = []

    #Печатает доску
    def __str__(self):
        res = ""
        res += "  | " + " | ".join(str(i + 1) for i in range(self.size)) + " |"

        for i, row in enumerate(self.field):
            res += "\n" + "--+" + "---+" * self.size  # разделитель
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        # скрытие кораблей на доске, если это доска ИИ - корабли превращаются в О и их не видно
        if self.is_hidden:
            res = res.replace("■", "O")
        return res

    # Проверяем точку, не выходит ли она за границы поля
    def is_out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, show_contour_dots=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                coord = Dot(dot.x + dx, dot.y + dy)
                if not (self.is_out(coord)) and coord not in self.filled:
                    if show_contour_dots:
                        self.field[coord.x][coord.y] = "."
                    self.filled.append(coord)

    def add_ship(self, ship, max_attempts=3000):
        attempts = 0
        while attempts < max_attempts:
            for dot in ship.dots:
                # Проверка на выход корабля за пределы поля или присутствие в списке занятых клеток
                if self.is_out(dot) or dot in self.filled:
                    attempts += 1
                    break

            else:
                # Если корабль успешно добавлен, выходим из цикла
                break

        if attempts == max_attempts:
            raise BoardWrongPlaceException()

        # Закрашивание точки корабля, добавление его в список занятых клеток
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.filled.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
    #Проверки на выход за пределы доски и повторный выстрел:
        if self.is_out(dot):
            raise BoardShotOutException()

        if dot in self.filled:
            raise BoardUsedCellException()

        #Добавляем точку в список "использованных" клеток
        self.filled.append(dot)

        #Механика выстрела:
        for ship in self.ships:
            if dot in ship.dots:
                #Если точка находится в списке точек корабля, кол-во жизней уменьшаем на 1
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                #Если не осталось жизней, счет + 1, выводим контур
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, show_contour_dots=True)
                    print("Убит!")
                    return True
                else:
                    print("Ранен!")
                    return True
        #Если промах:
        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    #Для начала игры очищаем список точек
    def begin(self):
        self.filled = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target_dot = self.ask()
                #Проверяем, нужно ли повторить ход после выстрела, принимает True или False
                repeat_move = self.enemy.shot(target_dot)
                return repeat_move
            #Если при вводе, или при выстреле, или еще где-то возникает какая-то из ошибок, выводим ее
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        print("Ваш ход")
        while True:
            try:
                x = int(input("Введите номер строки: "))
            except ValueError:
                print("Введите число!")
                x = int(input("Введите номер строки: "))

            try:
                y = int(input("Введите номер столбца: "))
            except ValueError:
                print("Введите число!")
                y = int(input("Введите номер столбца: "))

            return Dot(x - 1, y - 1)

class AI(Player):
    def ask(self):
        dot = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f'Компьютер думает...')
        time.sleep(2)
        print(f'Ход компьютера: {dot.x + 1, dot.y + 1}!')
        return dot


class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.get_some_board()
        ai_board = self.get_some_board()

        ai_board.is_hidden = True

        # Определяем игроков класса Player
        self.ai = AI(ai_board, player_board)
        self.human = User(player_board, ai_board)


    def create_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        attempts = 0

        while attempts <= 300:
            board = Board()
            try:
                for l in lens:
                    while True:
                        ship = Ship(Dot(random.randint(0, self.size - 1), random.randint(0, self.size - 1)), l,
                                    random.choice(['vertical', 'horizontal']))
                        try:
                            board.add_ship(ship)
                            break
                        except BoardWrongPlaceException:
                            pass

                board.begin()
                return board

            except BoardWrongPlaceException:
                attempts += 1

        return None

    def get_some_board(self):
        print("Генерация досок...")
        while True:
            board = self.create_board()
            if board is not None:
                return board

    def game_process(self):
        move_marker = 0
        while True:
            print('Доскa игрока: ')
            print(self.human.board)
            print("-" * 25)
            print('Доскa ИИ: ')
            print(self.ai.board)
            print("-" * 25)

#move_marker определяет, чей ход и зависит от возвращенного значения метода shot (repeat - True или False)
            if move_marker % 2 == 0:
                print("Ходит игрок!")
                repeat = self.human.move()
            else:
                print("Ходит ИИ!")
                repeat = self.ai.move()
            if repeat:
                move_marker -= 1

            if self.ai.board.count == 7:
                print("-" * 25)
                print("Игрок выиграл!")
                print(self.ai.board)
                break

            if self.human.board.count == 7:
                print("-" * 25)
                print("ИИ выиграл!")
                print(self.human.board)
                break
            move_marker += 1

    def start_game(self):
        print("Добро пожаловать в игру 'Морской бой!'")
        self.game_process()

g = Game()
g.start_game()