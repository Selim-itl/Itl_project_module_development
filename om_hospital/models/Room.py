from odoo import fields, models

class Room(models.Model):
    _name = "hospital.room"

    name = fields.Char("Room Number")