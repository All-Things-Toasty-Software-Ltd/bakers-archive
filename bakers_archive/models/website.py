# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Website(models.Model):
    _inherit = 'website'

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_("Baker's Archive"), self.env['ir.http']._url_for('/archive'), 'bakers_archive'))
        return suggested_controllers

    def configurator_set_menu_links(self, menu_company, module_data):
        archives = module_data.get('#archive', [])
        for idx, archive in enumerate(archives):
            new_archive = self.env['bakers_archive.archive'].create({
                'name': archive['name'],
                'website_id': self.id,
            })
            archive_menu_values = {
                'name': archive['name'],
                'url': '/archive/%s' % new_archive.id,
                'sequence': archive['sequence'],
                'parent_id': menu_company.id if menu_company else self.menu_id.id,
                'website_id': self.id,
            }
            if idx == 0:
                archive_menu = self.env['website.menu'].search([('url', '=', '/archive'), ('website_id', '=', self.id)])
                archive_menu.write(archive_menu_values)
            else:
                self.env['website.menu'].create(archive_menu_values)
        super().configurator_set_menu_links(menu_company, module_data)

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['archives', 'archives_only', 'all']:
            result.append(self.env['bakers_archive.archive']._search_get_detail(self, order, options))
        if search_type in ['archives', 'archive_recipes_only', 'all']:
            result.append(self.env['bakers_archive.recipe']._search_get_detail(self, order, options))
        return result
