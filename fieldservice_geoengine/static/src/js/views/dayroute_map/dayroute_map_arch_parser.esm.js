/** @odoo-module **/

import {Field} from "@web/views/fields/field";
import {visitXML} from "@web/core/utils/xml";

export class DayrouteMapArchParser {
    parse(xmlDoc, models, modelName) {
        const fieldNodes = {};
        visitXML(xmlDoc, (node) => {
            if (node.tagName === "field") {
                const fieldInfo = Field.parseFieldNode(
                    node,
                    models,
                    modelName,
                    "dayroute_map"
                );
                fieldNodes[fieldInfo.name] = fieldInfo;
            }
        });
        const limit = xmlDoc.getAttribute("limit");
        return {
            activeFields: fieldNodes,
            fieldNodes,
            limit: limit && parseInt(limit, 10),
        };
    }
}
