import { DynamicSnippet } from "@website/snippets/s_dynamic_snippet/dynamic_snippet";
import { registry } from "@web/core/registry";

export class ArchiveRecipes extends DynamicSnippet {
    static selector = ".s_dynamic_snippet_archive_recipes";


    getSearchDomain() {
        const searchDomain = super.getSearchDomain(...arguments);
        const filterByArchiveId = parseInt(this.el.dataset.filterByArchiveId);
        if (filterByArchiveId >= 0) {
            searchDomain.push(["archive_id", "=", filterByArchiveId]);
        }
        return searchDomain;
    }
}

registry.category("public.interactions").add("bakers_archive.archive_recipes", ArchiveRecipes);

registry.category("public.interactions.edit").add("bakers_archive.archive_recipes", {
    Interaction: ArchiveRecipes,
});

registry.category("public.interactions.preview").add("bakers_archive.archive_recipes", {
    Interaction: ArchiveRecipes,
});
