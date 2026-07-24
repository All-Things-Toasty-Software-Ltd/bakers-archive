from odoo import fields, models


class BakersArchiveCoreTag(models.Model):
    _name = 'bakers_archive.core.tag'
    _description = 'Bakers Archive Core Tag'

    recipe_id = fields.Many2many('bakers_archive.core.recipe', String='Recipes')

    tag = fields.Char(string='Tag')
