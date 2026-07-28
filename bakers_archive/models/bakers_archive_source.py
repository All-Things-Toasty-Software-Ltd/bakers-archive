# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveSource(models.Model):
    _name = 'bakers_archive.source'
    _description = 'Bakers Archive Source'


    name = fields.Char(string='Name')
    type = fields.Char(string='Type')
    url = fields.Char(string='URL')
    notes = fields.Text(string='Notes')

    recipe_id = fields.Many2many('bakers_archive.recipe', string="Recipes")
