odoo.define('kaf-contacts-base.PartnerDetailsEdit', function(require) {
    'use strict';

    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');
	const rpc = require('web.rpc');
	const { onMounted, onWillUnmount } = owl;

    const PartnerDetailsEditVat = PartnerDetailsEdit =>
        class extends PartnerDetailsEdit {
            setup() {
	            super.setup(...arguments);
				this.intFields = ['country_id', 'state_id', 'property_product_pricelist','l10n_latam_identification_type_id','city_id','l10n_pe_district'];
				const partner = this.props.partner;
				this.changes = {
					'country_id': partner.country_id && partner.country_id[0],
					'state_id': partner.state_id && partner.state_id[0],
					'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id && partner.l10n_latam_identification_type_id[0],
					'city_id': partner.city_id && partner.city_id[0],
					'l10n_pe_district': partner.l10n_pe_district && partner.l10n_pe_district[0],
				};
				if (!partner.property_product_pricelist)
					this.changes['property_product_pricelist'] = this.env.pos.default_pricelist.id;
					
				onMounted(() => {
					this.iniciarDatos_vat_pe();
				});
	        }

	        iniciarDatos_vat_pe(){
	        	var self = this;
				$('.busqueda-datos').off('click', '');
		        $('.busqueda-datos').on('click', self._busquedaContacto.bind(self));
				this.id_pais = this.changes.country_id ? parseInt(this.changes.country_id) : parseInt(this.env.pos.company.country_id)
				this._hideshowPeru();
				this.id_departamento = this.changes.state_id || this.env.pos.company.state_id || false;
				this.id_provincia = this.changes.city_id || this.env.pos.company.city_id || false;
				this.id_distrito = this.changes.l10n_pe_district || this.env.pos.company.l10n_pe_district || false;
				this.id_doctype = this.changes.l10n_latam_identification_type_id;
				this._changeTypeIdentification();
		        $('.client-address-country').on('change', self._changeCountry.bind(self));
		        $('.client-address-states').on('change', self._changeState.bind(self));
		        $('.client-address-provincia').on('change', self._changeProvincia.bind(self));
				$('.client-address-distrito').on('change', self._changeDistrito.bind(self));

				$('.l10n_latam_identification_type_id').on('change', self._changeTypeIdentification.bind(self));

				$('#vat').on('change', self._changeVat.bind(self));
				$('#street').on('change', self._changeStreet.bind(self));
				$('#name').on('change', self._changeName.bind(self));
				$('input[name="email"]').on('change', self._changeEmail.bind(self));
				$('input[name="phone"]').on('change', self._changePhone.bind(self));
				$('input[name="barcode"]').on('change', self._changeBarcode.bind(self));

				this.render(true);
			}
			_hideshowPeru(){
				let div = $(".client-address-country")[0];
				if(div.options[div.selectedIndex].text == 'Perú'){
		          $('#client-address-provincia').show();
		          $('#client-address-distrito').show();
				  $('#client-address-external-city').hide();
		        } else {
		          $('#client-address-provincia').hide();
		          $('#client-address-distrito').hide();
				  $('#client-address-external-city').show();
		        }
			}

			_changeCountry() {
				this.id_pais = this.changes.country_id
				this._hideshowPeru();
				$('#client-address-states').val('')
				this.changes['state_id'] = ""
				$('.client-address-provincia').val('')
				this.changes['city_id'] = ""
				$('.client-address-distrito').val('')
				this.changes['l10n_pe_district'] = ""
				this.render(true);
		    }
			getIdPais() {	
				return parseInt(this.id_pais) ;
			}
			
			_changeState() {
				this.id_departamento = this.changes.state_id;
				$('.client-address-provincia').val('')
				this.changes['city_id'] = ""
				this.id_provincia = this.changes.city_id;
				$('.client-address-distrito').val('')
				this.changes['l10n_pe_district'] = ""
				this.id_distrito = this.changes.l10n_pe_district;
				this.render(true);
		    }
			getIdState() {
				return parseInt(this.id_departamento);
			}
			_changeProvincia() {	
				this.id_provincia = this.changes.city_id;
				$('.client-address-distrito').val('')
				this.changes['l10n_pe_district'] = ""
				this.id_distrito = this.changes.l10n_pe_district;
				this.render(true);
		    }
			getIdProvincia() {
				return parseInt(this.id_provincia);
			}
			_changeDistrito(){
				this.id_distrito = this.changes.l10n_pe_district;
			}
			getIdDistrito(){
				return parseInt(this.id_distrito);
			}
			_changeTypeIdentification(){
				this.id_doctype = this.changes.l10n_latam_identification_type_id;
				let div2 = $(".l10n_latam_identification_type_id")[0];
				let tipo_doc = div2.options[div2.selectedIndex].text
				$('#busqueda-boton').show();
				if (tipo_doc == 'RUC'){
					$('#state-sunat-div').show();
					$('#condition-sunat-div').show();
					$('.client-type').val('company')
					this.changes['company_type'] = "company"
				}
				else{
					if(tipo_doc != 'DNI'){
						$('#busqueda-boton').hide();
					}
					$('.client-type').val('person')
					this.changes['company_type'] = "person"
					$('#state-sunat-div').hide();
					$('#condition-sunat-div').hide();
				}
				this.render(true);
			}
			getIdDocType(){
				return parseInt(this.id_doctype);
			}

			_changeVat(){
				let inputVat = $("#vat").val();
				this.vat = inputVat;
			}
			getVat(){
				return this.vat;
			}

			_changeStreet(){
				let inpurStreet = $("#street").val();
				this.street = inpurStreet;
			}
			getStreet(){
				return this.street;
			}

			_changeName(){
				let inputName = $("#name").val();
				this.name = inputName;
			}
			getName(){
				return this.name;
			}
			
			_changeEmail(){
				let inputEmail = $('input[name="email"]').val();
				this.email = inputEmail;
			}
			getEmail(){
				return this.email;
			}

			_changePhone(){
				let inputPhone = $('input[name="phone"]').val();
				this.phone = inputPhone;
			}
			getPhone(){
				return this.phone;
			}

			_changeBarcode(){
				let inputBarcode = $('input[name="barcode"]').val();
				this.barcode = inputBarcode;
			}
			getBarcode(){
				return this.barcode;
			}

			_changeCompanyType(){
				let inputCompanyType = $('input[name="company_type"]').val();
				this.company_type = inputCompanyType;
			}
			getCompanyType(){
				return this.company_type;
			}

			_changeZip(){
				let inputZip = $('input[name="zip"]').val();
				this.zip = inputZip;
			}
			getZip(){
				return this.zip;
			}

			_changeStateSunat(){
				let inputStateSunat = $('input[name="state_sunat"]').val();
				this.state_sunat = inputStateSunat;
			}
			getStateSunat(){
				return this.state_sunat;
			}

			_changeConditionSunat(){
				let inputConditionSunat = $('input[name="condition_sunat"]').val();
				this.condition_sunat = inputConditionSunat;
			}
			getConditionSunat(){
				return this.condition_sunat;
			}

			_busquedaActualizar(){
				let a = this.changes.city_id
				$(`.client-address-provincia option[value="${a}"]`).attr('selected', 'selected')
				let b = this.changes.l10n_pe_district;
				$(`.client-address-distrito option[value="${b}"]`).attr('selected', 'selected')
				//this.render(true);
			}

			_busquedaContacto(){
				var self = this;
		        if (!$("#vat").val()) {return;}
				let vat = $("#vat").val();
				let div2 = $(".l10n_latam_identification_type_id")[0];
				let tipo_doc = div2.options[div2.selectedIndex].text
				self.changes['l10n_latam_identification_type_id'] = div2.options[div2.selectedIndex].value
				self.changes['vat'] = vat
				//Filtros necesarios para correcto funcionamiento y no guardar vat repetidos
				if(tipo_doc == 'VAT' || (tipo_doc == 'RUC' && vat.substr(0,2) == '20')){
					$('.partner-detail input[name="company_type"]').val('company');
					self.changes['company_type'] = 'company';
				} else {
					$('.partner-detail input[name="company_type"]').val('person');
					self.changes['company_type'] = 'person';
				}
                if(tipo_doc != 'DNI' && tipo_doc !='RUC'){
                	return;
                }
				const regex = /^[0-9]*$/;
				if(tipo_doc == 'RUC'){
					if(vat.length != 11 || !regex.test(vat) || (vat.substr(0,2) != '20' && vat.substr(0,2) != '10') ) {
						self.showPopup('ErrorTracebackPopup', {
	                        'title': 'Alerta RUC!',
	                        'body': 'El RUC debe tener 11 dígitos, debe tener solo números y debe comenzar con 10 o 20',
	                    });
						return;
					}
				}
				else if(tipo_doc == 'DNI'){
					if(vat.length != 8 || !regex.test(vat)) {
						self.showPopup('ErrorTracebackPopup', {
	                        'title': 'Alerta DNI!',
	                        'body': 'El DNI debe tener 8 dígitos y debe tener solo números.',
	                    });
						return;
					}
				}

				let flag_busqueda = false ;
				let intervalBusqueda = setInterval(() =>{
					if(flag_busqueda){
						$('.busqueda-2').click()
					}
				}, 250);
				this.func_busqueda (tipo_doc, vat).then(() => {
					flag_busqueda = true;					
				}).finally(() => {
					setTimeout(() => {
						clearInterval(intervalBusqueda)
					},250)
				})
			}

			async func_busqueda (tipo_doc, vat) {
				var self = this
				let respuesta;
				let contents = $('.partner-details');
				let parametros = [tipo_doc == "DNI" ? "dni" : "ruc", vat]
				const response = await rpc.query({
					model: 'res.partner',
					method: 'consulta_datos',
					args: parametros,
				})
				if (response.error) {
					self.showPopup('ErrorTracebackPopup', {
						'title': 'Alerta de consulta!',
						'body': `${response.message}`,
					});
					return;
				} else if (response.data) {

					self.changes['zip'] = null;
					contents.find('input[name="zip"]').val('');
					self.changes['city_id'] = null;
					contents.find('select[name="city_id"]').val('');				
					self.changes['l10n_pe_district'] = null;
					contents.find('select[name="l10n_pe_district"]').val('');
					self.changes['name'] = null;
					contents.find('input[name="name"]').val('');
					self.changes['street'] = null;
					contents.find('input[name="street"]').val('');

					respuesta = response.data.data;
					contents.find('input[name="name"]').val(respuesta.name);
					self.changes['name'] = respuesta.name;
					self._changeName();
					contents.find('input[name="company_type"]').val(respuesta.company_type);
					self.changes['company_type'] = respuesta.company_type;
					self._changeCompanyType();
					contents.find('input[id="vat"]').val(respuesta.vat);
					self.changes['vat'] = respuesta.vat;
					self._changeVat();
					if (tipo_doc === 'RUC') {
						self._changeTypeIdentification();
						if (respuesta.zip){
							contents.find('input[name="zip"]').val(respuesta.zip);
							self.changes['zip'] = respuesta.zip;
							self._changeZip();
							
							self.changes['state_id'] = respuesta.state_id;
							contents.find('select[name="state_id"]').val(respuesta.state_id);
							self._changeState();								

							self.changes['city_id'] = respuesta.city_id;
							contents.find('select[name="city_id"]').val(respuesta.city_id);
							self._changeProvincia();
							
							self.changes['l10n_pe_district'] = respuesta.l10n_pe_district;
							contents.find('select[name="l10n_pe_district"]').val(respuesta.l10n_pe_district);
							self._changeDistrito();
						}
						contents.find('input[name="state_sunat"]').val(respuesta.state_sunat);
						self.changes['state_sunat'] = respuesta.state_sunat;
						self._changeStateSunat();
						contents.find('input[name="condition_sunat"]').val(respuesta.condition_sunat);
						self.changes['condition_sunat'] = respuesta.condition_sunat;
						self._changeConditionSunat();
						contents.find('input[name="street"]').val(respuesta.street);
						self.changes['street'] = respuesta.street;
						self._changeStreet();
						//Algunas advertencias
						let state_sunat = self.changes['state_sunat']
						if(state_sunat == 'ACTIVO') {
							$('#alerta-state-sunat').attr("hidden",true)
							$('.state-sunat-class').css("background", "#22e944c7")
						}
						else{
							$('#alerta-state-sunat').attr("hidden",false)
							$('.state-sunat-class').css("background", "#d96161c7")
						}
						let condition_sunat = self.changes['condition_sunat']
						if(condition_sunat == 'HABIDO') {
							$('#alerta-condition-sunat').attr("hidden",true)
							$('.condition-sunat-class').css("background", "#22e944c7")
						}
						else{
							$('#alerta-condition-sunat').attr("hidden",false)
							$('.state-sunat-class').css("background", "#d96161c7")
						}
					}
				}
			}
		}		

    Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditVat);

    return PartnerDetailsEdit;
});
