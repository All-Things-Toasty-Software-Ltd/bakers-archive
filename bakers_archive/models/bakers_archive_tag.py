from odoo import fields, models


class BakersArchiveTag(models.Model):
    _name = 'bakers_archive.tag'
    _description = 'Bakers Archive Tag'

    recipe_id = fields.Many2many('bakers_archive.recipe', String='Recipes')

    tag = fields.Char(string='Tag')
