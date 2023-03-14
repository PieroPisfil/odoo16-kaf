odoo.define('point_of_sale.ConfirmSelectPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { useState } = owl;

    // formerly ConfirmSelectPopupWidget
    class ConfirmSelectPopup extends AbstractAwaitablePopup {
        /**
         * Value of the `item` key of the selected element in the Selection
         * Array is the payload of this popup.
         *
         * @param {Object} props
         * @param {String} [props.confirmText='Confirm']
         * @param {String} [props.cancelText='Cancel']
         * @param {String} [props.title='Select']
         * @param {String} [props.body='']
         * @param {Array<Selection>} [props.list=[]]
         *      Selection {
         *          id: integer,
         *          label: string,
         *          isSelected: boolean,
         *          item: any,
         *      }
         */
        setup() {
            super.setup();
            this.state = useState({ selectedId: this.props.list.find((item) => item.id > -2) });
        }
        isSelected(itemId){
            if (this.state.selectedId == itemId){
                return true
            }
            return false
        }
        selectItem(itemId) {
            this.state.selectedId = itemId;
        }
        confirmselect(){
            const selected = this.props.list.find((item) => this.state.selectedId === item.id);
            if(!selected){return}
            this.confirm();
        }
        /**
         * We send as payload of the response the selected item.
         *
         * @override
         */
        getPayload() {
            const selected = this.props.list.find((item) => this.state.selectedId === item.id);
            return selected && selected.item;
        }
    }
    ConfirmSelectPopup.template = 'ConfirmSelectPopup';
    ConfirmSelectPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: _lt('Confirm ?'),
        body: '',
        list: [],
        confirmKey: false,
    };

    Registries.Component.add(ConfirmSelectPopup);

    return ConfirmSelectPopup;
});
