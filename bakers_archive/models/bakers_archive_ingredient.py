# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveIngredient(models.Model):
    _name = 'bakers_archive.ingredient'
    _description = 'Bakers Archive Ingredient'
    # website.seo.metadata gives the ingredient page proper title/meta tags when it's
    # set as the main_object, like the archive pages do.
    _inherit = [
        'website.seo.metadata',
    ]
    _order = 'name'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')

    recipe_ingredient_id = fields.One2many('bakers_archive.recipe.ingredient', 'name',
                                           string='Recipe Ingredient')
