from odoo import api, fields, models


class LogicBaseCourses(models.Model):
    _name = 'logic.base.courses'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Course'

    name = fields.Char(string='Name', required=True)
    course_fee = fields.Float(string='Course Fee')
    type = fields.Selection([('indian', 'Indian'), ('international', 'International'), ('crash', 'Crash')],
                            string='Type')
    board_registration = fields.Boolean(string='Board Registration')
    company_id = fields.Many2one('res.company', string="Branch", default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

    def create_course(self):
        self.state = 'done'
        self.env['product.product'].create({
            'name': self.name,
            'type': 'service',
            'categ_id': 1,
            'uom_id': 1,
            'uom_po_id': 1,
            'lst_price': self.course_fee,
        })

    def return_menu(self):
        self.state = 'draft'
