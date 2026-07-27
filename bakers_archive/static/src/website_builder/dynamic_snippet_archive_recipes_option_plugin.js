import {DYNAMIC_SNIPPET, setDatasetIfUndefined,} from "@website/builder/plugins/options/dynamic_snippet_option_plugin";
import {Plugin} from "@html_editor/plugin";
import {withSequence} from "@html_editor/utils/resource";
import {registry} from "@web/core/registry";
import {DynamicSnippetArchiveRecipesOption} from "./dynamic_snippet_archive_recipes_option";


class DynamicSnippetArchiveRecipesOptionPlugin extends Plugin {
    static id = "dynamicSnippetArchiveRecipesOption";
    static dependencies = ["dynamicSnippetOption"];
    static shared = ["fetchArchives", "getModelNameFilter"];
    modelNameFilter = "bakers_archive.recipe";
    resources = {
        builder_options: withSequence(DYNAMIC_SNIPPET, DynamicSnippetArchiveRecipesOption),
        on_snippet_dropped_handlers: this.onSnippetDropped.bind(this),
    };

    setup() {
        this.archives = undefined;
    }

    getModelNameFilter() {
        return this.modelNameFilter;
    }

    async onSnippetDropped({snippetEl}) {
        if (snippetEl.matches(DynamicSnippetArchiveRecipesOption.selector)) {
            setDatasetIfUndefined(snippetEl, "filterByArchiveId", -1);
            await this.dependencies.dynamicSnippetOption.setOptionsDefaultValues(
                snippetEl,
                this.modelNameFilter
            );
        }
    }

    async fetchArchives() {
        if (!this.archives) {
            this.archives = this._fetchArchives();
        }
        return this.archives;
    }

    async _fetchArchives() {
        const websiteDomain = [
            "|",
            ["website_id", "=", false],
            ["website_id", "=", this.services.website.currentWebsite.id],
        ];
        return this.services.orm.searchRead("bakers_archive.archive", websiteDomain, ["id", "name"]);
    }
}

registry
    .category("website-plugins")
    .add(DynamicSnippetArchiveRecipesOptionPlugin.id, DynamicSnippetArchiveRecipesOptionPlugin);
