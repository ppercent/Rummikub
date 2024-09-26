from random import shuffle, randint
from rummikub_bot import RummikubBot
import sys


class Tile:
    def __init__(self, number=None, color=None, is_joker=False) -> None:
        self.number = number if not is_joker else None
        self.color = color if not is_joker else None
        self.is_joker = is_joker
    
    def clear_joker(self) -> None:
        """
        Clear the number and color attributes of a joker tile.

        This method is called when a player replaces the joker with its corresponding tile, preparing the joker tile for reuse.
        """
        if self.is_joker:
            self.number = None
            self.color = None

class Player:
    def __init__(self, name='Player') -> None:
        self.name = name
        self.hand = [] # array of Tiles
        self.has_placed_30 = False # the player can contribute after he placed in one turn 30+ tile points
        self.is_bot = False # the player is a bot

class GameState:
    def __init__(self) -> None:
        '''Used to pass to the bot info about the game'''
        pass

class TileSet:
        def __init__(self, tiles: list[Tile]) -> None:
            self.tile_set = tiles

        def is_valid(self) -> bool:
            if self.is_valid_sequence() or self.is_valid_group():
                return True
            return False
            
        def is_valid_sequence(self):
            if len(self.tile_set) < 3 or len(self.tile_set) > 13:
                # not enough/too much Tiles to complete a valid sequence
                return False
            
            sorted_tiles = sorted(self.tiles, key=lambda t: t.number)
            base_color = self.tile_set[0].color

            #TODO complete the logic

        def is_valid_group(self):
            if len(self.tile_set) not in [3, 4]:
                # not enough/too much Tiles to complete a valid group
                return False
            
            known_colors = []
            base_number = self.tile_set[0].number
            for tile in self.tile_set:
                if tile.color in known_colors:
                    # 2 identical color in one group, invalid
                    return False
                if tile.number != base_number:
                    # 2 different numbers in the group, invalid
                    return False
                
                known_colors.append(tile.color)
            # tile set has same numbers & different colors, valid
            return True

class Board:
    def __init__(self) -> None:
        self.sets = []
    
    def add_tile_set(self, tiles: list[Tile]):
        self.sets.append(TileSet(tiles))

class RummikubGame:
    def __init__(self, *players, player_to_start = None, ) -> None:
        # initialize players
        self.players = [Player(name) for name in players]
        if len(players) not in [2, 3, 4]:
            print(f'Rummikub can only be played with 2-4 players.')
            sys.exit() # TODO change the logic accordingly (with the ui)
        
        # initilize board & draw pile
        self.board = Board()
        self.draw_pile = self.init_draw_pile() # array of Tiles

        # other
        try:
            self.player_turn = [player.name for player in self.players].index(player_to_start) - 1 if player_to_start else None
        except ValueError:
            self.player_turn = None

        self.board.add_tile_set([Tile(1, 'blue'), Tile(6, 'blue'), Tile(6, 'blue'), Tile(6, 'blue')])
        print(self.board.sets[0].is_valid_group())

    def draw(self, tile_number: int) -> Tile | list[Tile]:
        '''Draw a specified number of tiles from the draw pile.'''
        if len(self.draw_pile) < tile_number:
            # not enough tiles in the draw
            return None
        
        if tile_number == 1:
            tile_picked = self.draw_pile[0]
            self.draw_pile = self.draw_pile[tile_number:]
            return tile_picked
        else:
            tiles_picked = self.draw_pile[:tile_number]
            self.draw_pile = self.draw_pile[tile_number:]
            return tiles_picked 

    def player_draw(self, player: Player) -> None:
        '''Action of player drawing one Tile (he cannot play so he has to draw)'''
        player.hand.append(self.draw(1))

    def init_draw_pile(self) -> list[Tile]:
        '''Initializes the draw pile and shuffle it (1-13 Tiles with 4 different colors duplicated and 2 jokers)'''
        colors = ['orange', 'blue', 'black', 'red']
        draw_pile = []    

        for tile_number in range(1, 14):
            for tile_color in colors:
                for _ in range(2):
                    draw_pile.append(Tile(tile_number, tile_color))
        
        draw_pile.extend([Tile(is_joker=True) for _ in range(2)])
        shuffle(draw_pile)
        return draw_pile

    def deal(self) -> None:
        '''Deal 14 Tiles to each player'''
        for player in self.players:
            player.hand = self.draw_pile(14)

    def get_player_turn(self) -> Player:
        '''Returns the player who needs to play'''
        if self.player_turn != None:
            # a player has already played
            self.player_turn = (self.player_turn + 1) % len(self.players)
            return self.players[self.player_turn]
        else:
            # (get) the first player to play
            self.player_turn = randint(0, len(self.players) - 1) # TODO implement different logic (choose whoever wants to start)
            return self.players[self.player_turn]
            
    def player_play(self, player: Player) -> None:
        '''Handle a player'''
        pass

if __name__ == '__main__':
    game = RummikubGame('coince', 'gabi', 'cheik')
