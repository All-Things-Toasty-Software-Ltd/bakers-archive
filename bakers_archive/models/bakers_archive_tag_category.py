from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
from odoo.tools import html_escape


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
