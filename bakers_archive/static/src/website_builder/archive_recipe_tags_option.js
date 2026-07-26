import { BaseOptionComponent, useDomState } from "@html_builder/core/utils";

export class ArchiveRecipeTagsOption extends BaseOptionComponent {
    static template = "bakers_archive.ArchiveRecipeTagsOption";
    static selector = ".o_barchive_post_page_cover[data-res-model='bakers_archive.post']";
    static editableOnly = false;

    setup() {
        super.setup();
        this.domState = useDomState((el) => ({
            archiveId: parseInt(el.dataset.resId),
        }));
    }
}
