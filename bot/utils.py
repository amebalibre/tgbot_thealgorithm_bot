# -*- coding: utf-8 -*-

import re
from settings import Settings

FILTERS = ('l.', 'n.', 'h.', 't.', 's.', 'i.', 'r.', 'e.')
WEB_FILTERS = ('lang', 'name', 'house', 'type', 'subtype', 'id', 'rarity', 'expansion')


class Utils:

    def verbalize_params(self, raw):
        """Read raw and extract the params.
        :param raw:
        :return: params list
        """
        params = []
        for m in re.findall(Settings.PATTERN_FILTER, raw):
            key = WEB_FILTERS[FILTERS.index(m[1:3])]
            value = m[3:]
            params.append('%s=%s' % (key, value))
        return params
