# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveLicense(models.Model):
    _name = "bakers_archive.license"
    _description = "Bakers Archive License"

    name = fields.Char(string="License")
    short_name = fields.Char(string="Short Name")
    url = fields.Char(string="URL")
    description = fields.Text(string="Description")
    recipe_ids = fields.Many2many('bakers_archive.recipe', string='Recipes')
