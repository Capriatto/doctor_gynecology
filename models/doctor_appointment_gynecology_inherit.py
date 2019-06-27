# -*- encoding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
import base64
import sys, os

class doctor_appointment(osv.osv):

	_name = "doctor.appointment"
	_inherit = "doctor.appointment"

	_columns = {
		'attentiont_gynecology_id': fields.many2one('doctor.attentions.gynecology', 'Attentiont', ondelete='restrict', readonly=True),
	}


	def create_attentiont_gynecology(self, cr, uid, doctor_appointment, modelo_crear,  context={}):
		"""
		Method that creates an attention from given data.
		@param doctor_appointment: Appointment method get data from.
		"""
		attentiont_obj = modelo_crear
		# Create attentiont object
		attentiont = {
			'patient_id': doctor_appointment.patient_id.id,
			'professional_id': doctor_appointment.professional_id.id,
			'origin': doctor_appointment.number,
		}
		# Get other attentiont values from appointment partner
		context['patient_id'] = doctor_appointment.patient_id.id
		attentiont_id = attentiont_obj.create(cr, uid, attentiont, context=context)
		# Create number attentiont record
		attentiont_number = {
			'attentiont_gynecology_id': attentiont_id,
		}

		self.pool.get('doctor.appointment').write(cr, uid, [doctor_appointment.id], attentiont_number, context=context)

		return attentiont_id



	def generate_attentiont(self, cr, uid, ids, context={}):
		
		doctor_appointment_variable = self.browse(cr, uid, ids, context=context)[0]
		#attentiont_id = self.create_attentiont(cr, uid, doctor_appointment_variable, context=context)
		# Update appointment state
		appointment_state = doctor_appointment_variable.state

		tipo_historia = doctor_appointment_variable.type_id.modulos_id.name
		_logger.info("==============> %s" % tipo_historia)
		
		#modelo = self.pool.get('doctor.doctor').tipo_historia(tipo_historia)

	
		
		#self.pool.get('doctor.doctor').obtener_ultimas_atenciones_paciente(cr, uid, modelo, 2, doctor_appointment_variable.patient_id.id, doctor_appointment_variable.time_begin, context=context)
		
		if appointment_state != 'invoiced':
			self.write(cr, uid, doctor_appointment_variable.id, {'state': 'attending'}, context=context)
		self.write(cr, uid, doctor_appointment_variable.id, {'attended': True}, context=context)
		# Get appoinment type
		tipo_historia = doctor_appointment_variable.type_id.modulos_id.name
		tipo_cita = doctor_appointment_variable.type_id.name
		profesional_id = doctor_appointment_variable.schedule_id.professional_id.id


		if tipo_historia == "doctor" or tipo_historia == "l10n_co_doctor":
			attentiont_id = self.create_attentiont(cr, uid, doctor_appointment_variable, context=context)
		#GET model of the viewpg 
		data_obj = self.pool.get('ir.model.data')

		if tipo_historia == 'doctor_psychology'  :
			attentiont_id = self.create_attentiont_psicologia(cr, uid, doctor_appointment_variable, self.pool.get('doctor.psicologia'), context=context)
			result = data_obj._get_id(cr, uid, 'doctor_psychology', 'doctor_psicologia_form_view')
			view_id = data_obj.browse(cr, uid, result).res_id
			context['default_patient_id'] = context.get('patient_id')
			context['default_professional_id'] = profesional_id
			return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'doctor.psicologia',
				'res_id': attentiont_id or False,
				'view_id': [view_id] or False,
				'type': 'ir.actions.act_window',
				'context' : context or None,
				'nodestroy': True,
			}

		if self.pool.get('doctor.doctor').modulo_instalado(cr, uid, 'doctor_control', context=context):
			
			if tipo_historia == 'doctor_control'  :
				context['default_patient_id'] = context.get('patient_id')
				context['default_professional_id'] = profesional_id
				context['tipo_cita_id'] = tipo_cita
				attentiont_id = self.create_attentiont_control(cr, uid, doctor_appointment_variable, self.pool.get('doctor.hc.control'), context=context)
				result = data_obj._get_id(cr, uid, 'doctor_control', 'doctor_hc_control_form_view')
				view_id = data_obj.browse(cr, uid, result).res_id
				return {
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'doctor.hc.control',
					'res_id': attentiont_id or False,
					'view_id': [view_id] or False,
					'type': 'ir.actions.act_window',
					'context' : context or None,
					'nodestroy': True,
				}

		if self.pool.get('doctor.doctor').modulo_instalado(cr, uid, 'doctor_dental_care', context=context):

			if tipo_historia == u'doctor_dental_care':
				attentiont_id = self.create_attentiont_psicologia(cr, uid, doctor_appointment_variable, self.pool.get('doctor.hc.odontologia'), context=context)
				result = data_obj._get_id(cr, uid, 'doctor_dental_care', 'view_doctor_hc_odonto_form')
				view_id = data_obj.browse(cr, uid, result).res_id
				context['default_patient_id'] = context.get('patient_id')
				context['default_professional_id'] = profesional_id
				return {
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'doctor.hc.odontologia',
					'res_id': attentiont_id or False,
					'view_id': [view_id] or False,
					'type': 'ir.actions.act_window',
					'context' : context or None,
					'nodestroy': True,
				}

		if self.pool.get('doctor.doctor').modulo_instalado(cr, uid, 'doctor_biological_risk', context=context):

			if tipo_historia == u'doctor_biological_risk':
				attentiont_id = self.create_attentiont_psicologia(cr, uid, doctor_appointment_variable, self.pool.get('doctor.atencion.ries.bio'), context=context)
				result = data_obj._get_id(cr, uid, 'doctor_biological_risk', 'doctor_atencion_ries_bio_form_view')
				view_id = data_obj.browse(cr, uid, result).res_id
				context['default_patient_id'] = context.get('patient_id')
				context['default_professional_id'] = profesional_id
				return {
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'doctor.atencion.ries.bio',
					'res_id': attentiont_id or False,
					'view_id': [view_id] or False,
					'type': 'ir.actions.act_window',
					'context' : context or None,
					'nodestroy': True,
				}

		if self.pool.get('doctor.doctor').modulo_instalado(cr, uid, 'doctor_pediatrics', context=context):
			
			if tipo_historia == u'doctor_pediatrics':
				context['default_patient_id'] = context.get('patient_id')
				context['default_professional_id'] = profesional_id
				context['tipo_cita_id'] = tipo_cita
				attentiont_id = self.create_attentiont_pediatrics(cr, uid, doctor_appointment_variable, self.pool.get('doctor.attentions.pediatrics'), context=context)
				result = data_obj._get_id(cr, uid, 'doctor_pediatrics', 'view_doctor_attentions_pediatrics_form')
				view_id = data_obj.browse(cr, uid, result).res_id
				return {
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'doctor.attentions.pediatrics',
					'res_id': attentiont_id or False,
					'view_id': [view_id] or False,
					'type': 'ir.actions.act_window',
					'context' : context or None,
					'nodestroy': True,
				}


		if self.pool.get('doctor.doctor').modulo_instalado(cr, uid, 'doctor_gynecology', context=context):
			
			if tipo_historia == u'doctor_gynecology':
				context['default_patient_id'] = context.get('patient_id')
				context['default_professional_id'] = profesional_id
				context['tipo_cita_id'] = tipo_cita
				context['default_patient_birth_date'] = doctor_appointment_variable.patient_id.birth_date
				context['default_patient_sex'] = doctor_appointment_variable.patient_id.sex
				context['default_patient_beliefs'] = doctor_appointment_variable.patient_id.creencias
				context['default_patient_educational_level'] = doctor_appointment_variable.patient_id.nivel_educativo

				
				attentiont_id = self.create_attentiont_gynecology(cr, uid, doctor_appointment_variable, self.pool.get('doctor.attentions.gynecology'), context=context)
				result = data_obj._get_id(cr, uid, 'doctor_gynecology','view_doctor_attentions_gynecology_form')
				view_id = data_obj.browse(cr, uid, result).res_id
				return {
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'doctor.attentions.gynecology',
					'res_id': attentiont_id or False,
					'view_id': [view_id] or False,
					'type': 'ir.actions.act_window',
					'context' : context or None,
					'nodestroy': True,
				}



		if tipo_historia == "doctor" or tipo_historia == "l10n_co_doctor":
			# Get view to show
			result = data_obj._get_id(cr, uid, 'doctor', 'view_doctor_attentions_form')
			view_id = data_obj.browse(cr, uid, result).res_id

			return {
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'doctor.attentions',
				'res_id': attentiont_id or False,
				'view_id': [view_id],
				'type': 'ir.actions.act_window',
				'context' : context,
				'nodestroy': True,
			}

		return True

doctor_appointment()
