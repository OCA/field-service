/** @odoo-module **/
import {FormController} from "@web/views/form/form_controller";
import {_t} from "@web/core/l10n/translation";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class GeolocateButtonController extends FormController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    getCurrentPositionPromise(options = {}) {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, options);
        });
    }

    async geolocate() {
        if (!navigator.geolocation) {
            this.notification.add(_t("Your browser does not allow Gelocalization"), {
                type: "danger",
            });
            return;
        }

        await this.model.root.save({reload: true});
        await this.model.root.load();
        let position = null;
        try {
            position = await this.getCurrentPositionPromise({enableHighAccuracy: true});
        } catch (error) {
            this.notification.add(
                _t("Error ocurred when getting the location: " + error.message),
                {
                    type: "danger",
                }
            );
            return;
        }

        const {latitude: lat, longitude: lon} = position.coords;

        try {
            const location = await this.orm.call(
                "fsm.order",
                "save_location_from_browser",
                [[this.model.root.resId], lat, lon]
            );

            this.model.root.update({
                location_id: [location.id, location.name],
            });
            await this.model.root.load();
            this.notification.add(_t("Location saved correctly"), {
                type: "success",
            });
        } catch (error) {
            this.notification.add(
                _t("Error when saving the location: " + error.message),
                {
                    type: "danger",
                }
            );
        }
    }
}

GeolocateButtonController.template = "fieldservice_current_location.GeolocateButton";

export const modelInfoView = {
    ...formView,
    Controller: GeolocateButtonController,
};

registry.category("views").add("geolocate_button", modelInfoView);
