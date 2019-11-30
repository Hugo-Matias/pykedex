"""
This object gathers all the necessary information about a specific pokemon.

INPUT FROM THE QWidgetListItem (self.selected_pokemon_item):
.text() - Name
.data(32) - Current Pokedex Number
.data(33) - Species ID (National Pokedex Number)
"""
import os, re
from operator import itemgetter
from collections import defaultdict


class PokemonObject:
    def get_pokemon(self):
        # Essential
        version = self.game_selected
        version_group = self.get_version_group(version)
        species_id = self.item.data(33)
        number = self.get_number()
        name = self.item.text()
        types = self.get_types()
        # Stats - Header
        desc = self.get_stats_description()
        # Stats  - Damage
        abilities = self.get_stats_abilities()
        damage = self.get_stats_damage_types(types)
        # Stats - Base Stats
        stats = self.get_stats_base()
        # Stats - Evolution Chain
        evo_chain = self.get_stats_evo()
        evo_data = self.get_evo_data(evo_chain)
        # Stats - Breeding
        breeding = self.get_breeding_data()
        # Stats - Training
        training = self.get_training_data()
        # Stats - Flavor
        flavor = self.get_flavor_data()
        pokemon = {'version': version,
                   'version_group': version_group,
                   'species_id': species_id,
                   'name': name,
                   'number': number,
                   'types': types,
                   'desc': desc,
                   'abilities': abilities,
                   'damage': damage,
                   'stats': stats,
                   'evo_chain': evo_chain,
                   'evo_data': evo_data,
                   'breeding': breeding,
                   'training': training,
                   'flavor': flavor}

        return pokemon

    def get_version_group(self, version):
        version_group = self.fetch_db('version_group_id', 'versions', 'id= ' + str(version))
        if not version_group:
            version_group = 0
        else:
            version_group = version_group[0][0]

        return version_group

    def get_number(self):
        pkn = str(self.item.data(32))
        if len(pkn) == 1:
            num = ('# 00' + pkn)
        elif len(pkn) == 2:
            num = ('# 0' + pkn)
        else:
            num = ('# ' + pkn)
        return num

    def get_types(self):
        query = '''SELECT pokemon_types.type_id, type_names.name, pokemon_types.slot 
                FROM pokemon_types INNER JOIN type_names 
                ON type_names.type_id = pokemon_types.type_id 
                WHERE pokemon_types.pokemon_id=''' + str(self.item.data(33)) + \
                ''' AND type_names.local_language_id ='''

        pokemon_types = self.fetch_db_query(query + str(self.local_language_id))
        if not pokemon_types:
            pokemon_types = self.fetch_db_query(query + '9')

        return pokemon_types

    def get_stats_description(self):
        species_id = str(self.item.data(33))
        version = str(self.game_selected)
        if version == '27':  # No data for Pokémon Sun, Pokémon Moon's is used instead
            version = '28'
        if version == '30':  # No data for Pokémon Ultra Moon, Pokémon Ultra Sun's is used instead
            version = '29'
        language_id = str(self.local_language_id)
        query = f'SELECT flavor_text FROM pokemon_species_flavor_text WHERE species_id={species_id} ' \
            f'AND version_id= {version} AND language_id= {language_id}'

        def clean_flavor(flavor):
            flavor = re.sub(r'\u00ad\n', '', flavor)
            flavor = re.sub(r'\n', ' ', flavor)
            flavor = re.sub(r'\f', ' ', flavor)
            return flavor

        flavor = self.fetch_db_query(query)

        while not flavor:  # If no description is available for the version on the specific lang, search other versions
            for i in range(30, 0, -1):
                version = str(i)
                query = f'SELECT flavor_text FROM pokemon_species_flavor_text WHERE species_id={species_id} ' \
                    f'AND version_id= {version} AND language_id= {language_id}'
                flavor = self.fetch_db_query(query)
                if flavor:
                    break
                elif i == 1 and not flavor:
                    flavor = [('No description available\n\nfor this language.',)]
                    break

        flavor = clean_flavor(flavor[0][0])

        return flavor

    def get_stats_abilities(self):
        language = self.local_language_id
        pokemon_id = self.item.data(33)
        abilities = []

        fquery = 'SELECT ability_names.name, ability_prose.short_effect FROM ability_names ' \
                 'INNER JOIN pokemon_abilities ON pokemon_abilities.ability_id=ability_names.ability_id ' \
                 'INNER JOIN ability_prose ON ability_prose.ability_id = pokemon_abilities.ability_id ' \
                 'WHERE pokemon_abilities.pokemon_id = {pokemon_id} AND pokemon_abilities.slot = {slot} ' \
                 'AND ability_names.local_language_id = {language} AND ability_prose.local_language_id = {language}'

        # query = fquery.format(pokemon_id=pokemon_id, slot=1, language=language)
        ability_1 = self.fetch_db_query(fquery.format(pokemon_id=pokemon_id, slot=1, language=language))
        ability_2 = self.fetch_db_query(fquery.format(pokemon_id=pokemon_id, slot=2, language=language))
        ability_3 = self.fetch_db_query(fquery.format(pokemon_id=pokemon_id, slot=3, language=language))

        # def clean_effect_description(ability):  # TODO
        #     print(ability[1])
        #     # check = re.findall(r'(\[\w+\])', ability[1])
        #     sub = re.sub(r'\[', '', ability[1])
        #     sub = re.sub(r'\]', '', sub)
        #     sub = re.sub(r'(\{\w+:\w+})', '', sub)
        #     print(sub)

        for i in [ability_1, ability_2, ability_3]:
            if i:
                # clean_effect_description(i[0])
                abilities.append(i[0])
            else:
                i = ()
                abilities.append(i)

        return abilities

    def get_stats_damage_types(self, types):
        pokemon_types = []

        query = 'SELECT damage_type_id, damage_factor FROM type_efficacy ' \
                'WHERE target_type_id = {type}'

        if len(types) == 2:
            pokemon_types = [types[0][0], types[1][0]]
            damage_factor_1 = self.fetch_db_query(query.format(type=pokemon_types[0]))
            damage_factor_2 = self.fetch_db_query(query.format(type=pokemon_types[1]))
            damage_factors = {key: value / 100 for (key, value) in damage_factor_1}
            for (k, v) in damage_factor_2:
                if k in damage_factors:
                    damage_factors[k] *= v / 100
        else:
            pokemon_types = [types[0][0]]
            damage_factors = self.fetch_db_query(query.format(type=pokemon_types[0]))
            damage_factors = {key: value / 100 for (key, value) in damage_factors}

        def convert_values(value):
            if value >= 1 or value == 0:
                value = int(value)
            elif value == 0.5:
                value = '\u00BD'
            elif value == 0.25:
                value = '\u00BC'
            return value

        for key in damage_factors:
            damage_factors[key] = convert_values(damage_factors[key])

        return damage_factors

    def get_stats_base(self):
        stats = self.fetch_db('stat_id, base_stat, effort', 'pokemon_stats', 'pokemon_id=' + str(self.item.data(33)))
        total = []
        for t in stats:
            total.append(t[1])
        stats.append((7, sum(total), 0))

        return stats

    def get_stats_evo(self):
        evolution_chain_id = self.fetch_db('evolution_chain_id', 'pokemon_species', 'id=' + str(self.item.data(33)))
        evolution_chain_id = evolution_chain_id[0][0]

        evolution_chain_pokemons_data = self.fetch_db('id, evolves_from_species_id, is_baby',
                                                      'pokemon_species',
                                                      'evolution_chain_id=' + str(evolution_chain_id))
        # Output: [(25, 172, 0), (26, 25, 0), (172, None, 1)] - Pikachu line unsorted and with baby
        # Nulls need to be zeroed for sorting, a new list will be created to manipulate the tuples
        evolution_chain_pokemons = []
        for i in evolution_chain_pokemons_data:
            if not i[1]:
                l = list(i)
                l[1] = 0
                i = tuple(l)
                evolution_chain_pokemons.append(i)
            else:
                evolution_chain_pokemons.append(i)

        # Sorts first evo(i.e evolves_from_species field == none)
        evolution_chain_pokemons = sorted(evolution_chain_pokemons, key=itemgetter(1))
        # print(evolution_chain_pokemons)

        sorted_evo_chain = defaultdict(list)

        baby = 0
        baby_key = sorted_evo_chain['baby']
        base = 0
        base_key = sorted_evo_chain['base']
        stg_1 = 0
        stg_1_key = sorted_evo_chain['stg_1']
        stg_2 = 0
        stg_2_key = sorted_evo_chain['stg_2']

        for i in evolution_chain_pokemons:
            if i[1] == 0 and i[2] == 1:
                baby = i[0]
            elif i[1] == 0 or i[1] in sorted_evo_chain['baby']:
                base = i[0]
            else:
                for j in evolution_chain_pokemons:
                    if i[1] == j[0] and (j[1] == baby or j[1] == 0):
                        stg_1 = i[0]
                    elif i[1] == j[0] and j[0] in sorted_evo_chain['stg_1']:
                        stg_2 = i[0]

            if baby not in baby_key and baby != 0:
                baby_key.append(baby)
            if base not in base_key and base != 0:
                base_key.append(base)
            if stg_1 not in stg_1_key and stg_1 != 0:
                stg_1_key.append(stg_1)
            if stg_2 not in stg_2_key and stg_2 != 0:
                stg_2_key.append(stg_2)

        for key in sorted_evo_chain:
            if sorted_evo_chain[key] == []:
                sorted_evo_chain[key] = [0]
        # print(sorted_evo_chain)

        return sorted_evo_chain

    def get_evo_data(self, evo_chain):
        def get_evolution_stage_data(species_id):
            data = self.fetch_db('evolved_species_id,'
                                 'evolution_trigger_id,'
                                 'trigger_item_id,'
                                 'minimum_level,'
                                 'gender_id,'
                                 'location_id,'
                                 'held_item_id,'
                                 'time_of_day,'
                                 'known_move_id,'
                                 'known_move_type_id,'
                                 'minimum_happiness,'
                                 'minimum_beauty,'
                                 'minimum_affection,'
                                 'relative_physical_stats,'
                                 'party_species_id,'
                                 'party_type_id,'
                                 'trade_species_id,'
                                 'needs_overworld_rain,'
                                 'turn_upside_down',
                                 'pokemon_evolution',
                                 'evolved_species_id= ' + str(species_id))

            pokedex_number = self.fetch_db('pokedex_number',
                                           'pokemon_dex_numbers',
                                           'pokedex_id= ' + str(self.pokedex_id) +
                                           ' AND species_id= ' + str(species_id))

            if pokedex_number and data:
                data = pokedex_number[0] + data[0]
            elif pokedex_number and not data:
                data = pokedex_number[0]
            # print(data)
            return data

        evo_chain_data = defaultdict(list)
        baby_key = evo_chain_data['baby']
        base_key = evo_chain_data['base']
        stg_1_key = evo_chain_data['stg_1']
        stg_2_key = evo_chain_data['stg_2']

        if evo_chain['baby'][0] != 0:
            for pokemon_baby in evo_chain['baby']:
                baby_key.append(get_evolution_stage_data(pokemon_baby))

            for pokemon_base in evo_chain['base']:
                if pokemon_base != 0:
                    base_key.append(get_evolution_stage_data(pokemon_base))

        if evo_chain['base'][0] != 0:
            for pokemon_base in evo_chain['base']:
                if get_evolution_stage_data(pokemon_base) not in evo_chain_data['base']:
                    base_key.append(get_evolution_stage_data(pokemon_base))
            for pokemon_stg_1 in evo_chain['stg_1']:
                if pokemon_stg_1 != 0:
                    stg_1_key.append(get_evolution_stage_data(pokemon_stg_1))

        if evo_chain['stg_1'][0] != 0:
            for pokemon_stg_2 in evo_chain['stg_2']:
                if pokemon_stg_2 != 0:
                    stg_2_key.append(get_evolution_stage_data(pokemon_stg_2))
        # print(evo_chain_data)
        return evo_chain_data

    def get_breeding_data(self):
        breeding_data = self.fetch_db('gender_rate, hatch_counter', 'pokemon_species',
                                      'id = ' + str(self.item.data(33)))
        query = 'SELECT egg_group_prose.egg_group_id, name FROM egg_group_prose INNER JOIN pokemon_egg_groups ' \
                'ON pokemon_egg_groups.egg_group_id = egg_group_prose.egg_group_id ' \
                'WHERE pokemon_egg_groups.species_id = ' + str(self.item.data(33)) + \
                ' AND egg_group_prose.local_language_id= '

        egg_groups = self.fetch_db_query(query + str(self.local_language_id))
        if not egg_groups:
            egg_groups = self.fetch_db_query(query + str(self.local_language_id_en))

        breeding_data = [breeding_data[0],
                         tuple([group_id[0] for group_id in egg_groups]),
                         tuple([group_name[1] for group_name in egg_groups])]

        compatible_pokemons = []
        if breeding_data[1][0] != 15 and breeding_data[1][0] != 13:  # No Undiscovered and no Ditto groups
            if breeding_data[0][0] != -1:  # Checks if sel. pokemon is not genderless
                for pokemon in self.base_pokemons:
                    # Filters single gender pokemon from reproducing with same gender (ex. Nidoran F. w/ Kangaskhan)
                    # Genderless and Undiscovered egg group are also filtered out
                    if (pokemon[3] != -1 or pokemon[2][0] == 13) and \
                            pokemon[2][0] != 15 and \
                            breeding_data[0][0] + pokemon[3] != 16 and \
                            breeding_data[0][0] + pokemon[3] != 0:

                        for i in range(len(breeding_data[1])):
                            if breeding_data[1][i] in pokemon[2] and pokemon not in compatible_pokemons:
                                compatible_pokemons.append(pokemon)

                            # Adds Ditto to the compatible list (13 is it's own egg group)
                            if pokemon[2][0] == 13 and pokemon not in compatible_pokemons:
                                compatible_pokemons.append(pokemon)
            else:
                for pokemon in self.base_pokemons:
                    if pokemon[2][0] == 13:
                        compatible_pokemons.append(pokemon)  # Adds Ditto for genderless pokemon

        if self.item.data(33) == 132:  # Creates Ditto compatibles list, every pkmn except Undiscovered/Ditto egg groups
            for pokemon in self.base_pokemons:
                if pokemon[2][0] != 15 and pokemon[2][0] != 13:
                    compatible_pokemons.append(pokemon)

        self.populate_list(compatible_pokemons, 'egg_group')
        return breeding_data

    def get_training_data(self):
        query_t = 'SELECT pokemon.base_experience, ' \
                  'pokemon_species.capture_rate, pokemon_species.base_happiness, ' \
                  'growth_rate_prose.name ' \
                  'FROM pokemon ' \
                  'INNER JOIN pokemon_species ON pokemon.id = pokemon_species.id ' \
                  'INNER JOIN growth_rate_prose ON pokemon_species.growth_rate_id = growth_rate_prose.growth_rate_id ' \
                  'WHERE pokemon.id = ' + str(self.item.data(32)) + ' AND growth_rate_prose.local_language_id = '

        training_data = self.fetch_db_query(query_t + str(self.local_language_id))
        if not training_data:
            training_data = self.fetch_db_query(query_t + str(self.local_language_id_en))

        def get_effort_points(stat_id):
            points = self.fetch_db('effort', 'pokemon_stats',
                                   'pokemon_id = ' + str(self.item.data(32)) +
                                   ' AND stat_id =' + str(stat_id) + ' AND effort > 0')
            if points:
                points = points[0][0]

            return points

        effort_points = {}
        effort_points['hp'] = get_effort_points(1)
        effort_points['atk'] = get_effort_points(2)
        effort_points['def'] = get_effort_points(3)
        effort_points['spa'] = get_effort_points(4)
        effort_points['spd'] = get_effort_points(5)
        effort_points['spe'] = get_effort_points(6)

        training_data = training_data + [effort_points]

        return training_data

    def get_flavor_data(self):
        pokemon_id = str(self.item.data(33))
        version = str(self.game_selected)
        language = str(self.local_language_id)
        language_en = str(self.local_language_id_en)

        flavor = {}
        flavor['height'] = self.fetch_db('height', 'pokemon', 'id =' + pokemon_id)[0][0]
        flavor['weight'] = self.fetch_db('weight', 'pokemon', 'id =' + pokemon_id)[0][0]
        flavor['species'] = self.fetch_db('genus', 'pokemon_species_names', 'pokemon_species_id =' + pokemon_id)[0][0]

        flavor['species'] = self.fetch_db('genus', 'pokemon_species_names',
                                          'pokemon_species_id =' + pokemon_id +
                                          ' AND local_language_id = ' + language)[0][0]
        if not flavor['species']:
            flavor['species'] = self.fetch_db('genus', 'pokemon_species_names',
                                              'pokemon_species_id =' + pokemon_id +
                                              ' AND local_language_id = ' + language_en)[0][0]

        flavor['shape'] = self.fetch_db_join('pokemon_species.shape_id, pokemon_shape_prose.awesome_name',
                                             'pokemon_species',
                                             'pokemon_shape_prose ON '
                                             'pokemon_species.shape_id = pokemon_shape_prose.pokemon_shape_id',
                                             'pokemon_species.id =' + pokemon_id +
                                             ' AND local_language_id = ' + language)[0]
        if not flavor['shape']:
            flavor['shape'] = self.fetch_db_join('pokemon_species.shape_id, pokemon_shape_prose.awesome_name',
                                                 'pokemon_species',
                                                 'pokemon_shape_prose ON '
                                                 'pokemon_species.shape_id = pokemon_shape_prose.pokemon_shape_id',
                                                 'pokemon_species.id =' + pokemon_id +
                                                 ' AND local_language_id = ' + language_en)[0]

        flavor['habitat'] = self.fetch_db('habitat_id', 'pokemon_species', 'id = ' + pokemon_id)[0][0]

        flavor['color'] = self.fetch_db_join('pokemon_species.color_id, pokemon_color_names.name',
                                             'pokemon_species',
                                             'pokemon_color_names '
                                             'ON pokemon_species.color_id = pokemon_color_names.pokemon_color_id',
                                             'pokemon_species.id = ' + pokemon_id +
                                             ' AND pokemon_color_names.local_language_id = ' + language)[0]
        if not flavor['color']:
            flavor['color'] = self.fetch_db_join('pokemon_species.color_id, pokemon_color_names.name',
                                                 'pokemon_species',
                                                 'pokemon_color_names '
                                                 'ON pokemon_species.color_id = pokemon_color_names.pokemon_color_id',
                                                 'pokemon_species.id = ' + pokemon_id +
                                                 ' AND pokemon_color_names.local_language_id = ' + language_en)[0]
        try:
            flavor['item'] = self.fetch_db_join('pokemon_items.item_id, pokemon_items.rarity, item_names.name',
                                                'pokemon_items',
                                                'item_names ON pokemon_items.item_id = item_names.item_id',
                                                'pokemon_items.pokemon_id = ' + pokemon_id +
                                                ' AND pokemon_items.version_id = ' + version +
                                                ' AND item_names.local_language_id = ' + language)[0]
            if not flavor['item']:
                flavor['item'] = self.fetch_db_join('pokemon_items.item_id, pokemon_items.rarity, item_names.name',
                                                    'pokemon_items',
                                                    'item_names ON pokemon_items.item_id = item_names.item_id',
                                                    'pokemon_items.pokemon_id = ' + pokemon_id +
                                                    ' AND pokemon_items.version_id = ' + version +
                                                    ' AND item_names.local_language_id = ' + language_en)[0]
        except IndexError:
            flavor['item'] = []

        return flavor

    def get_base_pokemons(self):
        initial_base_list = [pokemon[0] for pokemon in
                             self.fetch_db('id', 'pokemon_species', 'evolves_from_species_id IS NULL AND is_baby= 0')]

        baby_pokemons = [baby[0] for baby in self.fetch_db('id', 'pokemon_species', 'is_baby= 1')]
        base_from_baby = []
        for baby in baby_pokemons:
            p = self.fetch_db('id', 'pokemon_species', 'evolves_from_species_id= ' + str(baby))
            for pkmn in p:
                base_from_baby.append(pkmn)

        base_pokemons = sorted(initial_base_list + [pokemon[0] for pokemon in base_from_baby])

        base_pokemon_dex_numbers = []
        for pk in base_pokemons:
            if self.pokedex_id > 0:
                p = self.fetch_db('pokedex_number, species_id',  # Order matters for set_current_pokemon function
                                  'pokemon_dex_numbers',
                                  'pokedex_id= ' + str(self.pokedex_id) + ' AND species_id = ' + str(pk))
            else:
                p = (pk, pk)
            if p:
                base_pokemon_dex_numbers.append(p[0])

        base_pokemon_groups = []
        for pokemon in base_pokemon_dex_numbers:
            base_egg_groups = self.fetch_db('egg_group_id', 'pokemon_egg_groups', 'species_id=' + str(pokemon[1]))
            gender_rate = self.fetch_db('gender_rate', 'pokemon_species', 'id=' + str(pokemon[1]))
            base_pokemon_groups.append((pokemon, '',
                                        tuple([group_id[0] for group_id in base_egg_groups]),
                                        gender_rate[0][0]))
        return base_pokemon_groups

    def get_moves(self, method):
        pokemon = str(self.item.data(33))
        version = str(self.game_selected)
        language = str(self.local_language_id)
        language_en = str(self.local_language_id_en)

        if version != '0':
            version_group = str(self.fetch_db('version_group_id', 'versions', 'id = ' + version)[0][0])
        else:
            version_group = '18'

        if method != 4:
            query = 'SELECT pokemon_moves.move_id, pokemon_moves."level", pokemon_moves."order", ' \
                    'move_names.name, moves.type_id, moves.damage_class_id, moves.power, moves.accuracy ' \
                    'FROM pokemon_moves ' \
                    'INNER JOIN move_names ON pokemon_moves.move_id = move_names.move_id ' \
                    'INNER JOIN moves ON pokemon_moves.move_id = moves.id ' \
                    'WHERE pokemon_moves.pokemon_id = {pokemon_id} ' \
                    'AND pokemon_moves.pokemon_move_method_id = {method} ' \
                    'AND pokemon_moves.version_group_id = {version_id} ' \
                    'AND move_names.local_language_id = {language} ' \
                    'ORDER BY pokemon_moves."level" ASC, pokemon_moves."order" ASC, move_names.name ASC'

        elif method == 4:  # Fetches TM/HM names
            query = 'SELECT pokemon_moves.move_id, pokemon_moves."level", pokemon_moves."order", ' \
                    'move_names.name, moves.type_id, moves.damage_class_id, moves.power, moves.accuracy, ' \
                    'item_names.name ' \
                    'FROM pokemon_moves ' \
                    'INNER JOIN move_names ON pokemon_moves.move_id = move_names.move_id ' \
                    'INNER JOIN moves ON pokemon_moves.move_id = moves.id ' \
                    'INNER JOIN machines ON machines.move_id = pokemon_moves.move_id ' \
                    'INNER JOIN item_names ON item_names.item_id = machines.item_id ' \
                    'WHERE pokemon_moves.pokemon_id = {pokemon_id} ' \
                    'AND pokemon_moves.pokemon_move_method_id = {method} ' \
                    'AND pokemon_moves.version_group_id = {version_id} ' \
                    'AND machines.version_group_id = {version_id} ' \
                    'AND move_names.local_language_id = {language} ' \
                    'AND item_names.local_language_id = {language} ' \
                    'ORDER BY pokemon_moves."level" ASC, pokemon_moves."order" ASC, ' \
                    'item_names.name ASC, move_names.name ASC '

        moves = self.fetch_db_query(query.format(pokemon_id=pokemon, method=str(method),
                                                 version_id=version_group, language=language))
        if not moves:
            moves = self.fetch_db_query(query.format(pokemon_id=pokemon, method=str(method),
                                                     version_id=version_group, language=language_en))
        return moves

    def get_locations(self):
        pokemon_id = self.pokemon['species_id']
        version = self.game_selected
        language = self.local_language_id
        language_en = self.local_language_id_en

        query = 'SELECT locations.id, region_names.name, location_names.name, encounter_slots.rarity,' \
                'encounter_method_prose.name, ' \
                'encounters.min_level, encounters.max_level ' \
                'FROM region_names ' \
                'INNER JOIN locations ON region_names.region_id = locations.region_id ' \
                'INNER JOIN location_names ON location_names.location_id = locations.id ' \
                'INNER JOIN location_areas ON location_areas.location_id = locations.id ' \
                'INNER JOIN encounters ON encounters.location_area_id = location_areas.id ' \
                'INNER JOIN encounter_slots ON encounter_slots.id = encounters.encounter_slot_id ' \
                'INNER JOIN encounter_method_prose ' \
                'ON encounter_method_prose.encounter_method_id = encounter_slots.encounter_method_id ' \
                'WHERE encounters.pokemon_id = {pokemon_id} ' \
                'AND encounters.version_id = {version_id} ' \
                'AND region_names.local_language_id = {language} ' \
                'AND location_names.local_language_id = {language} ' \
                'AND encounter_method_prose.local_language_id = {language} ' \
                'ORDER BY location_names.name ASC, encounter_slots.rarity ASC'

        locations = self.fetch_db_query(query.format(pokemon_id=pokemon_id, version_id=version, language=language))
        if not locations:
            locations = self.fetch_db_query(query.format(pokemon_id=pokemon_id,
                                                         version_id=version, language=language_en))
        return locations
