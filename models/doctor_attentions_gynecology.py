# -*- coding: utf-8 -*-
import logging
from openerp.osv import osv, fields
from datetime import datetime, timedelta, date
from dateutil import relativedelta as rdelta
from openerp.tools.translate import _
import urllib
import urllib2
from dateutil.relativedelta import relativedelta
from unicodedata import normalize
import string

_logger = logging.getLogger(__name__)


class doctor_attentions_gynecology(osv.Model):
    _name = 'doctor.attentions.gynecology'
    _rec_name = 'number'
    _order = "date_attention desc"

    #Niveles de estudio
    educational_level = [
        ('5', 'JARDIN'),
        ('6', 'PRIMARIA'),
        ('7', 'SECUNDARIA'),
        ('1', 'PREGRADO'),
        ('2', 'POSGRADO'),
        ('3', u'MAESTRÍAS'),
        ('4', u'ESPECIALIZACIÓN'),
    ]


    def create(self, cr, uid, vals, context=None):
        # Set appointment number if empty
        if not vals.get('number'):
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'gyneco.sequence')
        return super(doctor_attentions_gynecology, self).create(cr, uid, vals, context=context)

    def button_closed(self, cr, uid, ids, context=None):
        ids_attention_past = self.pool.get('doctor.attentions.past').search(cr, uid, [('attentiont_id', '=', ids),
                                                                                      ('past', '=', False)],
                                                                            context=context)
        self.pool.get('doctor.attentions.past').unlink(cr, uid, ids_attention_past, context)

        ids_review_system = self.pool.get('doctor.review.systems').search(cr, uid, [('attentiont_id', '=', ids),
                                                                                    ('review_systems', '=', False)],
                                                                          context=context)
        self.pool.get('doctor.review.systems').unlink(cr, uid, ids_review_system, context)

        ids_examen_fisico = self.pool.get('doctor.attentions.exam').search(cr, uid, [('attentiont_id', '=', ids),
                                                                                     ('exam', '=', False)],
                                                                           context=context)
        self.pool.get('doctor.attentions.exam').unlink(cr, uid, ids_examen_fisico, context)
        return super(doctor_attentions_gynecology, self).write(cr, uid, ids, {'state': 'closed'}, context=context)

    def _previous(self, cr, uid, patient_id, type_past, attentiont_id=None):
        condition = [('patient_id', '=', patient_id.id)]
        if attentiont_id != None:
            condition.append(('attentiont_id', '<=', attentiont_id))
        if type_past == 'past':
            return self.pool.get('doctor.attentions.past').search(cr, uid, condition, order='id desc')
        if type_past == 'pathological':
            return self.pool.get('doctor.diseases.past').search(cr, uid, condition, order='id desc')
        if type_past == 'drugs':
            return self.pool.get('doctor.atc.past').search(cr, uid, condition, order='id desc')

    def _get_past(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for datos in self.browse(cr, uid, ids):
            res[datos.id] = self._previous(cr, uid, datos.patient_id, 'past', datos.id)
        return res

    def _get_pathological_past(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for datos in self.browse(cr, uid, ids):
            res[datos.id] = self._previous(cr, uid, datos.patient_id, 'pathological', datos.id)
        return res

    def _get_drugs_past(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for datos in self.browse(cr, uid, ids):
            res[datos.id] = self._previous(cr, uid, datos.patient_id, 'drugs', datos.id)
        return res

    _columns = {
        'patient_id': fields.many2one('doctor.patient', 'Patient', ondelete='restrict', readonly=True),
        'patient_photo': fields.related('patient_id', 'photo', type="binary", relation="doctor.patient", readonly=True),
        'date_attention': fields.datetime('Fecha Atención', required=True, readonly=True),
        'number': fields.char('Número Atención', select=1, size=32, readonly=True,
                              help="Número Antención. Esta secuencia será calculada automaticamente al guardar."),
        'origin': fields.char('Origen', size=64,
                              help="Reference of the document that produced this attentiont.", readonly=True),
        'age_attention': fields.integer('Current age', readonly=True),
        'age_unit': fields.selection([('1', 'Years'), ('2', 'Months'), ('3', 'Days'), ], 'Unit of measure of age',
                                     readonly=True),
        'age_patient_ymd': fields.char('Age in Years, months and days', size=30, readonly=True),

        'professional_id': fields.many2one('doctor.professional', 'Doctor', required=True, readonly=True),
        'speciality': fields.related('professional_id', 'speciality_id', type="many2one", relation="doctor.speciality",
                                     string='Speciality', required=False, store=True,
                                     states={'closed': [('readonly', True)]}),
        'professional_photo': fields.related('professional_id', 'photo', type="binary", relation="doctor.professional",
                                             readonly=True, store=False),
        'actual_disease': fields.text('Actual Disease', required=False, states={'closed': [('readonly', True)]}),
        'reason_consultation' : fields.char("Reason of Consultation", size=100, required=False, states={'closed': [('readonly', True)]}),
        

        'state': fields.selection([('open', 'Open'), ('closed', 'Closed')], 'Status', readonly=True, required=True),
        'tipo_historia': fields.char('tipo_historia', required=True),

        'patient_sex' : fields.selection([('m', 'Male'), ('f', 'Female'), ], 'Sex', select=True),
        'patient_educational_level': fields.selection(educational_level, 'Educational Level', required=False),
        'patient_beliefs' : fields.char('Beliefs'),
        'patient_birth_date': fields.date('Date of Birth'),

        'menarca' : fields.char('Menarca'),
        'fur' : fields.char('FUR'),
        'FPR' : fields.char('FPR'),
        'ritmo' : fields.char('Ritmo'),
        'regular' : fields.boolean('Regular'),
        'dismenorrea' : fields.char('Dismenorrea'),
        'metrorragias' : fields.char('Metrorragias'),
        'dispareunia' : fields.char('Dispareunia'),
        'sangrado_post_coito' : fields.char('Sangrado post-coito'),
        'frigidez' : fields.char('Frigidez'),
        'g' : fields.char('G'),
        'p' : fields.char('P'),
        'a' : fields.char('A'),
        'legrados' : fields.char('Legrados'),
        'legrados_fecha' : fields.char('Fecha'),
        'cesareas' : fields.char('Cesáreas'),
        'cesareas_fecha' : fields.char('Fecha'),
        'fup' : fields.char('FUP'),
        'atencion_prenatal' : fields.char('Atención prenatal'),
        'atencion_prenatal_donde' : fields.char('¿Dónde?'),
        'enfermedad_embarazo' : fields.char('Enf. Embarazo'),
        'duracion_embarazo' : fields.char('Duración Embarazo'),
        'partos_hospitalarios' : fields.char('Partos hospitalarios'),
        'partos_hospitalarios_donde' : fields.char('¿Dónde?'),
        'problemas_embarazos'  : fields.char('Poblemas embarazos'),
        'hemorragias'  : fields.char('Hemorragias'),
        'infecciones'  : fields.char('Infecciones'),
        'rupturas'  : fields.char('Rupturas'),
        'distocia'  : fields.char('Distocia'),
        'problemas_rn'  : fields.char('Problemas del R.N'),
        'peso_promedio_hijos'  : fields.char('Peso promedio hijos'),
        'edad_primer_hijo' : fields.char('Edad primer hijo'),
        'edad_ultimo_hijo' : fields.char('Edad ultimo hijo'),
        'lactancia' : fields.char('Lactancia'),
        'lactancia_tiempo' : fields.char('Tiempo'),
        'flujos_vaginales' : fields.text('Flujos vaginales'),
        'flujos_vaginales_color' : fields.text('Color'),
        'flujos_vaginales_olor' : fields.text('Olor'),
        'flujos_vaginales_prurito' : fields.text('Prurito'),
        'flujos_vaginales_tx' : fields.text('Tx')
    }

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        rec_name = 'number'
        res = [(r['id'], r[rec_name])
               for r in self.read(cr, uid, ids, [rec_name], context)]
        return res

    def onchange_professional(self, cr, uid, ids, professional_id, context=None):
        values = {}
        if not professional_id:
            return values
        professional_data = self.pool.get('doctor.professional').browse(cr, uid, professional_id, context=context)
        professional_img = professional_data.photo
        if professional_data.speciality_id.id:
            professional_speciality = professional_data.speciality_id.id
            values.update({
                'speciality': professional_speciality,
            })

        values.update({
            'professional_photo': professional_img,
        })
        _logger.info(values)
        return {'value': values}


    def onchange_patient(self, cr, uid, ids, patient_id, context=None):
        values = {}
        if not patient_id:
            return values
        past = self.pool.get('doctor.attentions.past').search(cr, uid, [('patient_id', '=', patient_id)],
                                                              order='id asc')
        phatological_past = self.pool.get('doctor.diseases.past').search(cr, uid, [('patient_id', '=', patient_id)],
                                                                         order='id asc')
        drugs_past = self.pool.get('doctor.atc.past').search(cr, uid, [('patient_id', '=', patient_id)], order='id asc')
        patient_data = self.pool.get('doctor.patient').browse(cr, uid, patient_id, context=context)
        photo_patient = patient_data.photo

        values.update({
            'patient_photo': photo_patient,
            'past_ids': past,
            'pathological_past_ids': phatological_past,
            'drugs_past_ids': drugs_past,
        })
        return {'value': values}

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

    # it allows to return the patient's age in years, months, days e.g  24 years, 8 months, 3 days. -C
    def calcular_edad_ymd(self, fecha_nacimiento):
        today = date.today()
        age = relativedelta(today, datetime.strptime(fecha_nacimiento, '%Y-%m-%d'))
        age_ymd = str(age.years) + ' Años, ' + str(age.months) + ' Meses,' + str(age.days) + ' Días'
        return age_ymd

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

    def _get_professional_id(self, cr, uid, user_id):
        try:
            professional_id = self.pool.get('doctor.professional').browse(cr, uid,
                                                                          self.pool.get('doctor.professional').search(
                                                                              cr, uid, [('user_id', '=', uid)]))[0].id
            return professional_id
        except:
            return False

    def default_get(self, cr, uid, fields, context=None):
        res = super(doctor_attentions_gynecology, self).default_get(cr, uid, fields, context=context)

        modelo_permisos = self.pool.get('res.groups')
        nombre_permisos = []
        cr.execute("SELECT gid FROM res_groups_users_rel WHERE uid = %s" % (uid))

        for i in cr.fetchall():
            grupo_id = modelo_permisos.browse(cr, uid, i[0], context=context).name
            nombre_permisos.append(grupo_id)

        if context.get('active_model') == "doctor.patient":
            id_paciente = context.get('default_patient_id')
        else:
            id_paciente = context.get('patient_id')

        registros_categorias = []
        registros_examenes_fisicos = []


        if id_paciente:
            fecha_nacimiento = self.pool.get('doctor.patient').browse(cr, uid, id_paciente, context=context).birth_date
            res['age_patient_ymd'] = self.calcular_edad_ymd(fecha_nacimiento)
            res['age_attention'] = self.calcular_edad(fecha_nacimiento)
            res['age_unit'] = self.calcular_age_unit(fecha_nacimiento)

        return res

    _defaults = {
        'patient_id': lambda self, cr, uid, context: context.get('patient_id', False),
        'date_attention': lambda *a: datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
        'professional_id': _get_professional_id if _get_professional_id != False else False,
        'state': 'open',
        'tipo_historia': 'hc_gynecology',
        'patient_birth_date': lambda self, cr, uid, context: context.get('defaut_patient_birth_date', False)
    }


doctor_attentions_gynecology()
