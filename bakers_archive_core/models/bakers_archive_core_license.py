from odoo import fields, models


class BakersArchiveCoreLicense(models.Model):
    _name = "bakers_archive.core.license"
    _description = "Bakers Archive Core License"

    license = fields.Char(string="License")
    short_name = fields.Char(string="Short Name")
    url = fields.Char(string="URL")
    description = fields.Text(string="Description")
    recipe_ids = fields.Many2many('bakers_archive.core.recipe', string='Recipes')
