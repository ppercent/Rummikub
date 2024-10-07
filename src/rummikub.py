from rummikub_bot import RummikubBot
from random import shuffle, randint
import copy
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

    def __eq__(self, other):
        return (self.number == other.number) and (self.color == other.color) and (self.is_joker == other.is_joker)

    def __str__(self):
        return f'[{self.number}-{self.color}]' if not self.is_joker else f'[{self.number if self.number else "no_value"}, {self.color if self.color else "no_value"}, joker]'

class Player:
    def __init__(self, name='Player', is_bot=False) -> None:
        self.name = name
        self.hand = [] # array of Tiles
        self.has_placed_30 = False # the player can contribute after he placed in one turn 30+ tile points
        self.is_bot = is_bot # if the player is a bot

    def __str__(self) -> str:
        hand_str = ""
        for tile in self.hand:
            hand_str += str(tile) + ' '
        
        player_info = f"""
        --- Player: {self.name} ---
        hand: {hand_str}
        has placed 30: {self.has_placed_30}
        is bot: {self.is_bot}
        ------
        """
        return player_info
    
class GameState:
    def __init__(self) -> None:
        '''Used to pass to the bot info about the game'''
        pass

class TileSet:
    def __init__(self, tiles: list[Tile]) -> None:
        self.tile_set = tiles
        self.update_attributes()

    def split_set(self, index: int, board_instance: 'Board'):
        '''Splits tileset in a given index'''
        if index <= 0 or index >= len(self.tile_set):
            # invalid index, returning
            return
        
        split_tiles = list((self.tile_set[:index], self.tile_set[index:]))
        split_tile_set = [TileSet(split_tiles[0]), TileSet(split_tiles[-1])]
        
        for tileset in split_tile_set:
            board_instance.add_tile_set(tileset)

    def append_tile(self, position: str, tile: Tile) -> None:
        '''append to the tileset tiles at position: 
        str position: left | right\n
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
        self.size = len(self.tile_set)
    
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

    def sequence_sort(self):
        '''Sorts the tileset by sequence'''
        sorted_set = []
        color_set = {}

        # sort by color
        for tile in self.tile_set:
            if tile.color not in color_set:
                color_set[tile.color if tile.color else 'joker'] = [tile]
            else:
                color_set[tile.color].append(tile)
        
        # sort tile number
        for color, tiles in color_set.items():
            tile_numbers = [tile.number for tile in tiles if tile.number]
            sorted_numbers = sorted(tile_numbers)

            if color == 'joker':
                sorted_set.append(joker for joker in tiles)
            for num in sorted_numbers:
                sorted_set.append(tiles[tile_numbers.index(num)])

        self.tile_set = sorted_set

    def group_sort(self):
        '''Sorts the tileset by groups'''
        groups = {}
	for tile in self.tile_set:
	    if tile.nombre not in groups:
	        groups[tile.nombre] = [tile]
            else:	
	        groups[tile.nombre].append(tile)
				
		

    def __eq__(self, other):
        return self.tile_set == other.tile_set

    def __str__(self):
        tileset = ''
        for tile in self.tile_set:
            tileset += f'{str(tile)}  '
        return tileset

class Board:
    def __init__(self) -> None:
        '''constructor of the board'''
        self.groups = []        # array of TileSet | must be valid
        self.sequences = []     # array of TileSet | must be valid
        self.temp_sets = []     # array of TileSet | can be invalid

    def merge_sets(self, left_set: TileSet, right_set: TileSet) -> None:
        '''Merge two TileSets if it creates a valid TileSet'''
        # create the array of tiles and merge it
        tile_array = []
        for tile in left_set.tile_set:
            tile_array.append(tile)

        for tile in right_set.tile_set:
            tile_array.append(tile)

        # convert it to a TileSet & clear the remaining copies of the Tiles
        merged_tile_set = TileSet(tile_array)
        if merged_tile_set.is_valid():
            self.add_tile_set(merged_tile_set)

            self.remove_tile_set(left_set)
            self.remove_tile_set(right_set)

    def remove_tile_set(self, tileset: TileSet) -> None:
        '''Removes a TileSet from the board. POTENTIAL ISSUE HERE'''
        self.groups.remove(tileset) if tileset in self.groups else None
        self.sequences.remove(tileset) if tileset in self.sequences else None
        self.temp_sets.remove(tileset) if tileset in self.temp_sets else None

    def add_tile_set(self, tiles: list[Tile] | TileSet) -> None:
        '''Add a tile set to either: groups if it's a valid group, sequence if it's a valid sequence else in temp sets'''
        if type(tiles).__name__ == 'list':
            tile_set = TileSet(tiles)
        else:
            tile_set = tiles
        
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
        board_str += 'No sets in sequences\n' if len(self.sequences) == 0 else ''
        for tile_set in self.sequences:
            board_str += f'{tile_set}\n'
            
        board_str += '\n====== GROUPS ======\n'
        board_str += 'No sets in groups\n' if len(self.groups) == 0 else ''
        for tile_set in self.groups:
            board_str += f'{tile_set}\n'

        board_str += '\n====== TEMP ======\n'
        board_str += 'No sets in temp\n' if len(self.temp_sets) == 0 else ''
        for tile_set in self.temp_sets:
            board_str += f'{tile_set}\n'

        return board_str

class RummikubGame:
    def __init__(self, player_info: list[tuple], player_to_start = None) -> None:
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
            player.hand = self.draw(14)

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
            
    def player_turn(self, player: Player) -> None:
        pass

if __name__ == '__main__':
    player_info = [('coince', False), ('gabi', False), ('cheik', False)]
    game = RummikubGame(player_info)
    game.deal()

    player_to_play = game.get_next_player_turn()
    tiles = TileSet([tile for tile in player_to_play.hand])
    tiles.sequence_sort()
    print(tiles)
