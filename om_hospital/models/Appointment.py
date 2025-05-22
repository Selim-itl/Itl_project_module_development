from odoo import fields, models

class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "hospital appointment"
    _rec_name = "ref"

    ref = fields.Char("Reference")
    patient_id = fields.Many2one("hospital.patient", "Patient")
    doctor_id = fields.Many2one("hospital.doctor", "Doctor")
    room = fields.Char(string="Room no")
    date = fields.Date(string="Appointment date")