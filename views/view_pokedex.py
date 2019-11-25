from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect


class PokedexView:
    def create_generation_list(self):
        generation_loader = self.fetch_db('generation_id, name', 'generation_names',
                                          'local_language_id= ' + str(self.local_language_id))
        self.sort_db(generation_loader, 'generation')

    def set_generation(self, item):
        self.generation_id = item.data(32)

        self.version_group_loader = self.fetch_db('id', 'version_groups',
                                                  'generation_id =' + str(item.data(32)) +
                                                  ' AND id!= 12 AND id!= 13')
        self.version_group_loader = [i[0] for i in self.version_group_loader]

        versions_loader = self.fetch_db_join('version_groups.id, versions.id', 'version_groups',
                                             'versions ON versions.version_group_id = version_groups.id',
                                             'generation_id= ' + str(self.generation_id) +
                                             ' AND versions.id!= 19 AND versions.id!= 20')

        self.versions_dict = {}  # https://www.w3resource.com/python-exercises/tuple/python-tuple-exercise-19.php
        for a, b in versions_loader:
            self.versions_dict.setdefault(a, []).append(b)

        self.games_page = 0
        self.game_scroll(None)
        self.set_games()

    def set_games(self):
        self.games_last_page = len(self.version_group_loader) - 1
        id = self.version_group_loader[self.games_page]
        self.game_versions = self.versions_dict[id]

        if len(self.game_versions) == 1:
            self.d_pokedex_g.setCurrentIndex(1)
            game_icon = QIcon(':img//icons/game_cover/' + str(self.game_versions[0]) + '.png')
            self.d_pokedex_g_1_1.setIcon(game_icon)

        elif len(self.game_versions) == 2:
            self.d_pokedex_g.setCurrentIndex(2)
            game_1_icon = QIcon(':img//icons/game_cover/' + str(self.game_versions[0]) + '.png')
            self.d_pokedex_g_2_1.setIcon(game_1_icon)
            game_2_icon = QIcon(':img//icons/game_cover/' + str(self.game_versions[1]) + '.png')
            self.d_pokedex_g_2_2.setIcon(game_2_icon)
        else:
            self.d_pokedex_g.setCurrentIndex(0)

        self.d_pokedex_g_1_reg_sel.hide()
        self.d_pokedex_g_2_reg_sel.hide()
        self.m_pokedex_activate.hide()
        self.t_pokedex_region_name.clear()
        self.t_pokedex_version_name.clear()

        game_covers = [self.d_pokedex_g_1_1, self.d_pokedex_g_2_1, self.d_pokedex_g_2_2]
        for cover in game_covers:
            self.set_game_state(cover, 'disable')

        self.set_regions()

    def set_regions(self):
        # Set Icons
        pokedex_ids = self.fetch_db('pokedex_id', 'pokedex_version_groups',
                                    'version_group_id IN ' + str(tuple(self.version_group_loader)))
        pokedex_ids = [i[0] for i in pokedex_ids]

        pokedex_icon_match = {1: [2], 2: [3], 3: [4], 4: [2],
                              5: [5, 6], 6: [7], 7: [8, 9], 8: [15],
                              9: [12, 13, 14], 10: [16, 17, 18, 19, 20, 21, 22, 23, 24, 25]}

        for i in range(1, 11):
            icon_pixmap = QPixmap(':/img/icons/pokedex/' + str(i) + '.png')
            icon_object = eval('self.i_pokedex_ico_' + str(i))
            icon_object.setPixmap(icon_pixmap)
            icon_object.show()
            if self.generation_id == 1 and i >= 2:
                continue
            elif self.generation_id > 1 and i < 2:
                continue
            else:
                for j in pokedex_ids:
                    if j in pokedex_icon_match[i]:
                        icon_pixmap = QPixmap(':/img/icons/pokedex/' + str(i) + '_on.png')
                        icon_object = eval('self.i_pokedex_ico_' + str(i))
                        icon_object.setPixmap(icon_pixmap)
                        icon_object.show()

    def set_game_state(self, widget, state):
        # Grey-out color effect
        effect = QGraphicsColorizeEffect(widget)
        effect.setColor(QColor('grey'))
        widget.setGraphicsEffect(effect)

        if state == 'disable':
            effect.setStrength(1.0)
        elif state == 'enable':
            effect.setStrength(0.0)
        elif state == 'select':
            effect.setColor(QColor('white'))
            effect.setStrength(0.7)
        else:
            pass

    def game_scroll(self, state):
        if state == 'next':
            self.games_page += 1
            self.set_games()
        elif state == 'prev':
            self.games_page -= 1
            self.set_games()

        # Disable Previous arrow on game's page 0
        if self.games_page <= 0:
            self.d_pokedex_g_1_prev.setEnabled(False)
            self.d_pokedex_g_2_prev.setEnabled(False)
        else:
            self.d_pokedex_g_1_prev.setEnabled(True)
            self.d_pokedex_g_2_prev.setEnabled(True)

        # Disable Next arrow on last game's page
        if self.games_page >= self.games_last_page:
            self.d_pokedex_g_1_next.setEnabled(False)
            self.d_pokedex_g_2_next.setEnabled(False)
        else:
            self.d_pokedex_g_1_next.setEnabled(True)
            self.d_pokedex_g_2_next.setEnabled(True)

    def set_pokedex(self):
        r = self.fetch_db_join('pokedex_prose.pokedex_id, pokedex_prose.name, '
                               'version_names.name, pokedex_prose.description',
                               'pokedex_version_groups',
                               'versions ON '
                               'versions.version_group_id = pokedex_version_groups.version_group_id '
                               'INNER JOIN pokedexes ON pokedexes.id = pokedex_version_groups.pokedex_id '
                               'INNER JOIN pokedex_prose ON pokedex_prose.pokedex_id = pokedexes.id '
                               'INNER JOIN version_names ON version_names.version_id = versions.id',
                               'versions.id= ' + str(self.game_selected) +
                               ' AND pokedex_prose.local_language_id= ' + str(self.local_language_id) +
                               ' AND version_names.local_language_id= ' + str(self.local_language_id))

        version_name = []
        for i in r:
            version_name.append(i[2])

        region_name = []
        for j in r:
            region_name.append(j[1])

        # Games with more than one region will show a dropdown box to pick the desired region dex
        cb = self.d_pokedex_g_2_reg_sel
        if len(region_name) <= 1:
            cb.hide()
            self.t_pokedex_region_name.setText(''.join(set(region_name)))
            self.t_pokedex_version_name.setText('Pokémon ' + ''.join(set(version_name)))
            self.statusbar.showMessage(r[0][3], 5000)
            self.pokedex_id = r[0][0]

        if len(region_name) >= 2:
            cb.show()
            cb.clear()
            for item in r:
                cb.addItem(item[1], userData=[item[0], item[2], item[3]])

        self.m_pokedex_activate.show()

    def set_region_combobox(self):
        cb = self.d_pokedex_g_2_reg_sel
        self.t_pokedex_region_name.setText(cb.currentText())

        try:
            self.t_pokedex_version_name.setText('Pokémon ' + str(cb.currentData()[1]))
            self.statusbar.showMessage(cb.currentData()[2], 5000)
        except:
            pass

    def set_national_pokedex(self):
        self.pokedex_id = 1
        self.game_selected = 0
        self.set_view('pokemon')

    def select_pokedex(self):
        cb = self.d_pokedex_g_2_reg_sel
        if cb.isVisible():
            self.pokedex_id = cb.currentData()[0]
        self.set_view('pokemon')