from odoo import fields,api,models

class LogicSubject(models.Model):
    _name = "logic.subject"
    name = fields.Char(string="Subject Name")
    course = fields.Char(string="Course")
