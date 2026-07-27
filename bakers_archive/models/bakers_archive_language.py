# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveLanguage(models.Model):
    _name = 'bakers_archive.language'
    _description = 'Bakers Archive Language'

    name = fields.Char(string='Language', required=True)
    recipe_ids = fields.Many2many('bakers_archive.recipe', string='Recipes')
