from odoo import fields, models

class Patient(models.Model):
    _name = "hospital.patient"
    _description = "hospital patient"

    name = fields.Char(string="Name")
    address = fields.Char(string="Address")
    mobile = fields.Char(string="Mobile")
