import re
from PyQt5.QtGui import QPixmap, QFontMetrics
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
from objects import pokemon, writer


class PokemonView(pokemon.PokemonObject, writer.Writer):
    def create_pokemon_list(self):
        pokemon_list = self.fetch_db_join('pokemon_dex_numbers.pokedex_number, '
                                          'pokemon_species_names.name, '
                                          'pokemon_species_names.pokemon_species_id',
                                          'pokemon_dex_numbers',
                                          'pokemon_species_names ON '
                                          'pokemon_species_names.pokemon_species_id = pokemon_dex_numbers.species_id',
                                          'pokemon_dex_numbers.pokedex_id= ' + str(self.pokedex_id) +
                                          ' AND pokemon_species_names.local_language_id= ' + str(
                                              self.local_language_id))

        self.sort_db(pokemon_list, 'pokemon')

    def set_game_button(self):
        self.m_pkmn_game_btn.setStyleSheet(
            "#m_pkmn_game_btn {background-image: url(:/img/icons/game/" +
            str(self.game_selected) + ".png);}"
                                      "#m_pkmn_game_btn:flat {border: none;}")

    def set_current_pokemon(self, pokemon):
        if type(pokemon) == QListWidgetItem:
            self.item = pokemon
            self.set_pkmn()
            self.selected_pokemon_row = self.m_pkmn_list.currentRow()
        elif pokemon:
            if 0 <= self.pokedex_id <= 7 or 10 <= self.pokedex_id:
                try:
                    self.m_pkmn_list.setCurrentRow(pokemon[0] - 1)
                except TypeError:
                    pass
            elif 8 <= self.pokedex_id <= 9:  # Victini is number 0, this will add an exception for Unova dex
                try:
                    self.m_pkmn_list.setCurrentRow(pokemon[0])
                except TypeError:
                    pass
        else:
            print('Error setting pokemon. Check function set_current_pokemon')

    def set_pokemon_display_page(self):
        # Check buttons Img|Stats|Moves|Loc
        sending_button = self.sender()
        for mode_btn in self.mode_btns:
            if sending_button.objectName() == mode_btn[1].objectName():
                self.pokemon_display_page = mode_btn[0]
            else:
                mode_btn[1].setStyleSheet(
                    '#' + mode_btn[1].objectName() + ' {background-image: url(:/img/buttons/pokemon/'
                    + mode_btn[1].objectName() + '.png);}'
                    '#' + mode_btn[1].objectName() + ':flat {border: none}')

        for i in range(1, 5):
            if i == self.pokemon_display_page:
                self.d_pkmn_i.setCurrentIndex(i - 1)
            if self.pokemon_display_page >= 2:
                self.t_pkmn_i.setCurrentIndex(1)
            else:
                self.t_pkmn_i.setCurrentIndex(0)

        if self.item:
            self.set_pkmn()

    def set_pokemon_stats_page(self):
        # Check buttons DMG|STA|EVO|EGG|TRN|FLA
        sending_button = self.sender()
        for stats_btn in self.stats_btns:
            if sending_button == stats_btn[1]:
                self.d_pkmn_i_2_info.setCurrentIndex(stats_btn[0] - 1)

    def set_pkmn(self):
        self.pokemon = self.get_pokemon()
        # print(self.pokemon)

        self.t_pkmn_number.setText(self.pokemon['number'])
        self.t_pkmn_name.setText(self.pokemon['name'])
        self.i_pkmn_label_type1.setText(self.pokemon['types'][0][1])
        if len(self.pokemon['types']) == 2:
            self.i_pkmn_label_type2.setText(self.pokemon['types'][1][1])
        else:
            self.i_pkmn_label_type2.setText(None)
        self.set_imgs()

        if self.pokemon_display_page == 2:
            self.set_stats_page()

    def set_stats_page(self):
        self.set_stats_basic()

        self.set_stats_damage()

        self.set_stats_base_stats()

        self.set_evolution_chain()

        self.set_breeding()

    def set_item_icons(self, item_id, phase, branched=False):
        pixmap = QPixmap(':/item/item/' + str(item_id) + '.png')
        if phase == 1:
            pass
        elif phase == 2:
            self.d_pkmn_i_2_i_evo_item_1.setPixmap(pixmap)
            self.d_pkmn_i_2_i_evo_item_1.show()
        elif phase == 3 and not branched:
            self.d_pkmn_i_2_i_evo_item_2.setPixmap(pixmap)
            self.d_pkmn_i_2_i_evo_item_2.show()
        elif phase == 3 and branched:
            self.d_pkmn_i_2_i_evo_item_2_2.setPixmap(pixmap)
            self.d_pkmn_i_2_i_evo_item_2_2.show()
        elif phase == 4 and not branched:
            self.d_pkmn_i_2_i_evo_item_3.setPixmap(pixmap)
            self.d_pkmn_i_2_i_evo_item_3.show()
        elif phase == 4 and branched:
            self.d_pkmn_i_2_i_evo_item_3_2.setPixmap(pixmap)
            self.d_pkmn_i_2_i_evo_item_3_2.show()

    def set_imgs(self):
        species_id = str(self.pokemon['species_id'])
        type_one = str(self.pokemon['types'][0][0])

        # Set main image
        pixmap = QPixmap(f':/pokemon/pokemon/image/{species_id}.png')
        self.d_pkmn_i_1_img.setPixmap(
            pixmap.scaled(self.d_pkmn_i_1_img.size(),
                          Qt.KeepAspectRatio,
                          Qt.SmoothTransformation))
        self.d_pkmn_i_1_img.show()

        # Set icon image next to name
        icon_pixmap = QPixmap(f':/pokemon/pokemon/icons/{species_id}.png')
        self.t_pkmn_icon.setPixmap(icon_pixmap)
        self.t_pkmn_icon.show()

        # Set background image according to pokemon's first type
        self.d_pkmn_i_1.setStyleSheet("#d_pkmn_i_1{background-image: url(:/bg/bgs/pkmn/type/" +
                                      str(self.pokemon['types'][0][0]) + ".png);}")

        # Type Icons
        pixmap = QPixmap(f':/pokemon/pokemon/types/{type_one}.png')
        self.i_pkmn_type_1.setPixmap(
            pixmap.scaled(self.i_pkmn_type_1.size(),
                          Qt.KeepAspectRatio,
                          Qt.SmoothTransformation))
        self.i_pkmn_type_1.show()

        if len(self.pokemon['types']) == 2:
            type_two = str(self.pokemon['types'][1][0])
            pixmap = QPixmap(f':/pokemon/pokemon/types/{type_two}.png')
            self.i_pkmn_type_2.setPixmap(
                pixmap.scaled(self.i_pkmn_type_2.size(),
                              Qt.KeepAspectRatio,
                              Qt.SmoothTransformation))
            self.i_pkmn_type_2.show()
        else:
            self.i_pkmn_type_2.hide()

    def set_sprites(self, shiny=False):
        version = str(self.pokemon['version'])
        version_group = str(self.pokemon['version_group'])
        species_id = str(self.pokemon['species_id'])
        evo_chain = [self.pokemon['evo_chain'][p] for p in self.pokemon['evo_chain']]

        # Modern games don't use sprites, BW style ones used
        # https://www.smogon.com/forums/threads/xy-sprite-project-read-1st-post-release-v1-1-on-post-3240.3486712/
        # https://www.smogon.com/forums/threads/sun-moon-sprite-project.3577711/
        if int(version) >= 12 or int(version) == 0:
            version_group = '11'

        # Gold and Silver versions have separate sprites for each version
        if version == '4':
            version_group = '3a'
        elif version == '5':
            version_group = '3b'

        # On mouse enter event the function is called again with key argument shiny=True, check eventFilter function
        if shiny and (version_group != '1' and version_group != '2'):  # Excludes first gen
            sprite_front = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/shiny/{species_id}.png')
            sprite_back = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/shiny/back/{species_id}.png')
            self.d_pkmn_i_2_sprite_f.setPixmap(sprite_front)
            self.d_pkmn_i_2_sprite_b.setPixmap(sprite_back)
        else:
            sprite_front = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{species_id}.png')
            sprite_back = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/back/{species_id}.png')
            self.d_pkmn_i_2_sprite_f.setPixmap(sprite_front)
            self.d_pkmn_i_2_sprite_b.setPixmap(sprite_back)

        # Evolution chain sprites TODO some refactoring
        for i in range(1, 5):
            if i == 1:
                evo_stage = evo_chain[0][0]
            elif i == 2 and len(evo_chain[1]) == 1:
                for evo_sprite_2_2 in (1, 2):  # For Phione/Manaphy line
                    eval('self.d_pkmn_i_2_i_evo_sprite_2_2_' + str(evo_sprite_2_2)).hide()
                for evo_sprite_2_4 in range(1, 5):  # For Tyrogue line
                    eval('self.d_pkmn_i_2_i_evo_sprite_2_4_' + str(evo_sprite_2_4)).hide()
                evo_stage = evo_chain[1][0]
            elif i == 3 and len(evo_chain[2]) == 1:
                for evo_sprite_3_2 in (1, 2):
                    eval('self.d_pkmn_i_2_i_evo_sprite_3_2_' + str(evo_sprite_3_2)).hide()
                for evo_sprite_3_9 in range(1, 10):  # For Eevee line
                    eval('self.d_pkmn_i_2_i_evo_sprite_3_9_' + str(evo_sprite_3_9)).hide()
                evo_stage = evo_chain[2][0]
            elif i == 4 and len(evo_chain[3]) == 1:
                for evo_sprite_4_2 in (1, 2):
                    eval('self.d_pkmn_i_2_i_evo_sprite_4_2_' + str(evo_sprite_4_2)).hide()
                for evo_sprite_4_9 in range(1, 10):
                    eval('self.d_pkmn_i_2_i_evo_sprite_4_9_' + str(evo_sprite_4_9)).hide()
                evo_stage = evo_chain[3][0]

            sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_' + str(i))
            sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
            sprite_evo_label.setPixmap(sprite_evo)
            sprite_evo_label.show()

            # For pokemon with branched evolutions like Eevee

            if len(evo_chain[1]) == 2 and i == 2:
                for n in range(len(evo_chain[1])):
                    evo_stage = evo_chain[1][n]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_2_2_' + str(n + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_2.hide()
                    for evo_sprite_2_4 in range(1, 5):
                        eval('self.d_pkmn_i_2_i_evo_sprite_2_4_' + str(evo_sprite_2_4)).hide()

            if len(evo_chain[1]) > 2 and i == 2:
                for n in range(len(evo_chain[1])):
                    evo_stage = evo_chain[1][n]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_2_4_' + str(n + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_2.hide()
                    for evo_sprite_2_2 in (1, 2):
                        eval('self.d_pkmn_i_2_i_evo_sprite_2_2_' + str(evo_sprite_2_2)).hide()

            if len(evo_chain[2]) == 2 and i == 3:
                for j in range(len(evo_chain[2])):
                    evo_stage = evo_chain[2][j]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_3_2_' + str(j + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_3.hide()
                    for evo_sprite_3_9 in range(1, 10):
                        eval('self.d_pkmn_i_2_i_evo_sprite_3_9_' + str(evo_sprite_3_9)).hide()

            if len(evo_chain[2]) > 2 and i == 3:
                for j in range(len(evo_chain[2])):
                    evo_stage = evo_chain[2][j]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_3_9_' + str(j + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_3.hide()
                    for evo_sprite_3_2 in (1, 2):
                        eval('self.d_pkmn_i_2_i_evo_sprite_3_2_' + str(evo_sprite_3_2)).hide()

            if len(evo_chain[3]) == 2 and i == 4:
                for k in range(len(evo_chain[3])):
                    evo_stage = evo_chain[3][k]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_4_2_' + str(k + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_4.hide()
                    for evo_sprite_4_9 in range(1, 10):
                        eval('self.d_pkmn_i_2_i_evo_sprite_4_9_' + str(evo_sprite_4_9)).hide()

            if len(evo_chain[3]) > 2 and i == 4:
                for k in range(len(evo_chain[3])):
                    evo_stage = evo_chain[3][k]
                    sprite_evo_label = eval('self.d_pkmn_i_2_i_evo_sprite_4_9_' + str(k + 1))
                    sprite_evo = QPixmap(f':/pokemon/pokemon/sprites/{version_group}/{evo_stage}.png')
                    sprite_evo_label.setPixmap(sprite_evo.scaled(sprite_evo_label.size(),
                                                                 Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation))
                    sprite_evo_label.show()
                    self.d_pkmn_i_2_i_evo_sprite_4.hide()
                    for evo_sprite_4_2 in (1, 2):
                        eval('self.d_pkmn_i_2_i_evo_sprite_4_2_' + str(evo_sprite_4_2)).hide()

    def set_stats_basic(self):
        # HEADER - Sprites and Description
        self.set_sprites()
        # Set description and resize font if necessary, default 12 points
        f = self.d_pkmn_i_2_desc.font()
        f.setPointSize(12)
        self.d_pkmn_i_2_desc.setText(self.pokemon['flavor'])
        width = self.d_pkmn_i_2_desc.fontMetrics().boundingRect(self.d_pkmn_i_2_desc.text()).width()
        text_size_factor = 276 / width + 0.45
        if text_size_factor <= 1:
            f.setPointSizeF(f.pointSizeF() * text_size_factor)
        self.d_pkmn_i_2_desc.setFont(f)

    def set_stats_damage(self):
        self.d_pkmn_i_2_i_d_ability_1.setText(self.pokemon['abilities'][0][0])
        if self.pokemon['abilities'][1]:
            self.d_pkmn_i_2_i_d_ability_2.setText(self.pokemon['abilities'][1][0])
        else:
            self.d_pkmn_i_2_i_d_ability_2.clear()
        if self.pokemon['abilities'][2]:
            self.d_pkmn_i_2_i_d_hidden_ability.setText(self.pokemon['abilities'][2][0])
        else:
            self.d_pkmn_i_2_i_d_hidden_ability.clear()

        def set_damage_values_color(label, value):
            if value == '4':
                label.setStyleSheet('color: rgb(228, 49, 49);')
            elif value == '2':
                label.setStyleSheet('color: rgb(247, 130, 35);')
            elif value == '1':
                label.setStyleSheet('color: rgb(225, 225, 225);')
            elif value == '\u00BD':
                label.setStyleSheet('color: rgb(156, 210, 27);')
            elif value == '\u00BC':
                label.setStyleSheet('color: rgb(58, 199, 229);')
            elif value == '0':
                label.setStyleSheet('color: rgb(26, 83, 211);')

        for i in range(1, 19):
            for key in self.pokemon['damage']:
                if i == key:
                    damage_type = eval('self.d_pkmn_i_2_i_d_' + str(i))
                    value = str(self.pokemon['damage'][key])
                    damage_type.setText(value + 'x')
                    set_damage_values_color(damage_type, value)

    def set_stats_base_stats(self):
        def change_bar_color(bar, value, stat):
            red = "css/progress_bar/red.css"
            orange = "css/progress_bar/orange.css"
            yellow = "css/progress_bar/yellow.css"
            green = "css/progress_bar/green.css"
            cyan = "css/progress_bar/cyan.css"
            if stat <= 6:
                if value <= 51:
                    stylesheet = red
                elif 51 < value <= 102:
                    stylesheet = orange
                elif 102 < value <= 153:
                    stylesheet = yellow
                elif 153 < value <= 204:
                    stylesheet = green
                elif 204 < value <= 255:
                    stylesheet = cyan
            else:  # Total Bar
                if value <= 255:
                    stylesheet = red
                elif 255 < value <= 510:
                    stylesheet = orange
                elif 510 < value <= 765:
                    stylesheet = yellow
                elif 765 < value <= 1020:
                    stylesheet = green
                elif 1020 < value <= 1275:
                    stylesheet = cyan
            with open(stylesheet, "r") as css:
                bar.setStyleSheet(css.read())

        for i in range(1, 8):
            for tuple in self.pokemon['stats']:
                base_stat = eval('self.d_pkmn_i_2_i_s_' + str(i))
                stat_bar = eval('self.d_pkmn_i_2_i_s_bar_' + str(i))
                if i == tuple[0]:
                    base_stat.setText(str(tuple[1]))
                    change_bar_color(stat_bar, tuple[1], i)
                    stat_bar.setValue(tuple[1])
        self.calc_ivs()

    def set_calculated_ivs(self):
        min_value_label = 'self.d_pkmn_i_2_i_iv_l_'
        max_value_label = 'self.d_pkmn_i_2_i_iv_h_'
        ivs = self.calculated_ivs

        for i in range(1, 7):
            label_min = eval(min_value_label + str(i))
            min_val = ivs['min'][i - 1]
            label_min.setText(str(min_val))
            label_max = eval(max_value_label + str(i))
            max_val = ivs['max'][i - 1]
            label_max.setText(str(max_val))

    def set_evolution_chain(self):
        # Resets evolution item icons
        for i in range(1, 4):
            eval('self.d_pkmn_i_2_i_evo_item_' + str(i) + '.hide()')
        self.d_pkmn_i_2_i_evo_item_2_2.hide()
        self.d_pkmn_i_2_i_evo_item_3_2.hide()

        def send_pokemon_to_get_item_icon(pokemon, phase, branched=False):
            if len(pokemon) > 1:
                if pokemon[3]:
                    self.set_item_icons(pokemon[3], phase, branched)
                elif pokemon[7]:
                    self.set_item_icons(pokemon[7], phase, branched)

        if self.pokemon['evo_data']['baby']:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['baby'][0], 1)
        if self.pokemon['evo_data']['base']:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['base'][0], 2)
        if len(self.pokemon['evo_data']['stg_1']) == 1:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_1'][0], 3)
        elif len(self.pokemon['evo_data']['stg_1']) == 2:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_1'][0], 3)
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_1'][1], 3, branched=True)
        if len(self.pokemon['evo_data']['stg_2']) == 1:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_2'][0], 4)
        elif len(self.pokemon['evo_data']['stg_2']) == 2:
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_2'][0], 4)
            send_pokemon_to_get_item_icon(self.pokemon['evo_data']['stg_2'][1], 4, branched=True)

    def set_evolution_description(self, pokemon):
        if type(pokemon) != list:
            description = self.write_evolution_description(pokemon)
            return description

    def set_breeding(self):
        breeding = self.pokemon['breeding']
        # Sets gender related info
        pixmap = QPixmap(':/pokemon/pokemon/gender/' + str(breeding[0][0]) + '.png')
        self.d_pkmn_i_2_i_egg_gender.setPixmap(pixmap)
        if breeding[0][0] == -1:
            self.d_pkmn_i_2_i_egg_gender_1.setText('')
            self.d_pkmn_i_2_i_egg_gender_2.setText('')
        elif breeding[0][0] == 0:
            self.d_pkmn_i_2_i_egg_gender_1.setText('8')
            self.d_pkmn_i_2_i_egg_gender_2.setText('0')
        elif breeding[0][0] == 1:
            self.d_pkmn_i_2_i_egg_gender_1.setText('7')
            self.d_pkmn_i_2_i_egg_gender_2.setText('1')
        elif breeding[0][0] == 2:
            self.d_pkmn_i_2_i_egg_gender_1.setText('6')
            self.d_pkmn_i_2_i_egg_gender_2.setText('2')
        elif breeding[0][0] == 4:
            self.d_pkmn_i_2_i_egg_gender_1.setText('4')
            self.d_pkmn_i_2_i_egg_gender_2.setText('4')
        elif breeding[0][0] == 6:
            self.d_pkmn_i_2_i_egg_gender_1.setText('2')
            self.d_pkmn_i_2_i_egg_gender_2.setText('6')
        elif breeding[0][0] == 7:
            self.d_pkmn_i_2_i_egg_gender_1.setText('1')
            self.d_pkmn_i_2_i_egg_gender_2.setText('7')
        elif breeding[0][0] == 8:
            self.d_pkmn_i_2_i_egg_gender_1.setText('0')
            self.d_pkmn_i_2_i_egg_gender_2.setText('8')

        #Calculates egg cycles according to gen selected
        if self.generation_id >= 2:
            self.d_pkmn_i_2_i_egg_hcount.setText(str(breeding[0][1]))
        if self.generation_id == 1:
            self.d_pkmn_i_2_i_egg_sth.setText('N/A')
            self.d_pkmn_i_2_i_egg_hcount.setText('N/A')
        elif self.generation_id == 2:
            self.d_pkmn_i_2_i_egg_sth.setText(str(breeding[0][1] * 256))
        elif self.generation_id == 3:
            self.d_pkmn_i_2_i_egg_sth.setText(str(breeding[0][1] * 256 + 256) + '/' +
                                              str(int(((breeding[0][1] * 256) / 2) + 256)))
        elif self.generation_id == 4:
            self.d_pkmn_i_2_i_egg_sth.setText(str(breeding[0][1] * 255 + 255) + '/' +
                                              str(int(((breeding[0][1] * 255) / 2) + 255)))
        elif self.generation_id >= 5:
            self.d_pkmn_i_2_i_egg_sth.setText(str(breeding[0][1] * 257) + '/' + str(int((breeding[0][1] * 257) / 2)))
        if self.game_selected == 0:  # When National Dex is selected latest step calc is used, independent of active gen
            self.d_pkmn_i_2_i_egg_sth.setText(str(breeding[0][1] * 257) + '/' + str(int((breeding[0][1] * 257) / 2)))

        self.d_pkmn_i_2_i_egg_group_1.setText(breeding[2][0])
        if len(breeding[2]) == 2:
            self.d_pkmn_i_2_i_egg_group_2.setText(breeding[2][1])
        else:
            self.d_pkmn_i_2_i_egg_group_2.setText('')

    def set_breeding_compatible(self, item):
        self.set_current_pokemon(item.data(32))

    def search_pkmn(self):
        query = self.i_pkmn_search_bar.text().lower().split()
        filtered_items = []

        # Reset list by entering empty string
        if not query:
            self.filter_pkmn(filtered_items, True)

        else:
            # By Name
            if self.i_pkmn_by_name.isChecked():
                for q in query:
                    q = '"%' + q + '%"'
                    r = self.fetch_db('pokemon_species_id',
                                      'pokemon_species_names',
                                      'name LIKE ' + q +
                                      ' AND local_language_id= ' + str(self.local_language_id))
                    r = [i[0] for i in r]
                    filtered_items.append(r)
                filtered_items = [item for sublist in filtered_items for item in sublist]
                self.filter_pkmn(filtered_items, False)

            # By Number
            if self.i_pkmn_by_number.isChecked():
                for q in query:
                    try:
                        r = self.fetch_db('species_id',
                                          'pokemon_dex_numbers',
                                          'pokedex_number= ' + str(q) +
                                          ' AND pokedex_id =' + str(self.pokedex_id))
                        r = [i[0] for i in r]
                        filtered_items.append(r)
                    except:
                        self.statusbar.showMessage('Please type numbers only.', 5000)
                filtered_items = [item for sublist in filtered_items for item in sublist]
                self.filter_pkmn(filtered_items, False)

            # By Type
            if self.i_pkmn_by_type.isChecked():
                for q in query:
                    if '+' in q:
                        q = q.split('+')
                        if len(q) > 2:
                            self.statusbar.showMessage('Please insert only 2 types for combo searching.', 4000)
                            self.i_pkmn_search_bar.setText('')
                        else:
                            if q[0]:
                                q1 = '"%' + q[0] + '%"'
                            else:
                                q1 = '""'
                            if q[1]:
                                q2 = '"%' + q[1] + '%"'
                            else:
                                q2 = '""'

                            r = self.fetch_db_join('pokemon_types.pokemon_id',
                                                   'type_names',
                                                   'pokemon_types ON pokemon_types.type_id = type_names.type_id',
                                                   '(name LIKE '+q1+' AND pokemon_types.slot= 1 '
                                                   'AND type_names.local_language_id= '+str(self.local_language_id) +
                                                   ') OR ('
                                                   'name LIKE '+q2+' AND pokemon_types.slot= 2 '
                                                   'AND type_names.local_language_id= '+str(self.local_language_id)+')')
                            r = [i[0] for i in r]
                            filtered_items.append(r)
                    else:
                        q = '"%' + q + '%"'
                        r = self.fetch_db_join('pokemon_types.pokemon_id',
                                               'type_names',
                                               'pokemon_types ON pokemon_types.type_id = type_names.type_id',
                                               'name LIKE ' + q +
                                               'AND type_names.local_language_id= ' + str(self.local_language_id))
                        r = [i[0] for i in r]
                        filtered_items.append(r)
                filtered_items = [item for sublist in filtered_items for item in sublist]
                self.filter_pkmn(filtered_items, False)

    def filter_pkmn(self, filtered_items, reset):
        all_items = self.m_pkmn_list.findItems('*', Qt.MatchWildcard)
        for item in all_items:
            if not reset:
                item.setHidden(True)
                for index in filtered_items:
                    if index == item.data(33):
                        item.setHidden(False)
            else:
                item.setHidden(False)

    def filter_name_chars(self, name):
        name = re.sub('\u2642', '-m', name)
        name = re.sub('\u2640', '-f', name)
        name = re.sub("\u2019", '', name)
        name = re.sub("\. ", '-', name)
        name = re.sub("\: ", '-', name)
        name = re.sub("é", 'e', name)
        name = re.sub("tapu ", 'tapu-', name)
        name = re.sub(" jr\.", '-jr', name)
        return name
