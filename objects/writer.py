class Writer:
    def write_evolution_description(self, pokemon):
        if len(pokemon) > 1:

            evolution_trigger_id = pokemon[2]

            trigger_item_id = pokemon[3]
            minimum_level = pokemon[4]

            gender_id = pokemon[5]
            location_id = pokemon[6]
            held_item_id = pokemon[7]
            time_of_day = pokemon[8]

            known_move_id = pokemon[9]
            known_move_type_id = pokemon[10]

            minimum_happiness = pokemon[11]
            minimum_beauty = pokemon[12]
            minimum_affection = pokemon[13]

            relative_physical_stats = pokemon[14]

            party_species_id = pokemon[15]
            party_type_id = pokemon[16]
            trade_species_id = pokemon[17]

            needs_overworld_rain = pokemon[18]
            turn_upside_down = pokemon[19]

            if evolution_trigger_id == 1:
                evolution_trigger_string = 'Level up'

                if minimum_level:
                    minimum_level_string = ', starts evolving at ' + str(minimum_level)
                else:
                    minimum_level_string = ''

                if gender_id:
                    gender = self.get_gender_name(gender_id)
                    gender_string = ', must be ' + gender
                else:
                    gender_string = ''

                if location_id:
                    location_name = self.get_location_name(location_id)
                    location_string = ' in the ' + location_name + ' area'
                else:
                    location_string = ''

                if held_item_id:
                    item_name = self.get_item_name(held_item_id)
                    held_item_string = ' holding item ' + item_name
                else:
                    held_item_string = ''

                if time_of_day:
                    time_of_day_string = ' during ' + time_of_day + ' time'
                else:
                    time_of_day_string = ''

                if known_move_id:
                    move_name = self.get_move_name(known_move_id)
                    known_move_id_string = ' after learning ' + move_name
                else:
                    known_move_id_string = ''

                if known_move_type_id:
                    move_type = self.get_type_name(known_move_type_id)
                    known_move_type_id_string = ' knowing a ' + move_type + '-type move'
                else:
                    known_move_type_id_string = ''

                if minimum_happiness:
                    minimum_happiness_string = ' with at least ' + str(minimum_happiness) + ' happiness'
                else:
                    minimum_happiness_string = ''

                if minimum_beauty:
                    minimum_beauty_string = ' with at least ' + str(minimum_beauty) + ' beauty'
                else:
                    minimum_beauty_string = ''

                if minimum_affection:
                    minimum_affection_string = '\n with at least ' +\
                                               '\u2764' * minimum_affection + ' affection in Pokémon-Amie'  # u2764 = ❤
                else:
                    minimum_affection_string = ''

                if relative_physical_stats in [-1, 0, 1]:
                    relative_state = self.get_relative_stats(relative_physical_stats)
                    relative_physical_stats_string = ' if Attack is ' + relative_state + ' Defense'
                else:
                    relative_physical_stats_string = ''

                if party_species_id:
                    party_species_name = self.get_pokemon_name(party_species_id)
                    party_species_string = ' with ' + party_species_name + ' in your party'
                else:
                    party_species_string = ''

                if party_type_id:
                    party_type_name = self.get_type_name(party_type_id)
                    party_type_string = ' with a ' + party_type_name + '-type Pokémon in your party'
                else:
                    party_type_string = ''

                if needs_overworld_rain == 1:
                    needs_overworld_rain_string = ' while raining'
                else:
                    needs_overworld_rain_string = ''

                if turn_upside_down == 1:
                    turn_upside_down_string = ' with console turned upside down'
                else:
                    turn_upside_down_string = ''

                description = f'{evolution_trigger_string}{minimum_level_string}{gender_string}' \
                    f'{location_string}{held_item_string}{time_of_day_string}' \
                    f'{known_move_id_string}{known_move_type_id_string}' \
                    f'{minimum_happiness_string}{minimum_beauty_string}{minimum_affection_string}' \
                    f'{relative_physical_stats_string}{party_species_string}{party_type_string}' \
                    f'{needs_overworld_rain_string}{turn_upside_down_string}'

            if evolution_trigger_id == 2:
                evolution_trigger_string = 'Trade'
                if held_item_id:
                    item_name = self.get_item_name(held_item_id)
                    held_item_string = ' holding item ' + item_name
                else:
                    held_item_string = ''
                if trade_species_id:
                    pokemon_name = self.get_pokemon_name(trade_species_id)
                    trade_species_string = ' in exchange for ' + pokemon_name
                else:
                    trade_species_string = ''

                description = f'{evolution_trigger_string}{held_item_string}{trade_species_string}'

            if evolution_trigger_id == 3:
                evolution_trigger_string = 'Use item '
                item_name = self.get_item_name(trigger_item_id)
                trigger_item_string = item_name

                if gender_id:
                    gender = self.get_gender_name(gender_id)
                    gender_string = ', must be ' + gender
                else:
                    gender_string = ''

                description = f'{evolution_trigger_string}{trigger_item_string}{gender_string}'

            if evolution_trigger_id == 4:
                evolution_trigger_string = 'Shed '

                description = f'{evolution_trigger_string}'

            return description

    def get_pokemon_name(self, pokemon_species_id):
        query = 'SELECT name FROM pokemon_species_names WHERE pokemon_species_id= ' \
                + str(pokemon_species_id) + ' AND local_language_id= '
        pokemon_species_name = self.fetch_db_query(query + str(self.local_language_id))
        if not pokemon_species_name:
            pokemon_species_name = self.fetch_db_query(query + str(self.local_language_id_en))

        return pokemon_species_name[0][0]

    def get_item_name(self, item_id):
        query = 'SELECT name FROM item_names WHERE item_id= ' + str(item_id) + ' AND local_language_id= '
        item_name = self.fetch_db_query(query + str(self.local_language_id))
        if not item_name:
            item_name = self.fetch_db_query(query + str(self.local_language_id_en))

        return item_name[0][0]

    def get_move_name(self, move_id):
        query = 'SELECT name FROM move_names WHERE move_id= ' + str(move_id) + ' AND local_language_id= '
        move_name = self.fetch_db_query(query + str(self.local_language_id))
        if not move_name:
            move_name = self.fetch_db_query(query + str(self.local_language_id_en))

        return move_name[0][0]

    def get_type_name(self, type_id):
        query = 'SELECT name FROM type_names WHERE type_id= ' + str(type_id) + ' AND local_language_id= '
        type_name = self.fetch_db_query(query + str(self.local_language_id))
        if not type_name:
            type_name = self.fetch_db_query(query + str(self.local_language_id_en))

        return type_name[0][0]

    def get_location_name(self, location_id):
        query = 'SELECT name FROM location_names WHERE location_id= ' + str(location_id) + ' AND local_language_id= '
        location_name = self.fetch_db_query(query + str(self.local_language_id))
        if not location_name:
            location_name = self.fetch_db_query(query + str(self.local_language_id_en))

        return location_name[0][0]

    def get_gender_name(self, gender_id):
        if gender_id == 1:
            return 'female'
        elif gender_id == 2:
            return 'male'

    # Mostly used for Tyrogue evolution type. It compares attack and defense and evolves accordingly.
    def get_relative_stats(self, relative_stats):
        if relative_stats == 1:
            return 'higher than'
        elif relative_stats == -1:
            return 'lower than'
        elif relative_stats == 0:
            return 'equal to'
