from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from datetime import date


class LogicBaseBathes(models.Model):
    _name = 'logic.base.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Batch'

    name = fields.Char(string="Batch Name", index=True, required=1)
    code = fields.Char(string="Batch Code", index=True)
    product_id = fields.Many2one('product.product', string="Course", index=True, required=1)
    company_id = fields.Many2one('res.company', string="Branch", default=lambda self: self.env.company.id, required=1)
    # location = fields.Many2one('res.company',string="Branch", index=True)
    tot_seats = fields.Integer(string="Total Seats", index=True)
    # batch_id = fields.Many2one('res.batch', string="Batch Name")
    student_id = fields.Many2one('res.partner', string="Student")
    # available_seats = fields.Integer(string="Available Seats",compute='_compute_seats', readonly="1", store=True)
    available_seats = fields.Integer(string="Available Seats", compute='_compute_seats', readonly="1", store=True)
    admission_count = fields.Integer(string="Student Count", compute='_compute_student_count', readonly="1")
    created_id = fields.Many2one('res.users', string="Created By", readonly="1")
    state = fields.Selection([('draft', 'Draft'),
                              ('marketing', 'Manager Approval'),
                              ('accounts', 'Accounts Approval'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], default='draft')
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    class_id = fields.Many2one('res.class', string="class")
    adm_id = fields.Many2one('res.admission', string="Admission")
    message_ids = fields.One2many('mail.message', 'res_id', string="Messages")
    create_date = fields.Datetime(string="Create Date", tracking=True, default=date.today())
    approve_date = fields.Date(string="Approve Date", tracking=True)
    active_state = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string="Status", default='active')

    class_teacher_id = fields.Many2one('hr.employee', string="Class Teacher")
    fee_collection_id = fields.Many2one('hr.employee', string="Fee Collector")

    @api.depends('make_visible_head_batch')
    def get_batch_head(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('logic_base.academic_head_batch'):
            self.make_visible_head_batch = False

        else:
            self.make_visible_head_batch = True

    make_visible_head_batch = fields.Boolean(string="User", default=True, compute='get_batch_head')

    @api.depends('make_visible_accounts_batch')
    def get_batch_accounts(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('logic_base.accounts_batch'):
            self.make_visible_accounts_batch = False

        else:
            self.make_visible_accounts_batch = True

    make_visible_accounts_batch = fields.Boolean(string="User", default=True, compute='get_batch_accounts')

    @api.depends('make_visible_manager_batch')
    def get_batch_manager(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('logic_base.manager_batch'):
            self.make_visible_manager_batch = False

        else:
            self.make_visible_manager_batch = True

    make_visible_manager_batch = fields.Boolean(string="User", default=True, compute='get_batch_manager')

    def action_cancel(self):
        self.state = 'cancel'

    def action_approve(self):
        self.state = 'marketing'
        for i in self:
            i.approve_date = date.today()
            i.created_id = self.env.user.id

    def manager_approve(self):
        self.state = 'accounts'
        # for i in self:
        #     i.approve_date = date.today()
        #     i.created_id = self.env.user.id

    def accounts_approve(self):
        self.state = 'done'
        # for i in self:
        #     i.approve_date = date.today()
        #     i.created_id = self.env.user.id

    @api.model
    def test_logic_cron_code(self):
        res = self.env['logic.batch'].search([])
        for i in res:
            if i.state in 'active' and i.to_date == date.today() + timedelta(days=1):
                i.state = 'inactive'

    def _compute_student_count(self):
        admission_ids = self.env['logic.base.class'].search_count([('batch_id', '=', self.id)])
        print(admission_ids, 'eb')
        if admission_ids:
            self.admission_count = admission_ids
        else:
            self.admission_count = 0
        # for i in admission_ids:
        #     print(len(i.batch_id), 'count')


    @api.depends('tot_seats')
    def _compute_seats(self):
        for i in self:
            count = self.env['res.admission'].sudo().search_count([('batch_id', '=', i.id), ('state', '=', 'confirm')])
            # if count:
            #     i.admission_count = count
            if i.tot_seats:
                i.available_seats = i.tot_seats - count
            if i.available_seats < 0:
                raise ValidationError(
                    _("This Batch is Already Filled"))

    def action_class_view(self):
        ss = self.env['logic.base.class'].search([('batch_id.id', '=', self.id)])
        print(self.id, 'sel')
        print(ss.batch_id, 'selffff')

        return {
            'name': _('Students'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'logic.base.class',
            # 'view_mode': 'tree,form',
            'domain': [('batch_id', 'in', ss.mapped('batch_id').ids)],
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False}}

        # partner_ids = ss.mapped('batch_id')
        # print(partner_ids, 'dd')
        # student_ids = ss.mapped('batch_id')
        # for i in ss:
        #     print(i.name, 'll')

    # def action_allocation(self):
    #     crm = self.env['classroom.allocate.student'].search([('class_id', '=', self.id)])
    #     return {
    #         'name': _('Task'),
    #         'view_mode': 'form',
    #         'res_model': 'classroom.allocate.student',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         "context": {
    #             'default_batch_id': self.id,
    #             'default_student_ids': self.student_id.id,
    #             # 'default_revenue': self.expected_revenue,
    #             # 'default_no_person': self.no_of_persons_package,
    #
    #         },
    #     }
