# -*- coding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
_logger = logging.getLogger(__name__)
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class doctor_patient(osv.osv):

	_name = 'doctor.patient'

	_inherit = 'doctor.patient'


	_columns = {
		'attentions_gynecology_ids': fields.one2many('doctor.attentions.gynecology', 'patient_id', 'Atenciones Ginecología'),
	}

	def calcular_edad(self, fecha_nacimiento):
		current_date = datetime.today()
		st_birth_date = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
		re = current_date - st_birth_date
		dif_days = re.days
		age = dif_days
		age_unit = ''
		if age < 30:
			age_attention = age,
			age_unit = '3'

		elif age > 30 and age < 365:
			age = age / 30
			age = int(age)
			age_attention = age,
			age_unit = '2'

		elif age >= 365:
			age = int((current_date.year - st_birth_date.year - 1) + (
				1 if (current_date.month, current_date.day) >= (st_birth_date.month, st_birth_date.day) else 0))
			age_attention = age,
			age_unit = '1'

		return age

	def calcular_age_unit(self, fecha_nacimiento):
		current_date = datetime.today()
		st_birth_date = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
		re = current_date - st_birth_date
		dif_days = re.days
		age = dif_days
		age_unit = ''
		if age < 30:
			age_unit = '3'
		elif age > 30 and age < 365:
			age_unit = '2'

		elif age >= 365:
			age_unit = '1'

		return age_unit

	def atender_paciente_gynecology(self, cr, uid, ids, context=None):
		try:
			professional_id= self.pool.get('doctor.professional').browse(cr, uid, self.pool.get('doctor.professional').search(cr, uid, [( 'user_id',  '=', uid)]))[0].id	
		except Exception as e:
			professional_id= None
			_logger.info("Error en doctor_patient_gynecology ===>  %s", e)
			

		for paciente in self.browse(cr,uid,ids):
			
			paciente_id = paciente.id
			context['default_patient_id'] = paciente_id
			context['default_professional_id'] = professional_id
			context['defaut_patient_birth_date']= paciente.birth_date
			context['default_patient_sex'] = paciente.sex
			context['default_age_attention'] = self.calcular_edad(paciente.birth_date)
			context['default_age_unit'] = self.calcular_age_unit(paciente.birth_date)
			context['default_patient_educational_level'] = paciente.nivel_educativo
			context['default_patient_beliefs'] = paciente.creencias

			return {
				'type': 'ir.actions.act_window',
				'name': 'Hc Atencion Ginecologia',
				'view_type': 'form',
				'view_mode': 'form',
				'res_id': False,
				'res_model': 'doctor.attentions.gynecology',
				'context': context or None,
				'view_id': False,
				'nodestroy': False,
				'target': 'current'
			}





doctor_patient()