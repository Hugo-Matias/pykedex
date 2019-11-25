import sys, sqlite3
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem
from PyQt5.QtCore import Qt, QEvent, QSettings
from gui import Ui_MainWindow
from views.view_pokedex import PokedexView
from views.view_pokemon import PokemonView
from calc.iv import IVs


class MainWindow(QMainWindow, Ui_MainWindow, PokedexView, PokemonView, IVs):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.show()
        #
        # VARIABLES AND SETTINGS
        #
        self.conn = sqlite3.connect('db.sqlite')
        # USER SETTINGS
        self.caught_pokemon = {}
        # GLOBAL VARIABLES
        self.generation_id = 1
        self.pokedex_id = 2
        self.game_selected = 0
        self.current_pokemon = []
        self.local_language_id_en = 9
        self.local_language_id = 9
        self.last_view = 1  # 1 - Pokemon(default) | 2 - Pokedex
        self.item = None  # Current list selection. Used to fetch information from "objects"
        self.pokemon = None  # Current pokemon
        # POKEDEX VIEW VARIABLES
        self.version_group_loader = []
        self.versions_dict = {}
        self.games_page = 0
        self.games_last_page = 5  # Random default value to make sure the next button is visible on startup
        self.game_versions = []
        self.selected_game_source = 0
        # POKEMON VIEW VARIABLES
        self.pokemon_display_page = 1
        self.selected_pokemon_row = 0
        self.mode_btns = [(1, self.i_pkmn_mode_img_btn),
                          (2, self.i_pkmn_mode_stats_btn),
                          (3, self.i_pkmn_mode_moves_btn),
                          (4, self.i_pkmn_mode_loc_btn)]
        self.stats_btns = [(1, self.d_pkmn_i_2_btn_1),
                           (2, self.d_pkmn_i_2_btn_2),
                           (3, self.d_pkmn_i_2_btn_3),
                           (4, self.d_pkmn_i_2_btn_4),
                           (5, self.d_pkmn_i_2_btn_5),
                           (6, self.d_pkmn_i_2_btn_6)]
        self.ability_names = [self.d_pkmn_i_2_i_d_ability_1,
                              self.d_pkmn_i_2_i_d_ability_2,
                              self.d_pkmn_i_2_i_d_hidden_ability]
        self.calculated_ivs = {}
        #
        # POKEDEX VIEW INTERACTIONS
        #
        self.game_scroll(None)
        self.d_pokedex_g_1_1.installEventFilter(self)
        self.d_pokedex_g_2_1.installEventFilter(self)
        self.d_pokedex_g_2_2.installEventFilter(self)
        self.m_pokedex_activate.installEventFilter(self)
        self.m_pokedex_nat.clicked.connect(self.set_national_pokedex)
        self.m_pokedex_list.itemClicked.connect(self.set_generation)
        self.d_pokedex_g_1_next.clicked.connect(lambda: self.game_scroll('next'))
        self.d_pokedex_g_1_prev.clicked.connect(lambda: self.game_scroll('prev'))
        self.d_pokedex_g_2_next.clicked.connect(lambda: self.game_scroll('next'))
        self.d_pokedex_g_2_prev.clicked.connect(lambda: self.game_scroll('prev'))
        self.d_pokedex_g_2_reg_sel.currentIndexChanged.connect(self.set_region_combobox)
        self.m_pokedex_activate.clicked.connect(self.select_pokedex)
        #
        # POKEMON VIEW INTERACTIONS
        #
        # Sets a margin to the right of the search box so that text isn't displayed behind the search button
        self.i_pkmn_search_bar.setTextMargins(0, 0, 60, 0)
        # self.m_pkmn_list.itemClicked.connect(self.set_pkmn)
        self.m_pkmn_list.currentItemChanged.connect(self.set_current_pokemon)
        self.m_pkmn_game_btn.clicked.connect(lambda: self.set_view('pokedex'))
        self.i_pkmn_search_bar.textChanged.connect(self.search_pkmn)
        self.i_pkmn_search_btn.clicked.connect(self.search_pkmn)
        self.d_pkmn_i_2_i_iv_level.textChanged.connect(self.calc_ivs)
        self.d_pkmn_i_2_i_iv_effort.textChanged.connect(self.calc_ivs)
        self.d_pkmn_i_2_sprite_b.installEventFilter(self)
        self.d_pkmn_i_2_sprite_f.installEventFilter(self)
        self.i_pkmn_search_btn.installEventFilter(self)
        for mode_btn in self.mode_btns:
            mode_btn[1].clicked.connect(self.set_pokemon_display_page)
            mode_btn[1].installEventFilter(self)
        for stats_btn in self.stats_btns:
            stats_btn[1].clicked.connect(self.set_pokemon_stats_page)
            stats_btn[1].installEventFilter(self)
        for ability in self.ability_names:
            ability.installEventFilter(self)

        #
        # START-UP FUNCTIONS
        #
        self.restore_settings()
        self.set_view(None)
        # self.set_view_pokemon()

    #
    # INITIALIZATIONS, DATABASE AND SETTINGS MANAGEMENT
    #
    # https://www.techonthenet.com/sql/where.php
    def fetch_db(self, value, table, condition):
        c = self.conn.cursor()
        c.execute("SELECT {v} FROM {t} WHERE {c}".format(v=value, t=table, c=condition))
        result = c.fetchall()
        return result

    # SELECT value_1, value_2 AS val_2
    # FROM table_1
    # INNERJOIN table_2
    # ON table_2.id_column = table_1.id_column
    # WHERE table_1.value_x = something
    # AND table_2 IN ("value_y")
    # OR table_1 > value_z
    # https://www.sqlitetutorial.net/sqlite-inner-join/
    def fetch_db_join(self, value, table, join, condition):
        c = self.conn.cursor()
        c.execute("SELECT {v} FROM {t} INNER JOIN {j} WHERE {c}".format(v=value, t=table, j=join, c=condition))
        result = c.fetchall()
        return result

    # https://www.sqlitetutorial.net/sqlite-case/
    def fetch_db_query(self, query):
        c = self.conn.cursor()
        c.execute(query)
        result = c.fetchall()
        return result

    def set_view(self, mode):
        if self.last_view == 1 or mode == 'pokemon':
            index = 0
            self.last_view = 1
            self.create_pokemon_list()
            self.m_pkmn_list.setCurrentRow(self.selected_pokemon_row)
        if self.last_view == 2 or mode == 'pokedex':
            index = 1
            self.last_view = 2
            self.create_generation_list()
            self.set_regions()
            self.m_pokedex_activate.hide()

        self.menuWidget.setCurrentIndex(index)
        self.titleWidget.setCurrentIndex(index)
        self.displayWidget.setCurrentIndex(index)
        self.infoWidget.setCurrentIndex(index)

        self.set_game_button()

    def sort_db(self, db, db_type):
        db = sorted(db, key=lambda x: x[0])
        self.populate_list(db, db_type)

    def populate_list(self, db, db_type):
        if db_type == 'pokemon':
            self.m_pkmn_list.clear()
        elif db_type == 'generation':
            self.m_pokedex_list.clear()

        for item in db:
            entry = QListWidgetItem(item[1])
            entry.setData(32, item[0])  # Database entry for 'name'
            if db_type == 'pokemon':
                entry.setData(33, item[2])  # Pokemon Species ID
                # entry.setTextAlignment(Qt.AlignHCenter)
                self.m_pkmn_list.addItem(entry)
            elif db_type == 'generation':
                self.m_pokedex_list.addItem(entry)

        if db_type == 'pokemon':
            # Set list icons
            all_items = self.m_pkmn_list.findItems('*', Qt.MatchWildcard)
            for pokemon in all_items:
                pixmap = QPixmap(':/pokemon/pokemon/icons/' + str(pokemon.data(33)) + '.png')
                icon = QIcon(pixmap)
                pokemon.setIcon(icon)

    def closeEvent(self, event):
        self.save_settings()
        super(MainWindow, self).closeEvent(event)
        pass

    def save_settings(self):
        settings = QSettings('HLM', 'Pykedex')
        settings.setValue('generation_id', self.generation_id)
        settings.setValue('pokedex_id', self.pokedex_id)
        settings.setValue('local_language_id', self.local_language_id)
        settings.setValue('last_view', self.last_view)
        settings.setValue('game_selected', self.game_selected)
        settings.setValue('pokemon_display_page', self.pokemon_display_page)
        settings.setValue('selected_pokemon_row', self.selected_pokemon_row)
        settings.sync()

    def restore_settings(self):
        settings = QSettings('HLM', 'Pykedex')
        self.pokedex_id = settings.value('pokedex_id', self.pokedex_id, type=int)
        self.local_language_id = settings.value('local_language_id', self.local_language_id, type=int)
        self.last_view = settings.value('last_view', self.last_view, type=int)
        self.generation_id = settings.value('generation_id', self.generation_id)
        self.game_selected = settings.value('game_selected', self.game_selected)
        self.pokemon_display_page = settings.value('pokemon_display_page', self.pokemon_display_page)
        self.selected_pokemon_row = settings.value('selected_pokemon_row', self.selected_pokemon_row)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.i_pkmn_search_btn:
            icon = QIcon(':/img/search_h.png')
            self.i_pkmn_search_btn.setIcon(icon)
        if event.type() == QEvent.Leave and source is self.i_pkmn_search_btn:
            icon = QIcon(':/img/search.png')
            self.i_pkmn_search_btn.setIcon(icon)

        # Pokedex Select Button

        if event.type() == QEvent.Enter and source is self.m_pokedex_activate:
            source.setStyleSheet('#m_pokedex_activate {'
                                 'background-image: url(:/img/buttons/pokedex/select_hover.png);}'
                                 '#m_pokedex_activate:pressed {'
                                 'background-image: url(:/img/buttons/pokedex/select_clicked.png);}'
                                 '#m_pokedex_activate:flat {border: none}')
            self.statusbar.showMessage('Select the current game database.', 3000)
        if event.type() == QEvent.Leave and source is self.m_pokedex_activate:
            source.setStyleSheet('#m_pokedex_activate {background-image: url(:/img/buttons/pokedex/select_normal.png);}'
                                 '#m_pokedex_activate:flat {border: none}')

        # Pokedex Game Icons

        game_icons = [self.d_pokedex_g_1_1, self.d_pokedex_g_2_1, self.d_pokedex_g_2_2]
        for game in game_icons:
            if event.type() == QEvent.Enter and source is game and self.selected_game_source != source:
                self.set_game_state(game, 'select')
            if event.type() == QEvent.Leave and source is game and self.selected_game_source != source:
                self.set_game_state(game, 'disable')

        for game in game_icons:
            if event.type() == QEvent.MouseButtonPress and source is game:
                self.selected_game_source = game
                for i in game_icons:
                    if i == self.selected_game_source:
                        self.set_game_state(i, 'enable')
                    else:
                        self.set_game_state(i, 'disable')
                if source in [self.d_pokedex_g_1_1, self.d_pokedex_g_2_1]:
                    self.game_selected = self.game_versions[0]
                elif source == self.d_pokedex_g_2_2:
                    self.game_selected = self.game_versions[1]
                self.set_pokedex()

        # Pokemon Mode View Buttons

        for mode_btn in self.mode_btns:
            button_style = '#' + mode_btn[1].objectName() + ':flat {border: none}' \
                            '#' + mode_btn[1].objectName() + ' {background-image: url(:/img/buttons/pokemon/'\
                            + mode_btn[1].objectName()

            if event.type() == QEvent.Enter and source == mode_btn[1]:
                source.setStyleSheet(button_style + '_h.png);}')

            if event.type() == QEvent.Leave and source == mode_btn[1] and mode_btn[0] != self.pokemon_display_page:
                source.setStyleSheet(button_style + '.png);}')

        if self.pokemon:
            # Pokemon Sprites - Shiny on Hover
            if event.type() == QEvent.Enter and \
                    (source == self.d_pkmn_i_2_sprite_b or source == self.d_pkmn_i_2_sprite_f):
                self.set_sprites(True)
            if event.type() == QEvent.Leave and \
                    (source == self.d_pkmn_i_2_sprite_b or source == self.d_pkmn_i_2_sprite_f):
                self.set_sprites(False)

            if event.type() == QEvent.Enter and source in self.ability_names:
                if source.objectName() == 'd_pkmn_i_2_i_d_ability_1':
                    if self.pokemon['abilities'][0]:
                        self.statusbar.showMessage(self.pokemon['abilities'][0][1], 10000)
                elif source.objectName() == 'd_pkmn_i_2_i_d_ability_2':
                    if self.pokemon['abilities'][1]:
                        self.statusbar.showMessage(self.pokemon['abilities'][1][1], 10000)
                elif source.objectName() == 'd_pkmn_i_2_i_d_hidden_ability':
                    if self.pokemon['abilities'][2]:
                        self.statusbar.showMessage(self.pokemon['abilities'][2][1], 10000)

        return super(MainWindow, self).eventFilter(source, event)


def main():
    app = QApplication(sys.argv)
    main = MainWindow()

    global_css = "css/global.css"
    with open(global_css, "r") as css:
        app.setStyleSheet(css.read())

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
