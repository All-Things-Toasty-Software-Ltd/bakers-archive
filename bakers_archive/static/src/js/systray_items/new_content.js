import {
    NewContentSystrayItem,
    MODULE_STATUS,
} from "@website/client_actions/website_preview/new_content_systray_item";
import { patch } from "@web/core/utils/patch";

patch(NewContentSystrayItem.prototype, {
    setup() {
        super.setup();

        let newArchiveElement = this.state.newContentElements.find(
            (element) => element.moduleXmlId === "base.module_bakers_archive"
        );

        if (!newArchiveElement) {
            newArchiveElement = {
                moduleXmlId: "base.module_bakers_archive",
                title: "Recipe",
            };
            this.state.newContentElements.push(newArchiveElement);
        }

        newArchiveElement.createNewContent = () =>
            this.onAddContent(
                "bakers_archive.bakers_archive_recipe_action_add",
                true,
                this.getCurrentArchiveContext()
            );
        newArchiveElement.status = MODULE_STATUS.INSTALLED;
        newArchiveElement.model = "bakers_archive.recipe";
    },

    getCurrentArchiveContext() {
        const iframeEl = document.querySelector("iframe")?.contentDocument;
        if (!iframeEl) return null;

        const isArchivePage = iframeEl.documentElement?.dataset?.mainObject?.startsWith("archive");

        if (isArchivePage) {
            const archiveEl = iframeEl.querySelector("#wrap.bakers_archive [data-oe-model='bakers_archive.archive']");
            const archiveId = parseInt(archiveEl?.dataset?.oeId, 10);

            if (archiveId) {
                return { default_archive_id: archiveId };
            }
        }
        return null;
    },
});