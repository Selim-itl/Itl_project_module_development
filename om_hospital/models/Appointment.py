from email.policy import default

from odoo import fields, models

class Appointment(models.Model):
    _name = "hospital.appointment"
    _description = "hospital appointment"
    _rec_name = "ref"

    ref = fields.Char("Reference")
    patient_id = fields.Many2one("hospital.patient", "Patient")
    doctor_id = fields.Many2one("hospital.doctor", "Doctor")
    date = fields.Date(string="Appointment date")
    tag_ids = fields.Many2many("hospital.tags", string="Tags")
    room_id = fields.Many2one("hospital.room", "Room")