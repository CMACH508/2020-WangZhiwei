
import re

def unparse_pygtp_coords(c):
    if c is None:
        return PASS
    return c[1] + 1, 19 - c[0]

def parse_pygtp_coords(vertex):
    'Interprets coords. (1, 1) is bottom left; (1, 9) is top left.'
    if vertex in (PASS, RESIGN):
        return None
    return 19 - vertex[1], vertex[0] - 1

def pre_engine(s):
    s = re.sub("[^\t\n -~]", "", s)
    s = s.split("#")[0]
    s = s.replace("\t", " ")
    return s


def pre_controller(s):
    s = re.sub("[^\t\n -~]", "", s)
    s = s.replace("\t", " ")
    return s


def gtp_boolean(b):
    return "true" if b else "false"


def gtp_list(l):
    return "\n".join(l)


def gtp_color(color):
    # an arbitrary choice amongst a number of possibilities
    return {BLACK: "B", WHITE: "W"}[color]


def gtp_vertex(x, y):
    if x == 9 and y == 9:
        return "resign"
    else:
        return "{}{}".format("ABCDEFGHIJKLMNOPQRSTYVWYZ"[y], x + 1)


def gtp_move(color, x, y):
    return " ".join([gtp_vertex(x, y)])


def parse_message(message):
    message = pre_engine(message).strip()
    first, rest = (message.split(" ", 1) + [None])[:2]
    if first.isdigit():
        message_id = int(first)
        if rest is not None:
            command, arguments = (rest.split(" ", 1) + [None])[:2]
        else:
            command, arguments = None, None
    else:
        message_id = None
        command, arguments = first, rest

    return message_id, command, arguments


WHITE = -1
BLACK = +1
EMPTY = 0

PASS = (0, 0)
RESIGN = "resign"


def parse_color(color):
    if color.lower() in ["b", "black"]:
        return BLACK
    elif color.lower() in ["w", "white"]:
        return WHITE
    else:
        return False


def parse_vertex(vertex_string):
    if vertex_string is None:
        return False
    elif vertex_string.lower() == "pass":
        return PASS
    elif vertex_string.lower() == "resign":
        return 9, 9
    elif len(vertex_string) > 1:
        y = "abcdefghijklmnopqrstuvwxyz".find(vertex_string[0].lower())
        if y == -1:
            return False
        if vertex_string[1:].isdigit():
            x = int(vertex_string[1:])
        else:
            return False
    else:
        return False
    return x - 1, y


def parse_move(move_string):
    color_string, vertex_string = (move_string.split(" ") + [None])[:2]
    color = parse_color(color_string)
    if color is False:
        return False
    vertex = parse_vertex(vertex_string)
    if vertex is False:
        return False

    return color, vertex


MIN_BOARD_SIZE = 7
MAX_BOARD_SIZE = 19


def format_success(message_id, response=None):
    if response is None:
        response = ""
    else:
        response = " {}".format(response)
    if message_id:
        return "={}{}\n\n".format(message_id, response)
    else:
        return "={}\n\n".format(response)


def format_error(message_id, response):
    if response:
        response = " {}".format(response)
    if message_id:
        return "?{}{}\n\n".format(message_id, response)
    else:
        return "?{}\n\n".format(response)


class Engine(object):

    def __init__(self, game_obj, name="gtp (python library)", version="0.2"):

        self.size = 9
        self.komi = 6.5

        self._game = game_obj
        self._game.clear()

        self._name = name
        self._version = version

        self.disconnect = False

        self.known_commands = [
            field[4:] for field in dir(self) if field.startswith("cmd_")]

    def send(self, message):
        message_id, command, arguments = parse_message(message)
        if command in self.known_commands:
            try:
                return getattr(self, "cmd_" + command)(arguments)
                '''return format_success(
                    message_id, getattr(self, "cmd_" + command)(arguments))'''
            except ValueError as exception:
                return format_error(message_id, exception.args[0])
        else:
            return format_error(message_id, "unknown command")

    def vertex_in_range(self, vertex):
        if vertex == PASS:
            return True
        if 1 <= vertex[0] <= self.size and 1 <= vertex[1] <= self.size:
            return True
        else:
            return False

    # commands

    def cmd_protocol_version(self, arguments):
        return 2

    def cmd_showboard(self, arguments):
        return "haha"
        return self._game.board.__repr__()

    def cmd_name(self, arguments):
        return self._name

    def cmd_version(self, arguments):
        return self._version

    def cmd_known_command(self, arguments):
        return gtp_boolean(arguments in self.known_commands)

    def cmd_list_commands(self, arguments):
        return gtp_list(self.known_commands)

    def cmd_quit(self, arguments):
        self.disconnect = True
        return ""

    def cmd_boardsize(self, arguments):
        return ""
        '''if arguments.isdigit():
            size = int(arguments)
            if MIN_BOARD_SIZE <= size <= MAX_BOARD_SIZE:
                self.size = size
                self._game.set_size(size)
            else:
                raise ValueError("unacceptable size")
        else:
            raise ValueError("non digit size")'''

    def cmd_clear_board(self, arguments):
        self._game.clear()

    def cmd_komi(self, arguments):
        try:
            komi = float(arguments)
            self.komi = komi

        except ValueError:
            raise ValueError("syntax error")

    def cmd_play(self, arguments):
        color, move = parse_move(arguments)
        x, y = move
        #print("play", x, y)
        #print("vertex: ", vertex)
        #if self._game.make_move(color, vertex):
        if self._game.make_move(x, y):
            return ""
            #return gtp_move(color, x, y)
        else:
            return "Illegal move"
        #raise ValueError("illegal move")

    def cmd_genmove(self, arguments):
        c = parse_color(arguments)
        if c:
            x, y = self._game.get_move()
            #print("gen", x, y)
            self._game.make_move(x, y)
            #return gtp_vertex(move)
            return gtp_vertex(x, y)
        else:
            raise ValueError("unknown player: {}".format(arguments))

    def cmd_final_score(self, arguments):
        over, res = self._game.is_game_over()
        if over:
            if res > 0:
                return "B+"
            else:
                return "W+"
        return "Not over"

    def cmd_result(self, arguments):
        over, res = self._game.show_result()
        if over:
            return res
        return "Not over"



class MinimalGame(object):

    def __init__(self, size=19, komi=6.5):
        self.size = size
        self.komi = 6.5
        self.board = [EMPTY] * (self.size * self.size)

    def _flatten(self, vertex):
        (x, y) = vertex
        return (x - 1) * self.size + (y - 1)

    def clear(self):
        self.board = [EMPTY] * (self.size * self.size)

    def make_move(self, color, vertex):
        # no legality check other than the space being empty..
        # no side-effects beyond placing the stone..
        if vertex == PASS:
            return True  # noop
        idx = self._flatten(vertex)
        if self.board[idx] == EMPTY:
            self.board[idx] = color
            return True
        else:
            return False

    def set_size(self, n):
        self.size = n
        self.clear()

    def set_komi(self, k):
        self.komi = k

    def get_move(self, color):
        # pass every time. At least it's legal
        return 0, 0

