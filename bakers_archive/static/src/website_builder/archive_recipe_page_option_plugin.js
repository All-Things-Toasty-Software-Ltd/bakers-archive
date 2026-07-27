import {Plugin} from "@html_editor/plugin";
import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {BaseOptionComponent} from "@html_builder/core/utils";

export class ArchiveRecipePageOption extends BaseOptionComponent {
    static template = "bakers_archive.archiveRecipePageOption";
    static selector = "main:has(#o_barchive_index_content)";
    static title = _t("Archives Page");
    static groups = ["website.group_website_designer"];
    static editableOnly = false;
}

export class ArchiveRecipePageOptionPlugin extends Plugin {
    static id = "archiveRecipePageOption";
    /** @type {import("plugins").WebsiteResources} */
    resources = {
        builder_options: [ArchiveRecipePageOption],
    };
}

registry.category("website-plugins").add(ArchiveRecipePageOptionPlugin.id, ArchiveRecipePageOptionPlugin);
