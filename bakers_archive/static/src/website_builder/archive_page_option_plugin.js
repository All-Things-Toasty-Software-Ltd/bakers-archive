import {BaseOptionComponent} from "@html_builder/core/utils";
import {Plugin} from "@html_editor/plugin";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

export class ArchivePageOption extends BaseOptionComponent {
    static template = "bakers_archive.ArchivePageOption";
    static selector = "main:has(#o_barchive_recipe_main)";
    static title = _t("Archive Page");
    static groups = ["website.group_website_designer"];
    static editableOnly = false;
}

export class ArchivePageOptionPlugin extends Plugin {
    static id = "archivePageOption";
    /** @type {import("plugins").WebsiteResources} */
    resources = {
        builder_options: [ArchivePageOption],
        content_not_editable_selectors: [".o_list_cover"],
    };
}

registry.category("website-plugins").add(ArchivePageOptionPlugin.id, ArchivePageOptionPlugin);
