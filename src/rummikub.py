from rummikub_bot import RummikubBot
from random import shuffle, randint
import copy
import sys


class Tile:
    def __init__(self, number=None, color=None, is_joker=False) -> None:
        self.number = number if not is_joker else None
        self.color = color if not is_joker else None
        self.is_joker = is_joker
    
    def __str__(self):
        return f'[{self.number}-{self.color}]'

    def clear_joker(self) -> None:
        """
        Clear the number and color attributes of a joker tile.

        This method is called when a player replaces the joker with its corresponding tile, preparing the joker tile for reuse.
        """
        if self.is_joker:
            self.number = None
            self.color = None

class Player:
    def __init__(self, name='Player', is_bot=False) -> None:
        self.name = name
        self.hand = [] # array of Tiles
        self.has_placed_30 = False # the player can contribute after he placed in one turn 30+ tile points
        self.is_bot = is_bot # if the player is a bot

class GameState:
    def __init__(self) -> None:
        '''Used to pass to the bot info about the game'''
        pass

class TileSet:
    def __init__(self, tiles: list[Tile]) -> None:
        self.tile_set = tiles
        self.update_attributes()
        # a tile_set has to be valid
        # TODO add splitting & inserting logic (with additional methods)

    def append_tile(self, position: str, tile: Tile) -> None:
        '''append to the tileset tiles at position
        str position: left | right
        tile: tile to be inserted
        '''
        tileset_snapshot = self.get_snapshot()
        # insert the tile in the tile_set
        if position == 'left':
            self.tile_set.insert(0, tile)
        else:
            self.tile_set.append(tile)
        if self.is_valid():
            # new set is valid, update attributes
            self.update_attributes()
        else:
            # new sequence is invalid, restore snapshot 
            self.restore_snapshot(tileset_snapshot)
        
    def update_attributes(self) -> None:
        '''used to update different attributes when changes are made'''
        self.left_tile = self.tile_set[0]
        self.right_tile = self.tile_set[-1]
        self.size = len(tiles)
    
    def get_snapshot(self):
        '''returns the snapshot of the current tileset state'''
        return copy.deepcopy(self.__dict__)
    
    def restore_snapshot(self, snapshot):
        '''restores a snapshot of a tilset state'''
        self.__dict__.update(copy.deepcopy(snapshot))

    def is_valid(self) -> bool:
        '''Check if the TileSet instance is a valid sequence or a valid group.'''
        if self.is_valid_sequence() or self.is_valid_group():
            return True
        return False
    
    def is_valid_sequence(self) -> bool:
        '''Check if the TileSet instance is a valid sequence.'''
        if len(self.tile_set) < 3 or len(self.tile_set) > 13:
            # not enough/too much Tiles to complete a valid sequence
            return False
        
        sorted_tiles = sorted(self.tile_set, key=lambda t: t.number)
        base_color = self.tile_set[0].color
        base_number = self.tile_set[0].number
        for i, tile in enumerate(sorted_tiles):
            if tile.color != base_color:
                # different colors in sequence, invalid
                return False
            if (tile.number + i) - (base_number + i) != i:
                # bad number sequence
                return False
        # valid sequence
        return True
            
    def is_valid_group(self) -> bool:
        '''Check if the TileSet instance is a valid group.'''
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
    
    def __str__(self):
        tileset = ''
        for tile in self.tile_set:
            tileset += f'[{tile.number}-{tile.color}]  '
        return tileset

class TempBoard:
    def __init__(self) -> None:
        pass
        # TODO add temp set logic

# -- class --
# should store multiple TileSet.
# is used after a player makes 'temp' moves that are illegal on the board thus cannot be stored in the valid groups
# at the end of a player turn instance should be cleared
# 
# -- Methods --
# check for every temp sets & tell if they are all resolved
# clear all the temp sets / make sure to clear resoled sets
# 


class Board:
    def __init__(self) -> None:
        '''constructor of the board'''
        self.groups = []
        self.sequences = []
        self.temp_sets = []

    def split_set(self, index: int) -> None:
        '''Splits groups/sequences in a given index'''
        # to be implemented later (after temp sets class)
        pass

    def add_tile_set(self, tiles):
        '''Add a tile set to either groups if it's a valid group, sequence if it's a valid sequence else in temp sets'''
        tile_set = TileSet(tiles)
        if tile_set.is_valid_group():
            # tile_set is a valid group
            self.groups.append(tile_set)
        elif tile_set.is_valid_sequence():
            # tile_set is a valid sequence
            self.sequences.append(tile_set)
        else:
            # tile_set isn't valid
            self.temp_sets.append(tile_set)

    def get_snapshot(self):
        '''returns the snapshot of the current board state'''
        return copy.deepcopy(self.__dict__)

    def restore_snapshot(self, snapshot):
        '''restores a snapshot of a board state'''
        self.__dict__.update(copy.deepcopy(snapshot))

    def clear_temp_sets(self):
        '''clears the temp set array'''
        self.temp_sets = []

    def __str__(self):
        board_str = '====== SEQUENCES ======\n'
        for tile_set in self.sequences:
            board_str += f'{tile_set}\n'
            
        board_str += '\n====== GROUPS ======\n'
        for tile_set in self.groups:
            board_str += f'{tile_set}\n'

        board_str += '\n====== TEMP ======\n'
        for tile_set in self.temp_sets:
            board_str += f'{tile_set}\n'

        return board_str

class RummikubGame:
    def __init__(self, player_info: list[tuple], player_to_start = None, ) -> None:
        # initialize players
        self.players = [Player(name, is_bot) for name, is_bot in player_info]
        if len(self.players) not in [2, 3, 4]:
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

    def get_next_player_turn(self) -> Player:
        '''Returns the player who needs to play'''
        if self.player_turn != None:
            # a player has already played
            self.player_turn = (self.player_turn + 1) % len(self.players)
            return self.players[self.player_turn]
        else:
            # (get) the first player to play
            self.player_turn = randint(0, len(self.players) - 1)
            return self.players[self.player_turn]
            
    def player_play(self, player: Player) -> None:
        '''Handle a player move'''
        pass


if __name__ == '__main__':
    player_info = [('coince', False), ('gabi', True), ('cheik', False)]
    game = RummikubGame(player_info, 'coince')

    # TODO (*)idea: make a class for the temp tiles on the board (keep track of them easier)
    # player to play init
    player_to_play = game.get_next_player_turn()


    # interaction 1: place a valid tile set on the board OR place invalid tile(s) on the (temp) board
    tiles = [Tile(1, 'blue'), Tile(2, 'blue'), Tile(3, 'blue'), Tile(4, 'blue')]
    game.board.add_tile_set(tiles)

    # interaction 2: insert a tile on the left/right of a tile set
    game.board.sequences[0].append_tile('right', Tile(5, 'blue'))

    # TODO interaction 3: splitting a board tile set into two different tile sets (*)idea


    # TODO interaction 4: merging different groups of tiles into one valid tile set (if isn't possible loading last snapshot of the board)
