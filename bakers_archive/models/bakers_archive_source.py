from odoo import fields, models


class BakersArchiveSource(models.Model):
    _name = 'bakers_archive.source'
    _description = 'Bakers Archive Source'

    recipe_id = fields.Many2many('bakers_archive.recipe', String="Recipes")

    name = fields.Char(string='Name')
    type = fields.Char(string='Type')
    url = fields.Char(string='URL')
    notes = fields.Text(string='Notes')
