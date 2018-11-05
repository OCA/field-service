odoo.define('fsm_base.stage_list_widget', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
    var Field = field_registry.get('char');
    var rpc = require('web.rpc');

    var FieldStageList = Field.extend({

        template: 'FieldStageList',
        widget_class: 'o_statusbar_status',
        events: {
            'click div.stage': 'onclick_stage'
        },

        init: function () {
            this._super.apply(this, arguments);
            this.stage_set = this.recordData.stage_set.data.id;
            this.stage_list = [];
            this.stage_id = this.recordData.stage_id ? this.recordData.stage_id.data.id:null;
        },
        update_stages_list: function () {
            var self = this;
            var stage_str = '';
            rpc.query({
                model: 'fsm.work_set',
                method: 'fetch_stages_list',
                args: [self.stage_set]
            }).done(function (res) {
                self.stage_list = res;
                for (var i in res){
                    var div_class = "stage btn-sm o_arrow_button";
                    if (self.stage_id && self.stage_id === res[i].id) {
                        div_class += " active";
                    }
                    stage_str += '<div class="'+div_class+'" >' +
                        '<span data-name="'+res[i].name+'" data-id="'+res[i].id+'">' + res[i].name +
                        '</span></div>';
                }
                stage_str = $(stage_str);
                $('.o_statusbar_status').empty();
                self.$el.append(stage_str);
            });
        },
        _render: function () {
            if( this.stage_set){
                this.update_stages_list();
            }

            this._super.apply(this, arguments);
        },
        onclick_stage: function (event) {
            var self = this;
            var stage_id, stage_name;
            try {
                stage_id = $(event.target).attr('data-id');
                stage_name = $(event.target).attr('data-name');
            }
            catch (err) {}
            if (stage_id) {
                rpc.query({
                    model: 'fsm.work_set',
                    method: 'stage_transition',
                    args: [
                        self.recordData.id,
                        stage_id,
                        stage_name
                    ]
                }).done(function () {
                    self.stage_id = parseInt(stage_id);
                    self.update_stages_list();
                });
            }
        }
    });

    field_registry.add('fsm_stage_list', FieldStageList);

    return {
        FieldStageList: FieldStageList
    };

});
