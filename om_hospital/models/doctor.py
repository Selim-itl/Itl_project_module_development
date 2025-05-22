from odoo import fields, models

class Doctor(models.Model):
    _name = "hospital.doctor"
    _description = "hospital doctor"

    name = fields.Char(string="Name")
    Degree = fields.Char(string="Degree")
    fee = fields.Integer(string="Fee")
