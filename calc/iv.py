from math import floor

class IVs:
    def calc_ivs(self):
        lvl = self.d_pkmn_i_2_i_iv_level
        ev = self.d_pkmn_i_2_i_iv_effort

        values = {}
        stats = self.pokemon['stats']

        try:
            value_lvl = int(lvl.text())
        except ValueError:
            value_lvl = None
        try:
            value_ev = int(ev.text())
        except ValueError:
            value_ev = None

        if value_lvl and 0 <= value_lvl <= 100:
            values['lvl'] = value_lvl
        elif not value_lvl:
            lvl.clear()
        elif value_lvl > 100:
            lvl.clear()
            self.statusbar.showMessage('Please input only numbers in the range 0 to 100.', 8000)

        if value_ev and 0 <= value_ev <= 255:
            values['ev'] = value_ev
        elif not value_ev:
            ev.clear()
        elif value_ev > 255:
            ev.clear()
            self.statusbar.showMessage('Please input only numbers in the range 0 to 255.', 8000)

        def calc_min_iv(stat_type, stat, level, effort, nature):
            if 2 <= stat_type <= 6:
                calculated_value = floor(((floor(((2 * stat + floor(effort / 4)) * level) / 100)) + 5) * nature)
            elif stat_type == 1:
                calculated_value = int((((2 * stat + floor(effort / 4)) * level) / 100) + level + 10)
            return calculated_value

        def calc_max_iv(stat_type, stat, level, effort, nature):
            if 2 <= stat_type <= 6:
                calculated_value = floor(((floor(((2 * stat + 31 + floor(effort / 4)) * level) / 100)) + 5) * nature)
            elif stat_type == 1:
                calculated_value = int((((2 * stat + 31 + floor(effort / 4)) * level) / 100) + level + 10)
            return calculated_value

        calculated_values = {}

        if len(values) == 2:
            level = values['lvl']
            effort = values['ev']
            min_values = []
            max_values = []
            for i in range(1, 7):
                for s in stats:
                    if s[0] == i:
                        min_val = calc_min_iv(s[0], s[1], level, effort, 1)  # TODO nature
                        min_values.append(min_val)
                        max_val = calc_max_iv(s[0], s[1], level, effort, 1)  # TODO nature
                        max_values.append(max_val)

            calculated_values['min'] = min_values
            calculated_values['max'] = max_values

            self.calculated_ivs = calculated_values
            self.set_calculated_ivs()
