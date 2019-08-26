# -*- coding: utf-8 -*-
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
###############################################################################

import time
from openerp.report import report_sxw
from openerp import pooler
import logging
_logger = logging.getLogger(__name__)


class doctor_gynecology_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(doctor_gynecology_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'select_escolaridad': self.select_escolaridad,
			'regular': self.regular,
			'check_fur': self.check_fur,
			'check_fup': self.check_fup,
			'check_fecha_legrado': self.check_fecha_legrado,
			'check_fecha_cesarea': self.check_fecha_cesarea
		})
		
	def select_escolaridad(self, patient_educational_level):
		tipo = ''
		if patient_educational_level == '1':
			tipo='Pregrado'
		elif patient_educational_level == '2':
			tipo='Postgrado'
		elif patient_educational_level == '3':
			tipo='Maestrías'
		elif patient_educational_level == '4':
			tipo='Especialización'
		elif patient_educational_level == '5':
			tipo='Jardín'
		elif patient_educational_level == '6':
			tipo='Primaria'
		return tipo

	
	def regular(self, regular):
		if regular:
			return 'Si'
		else:
			return ''

	def check_fur(self, fur):
		if fur == 'False':
			return ''
		else:
			return fur

	def check_fup(self, fup):
		if fup == 'False':
			return ''
		else:
			return fup

	def check_fecha_legrado(self, legrados_fecha):
		if legrados_fecha == 'False':
			return ''
		else:
			return legrados_fecha

	def check_fecha_cesarea(self, cesareas_fecha):
		if cesareas_fecha == 'False':
			return ''
		else:
			return cesareas_fecha


report_sxw.report_sxw('report.doctor.gynecology.report','doctor.attentions.gynecology','addons/doctor_gynecology/report/doctor_gynecology_report.rml', parser=doctor_gynecology_report)
