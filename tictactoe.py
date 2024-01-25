from enum import Enum
import channel_client
import pygame

line_color = (0, 0, 0)

ROOM_ID=42

class Tile(Enum):
    O = "O"
    X = "X"
    EMPTY = ""
    
class TicTacToeNetwork():
    def __init__(self, game, room_id):
        self.tictactoe = game
        self.socket = channel_client.connect_socket("ws://localhost:4000/tictactoe/websocket?vsn=2.0.0")
        self.lobby = F"room:{room_id}"
        channel_client.join_lobby(self.socket, self.lobby)
        
    def play(self, i, j, char):
        channel_client.send_message(self.socket, self.lobby, "play", {"i" : i, "j" : j, "char" : char})
        
    def check_play(self):
        message = channel_client.get_message(self.socket)
        if message is not None:
            type, payload = message[3], message[4]
            if type == "play":
                if payload["char"] == "O":
                    payload["char"] = Tile.O
                if payload["char"] == "X":
                    payload["char"] = Tile.X
                self.tictactoe.play_index(payload["i"], payload["j"], payload["char"])
                
    def disconnect(self):
        channel_client.disconnect_socket(self.socket)

class TicTacToe:
    def __init__(self, player_id, width, height):
        self.player = Tile.O
        self.board = [[Tile.EMPTY for _ in range(3)] for _ in range(3)]
        self.player_won = None
        self.network = TicTacToeNetwork(self, ROOM_ID)
        self.player_id = player_id
        self.width = width
        self.height = height
        
    def quit(self):
        self.network.disconnect()
        
    def play(self, pos):
        tile_width = self.width / 3
        tile_height = self.height / 3
        (x, y) = pos
        i = int(y // tile_height)
        j = int(x // tile_width)
        
        if self.player_id == None or self.player_id == self.player:
            self.play_index(i, j, self.player)

    def play_index(self, i, j, char):
        if self.board[i][j] == Tile.EMPTY and char == self.player:
            self.board[i][j] = char
            self.network.play(i, j, self.player.value)
            self.player = Tile.X if self.player == Tile.O else Tile.O

    def check_won(self):
        if self.player_won is not None:
            return True
        # full row
        for i in range(3):
            wonned = True
            for j in range(1, 3):
                if (
                    self.board[i][j] == Tile.EMPTY
                    or self.board[i][j] != self.board[i][j - 1]
                ):
                    wonned = False
                    break
            if wonned:
                self.player_won = self.board[i][0]
                return True

        # full column
        for j in range(3):
            wonned = True
            for i in range(1, 3):
                if (
                    self.board[i][j] == Tile.EMPTY
                    or self.board[i][j] != self.board[i - 1][j]
                ):
                    wonned = False
                    break
            if wonned:
                self.player_won = self.board[0][j]
                return True

        # main diagonal
        wonned = True
        for i in range(1, 3):
            if (
                self.board[i][i] == Tile.EMPTY
                or self.board[i][i] != self.board[i - 1][i - 1]
            ):
                wonned = False
                break
        if wonned:
            self.player_won = self.board[0][0]
            return True

        # reversed diagonal
        wonned = True
        for i in range(1, 3):
            if (
                self.board[i][2 - i] == Tile.EMPTY
                or self.board[i][2 - i] != self.board[i - 1][2 - i + 1]
            ):
                wonned = False
                break
        if wonned:
            self.player_won = self.board[0][2]
            return True

        return False
    
    def update(self):
        self.network.check_play()
        self.check_won()

    def display(self, screen):
        tile_width = self.width / 3
        tile_height = self.height / 3
        for i in range(1, 3):
            pygame.draw.line(
                screen,
                line_color,
                (0, tile_height * i),
                (self.width, tile_height * i),
                width=5,
            )
        for i in range(1, 3):
            pygame.draw.line(
                screen,
                line_color,
                (tile_width * i, 0),
                (tile_width * i, self.height),
                width=5,
            )

        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        for i in range(3):
            for j in range(3):
                char = self.board[i][j].value
                text = font.render(char, 1, (10, 10, 10))
                textpos = text.get_rect(center=((j + 0.5) * tile_width, (i + 0.5) * tile_height))
                screen.blit(text, textpos)
                
        # if won
        if self.check_won():
            font = pygame.font.Font(pygame.font.get_default_font(), 36)
            text = font.render(
                f"Player {self.player_won.value} has won", 1, (10, 10, 10)
            )
            temp_surface = pygame.Surface(text.get_size())
            temp_surface.fill((192, 192, 192))
            textpos = text.get_rect(center=(self.width / 2, self.height / 3))
            temp_surface.blit(text, (0, 0))
            screen.blit(temp_surface, textpos)
