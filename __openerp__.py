# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP S.A (<http://www.openerp.com>).
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

{
    'name' : 'doctor_gynecology',
    'version': '1.0',
    'depends': ['doctor', 'l10n_co_doctor'],
    'author': 'DracoSoft',
    'category': 'medical',
    'description': 
    """
    H.C Gynecology
    """,
    'website': '',
    'data': [
        'data/report_doctor_gynecology.xml',
        'views/doctor_sequence.xml',
        'data/appointment_type.sql',
        'security/doctor_security.xml',
        'security/ir.model.access.csv',
        'views/doctor_attentions_gynecology_view.xml',
        'views/doctor_patient_gynecology_inherit_view.xml',
        'views/doctor_appointment_inherit_view.xml'

    ],
    'demo': [''],
    'css': ['static/src/css/style.css'],
    'js' : ['static/src/js/javascript.js'],

    'auto_install': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
