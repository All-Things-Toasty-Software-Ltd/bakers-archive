# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

import random
from datetime import datetime
from odoo import api, models, fields, _
from odoo.addons.website.tools import text_from_html
from odoo.tools import html_escape
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate


class BakersArchiveTagCategory(models.Model):
    _name = 'bakers_archive.tag.category'
    _description = 'Bakers Archive Tag Category'
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    tag_ids = fields.One2many('bakers_archive.tag', 'category_id', string='Tags')

    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!',
    )
