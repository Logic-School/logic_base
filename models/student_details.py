from odoo import fields, models, api, _
from odoo.exceptions import UserError
import json

class LogicStudents(models.Model):
    _name = 'logic.students'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', copy=False, required=True)
    email = fields.Char(string='Email address')
    phone_number = fields.Char(string='Mobile number')
    admission_fee = fields.Float(string='Admission fee')
    reference = fields.Char(string="Name", readonly=True,
                            copy=False, default=lambda self: 'Adv/')
    student_id = fields.Char(string='Student ID')
    aadhar_number = fields.Char(string='Aadhar Number')
    parent_name = fields.Char(string='Parent Name')
    father_name = fields.Char(string='Father Name')
    father_number = fields.Char(string='Father Number')
    mother_name = fields.Char(string='Mother Name')
    mother_number = fields.Char(string='Mother Number')
    course_studied = fields.Char(string='Course Studied')
    last_institute_studied = fields.Char(string='Last Institute Studied')
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline')], string='Mode of Study')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    # adm_no_id = fields.Many2one('res.admission', string='Admission Number')
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country)]")
    country = fields.Many2one('res.country')
    stud_id = fields.Integer()
    batch_id = fields.Many2one('logic.base.batch', string='Batch')
    status = fields.Selection([('draft', 'Draft'), ('linked', 'Linked')], default='draft', string='Status')
    related_partner = fields.Many2one('res.partner', string='Related Partner')
    class_id = fields.Integer(string='Class')
    allocated_class_id = fields.Many2one('logic.base.class')
    adm_id = fields.Integer(string='Admission ID')
    allocated_class_ids = fields.Many2many('logic.base.class')

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'logic.students') or _('New')
        res = super(LogicStudents, self).create(vals)
        return res

    def action_open_admission_custom(self):
        print("ooooooooooooooooooo")
        ff = self.env['res.admission'].search([])
        # for i in ff:
        #     print(i.admission_id)
        for i in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Admission',
                'res_model': 'res.admission',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('crm_lead_id', '=', i.stud_id)],
                # 'domain' : 'admission_id'= self.partner_id
            }
        
    def action_open_exam_results(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Exam Results',
                'res_model': 'logic.student.result',
                'view_mode': 'tree',
                'target': 'current',
                'domain': [('student_id', '=', self.id)],
                # 'domain' : 'admission_id'= self.partner_id
            }

    def action_open_class_custom(self):
        print(self.batch_id.name, 'self')

        data = self.env['logic.base.class'].search([])
        for i in data:
            print(i.batch_id.name, 'selfff')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Class',
                'res_model': 'logic.base.class',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('batch_id.id', '=', self.batch_id.id)]
            }



    def link_partner(self):
        # admission = self.env['res.admission'].search([])
        # for admsn in admission:
        #     if admsn.crm_lead_id.id == self.stud_id:
        #         self.adm_id = admsn.id
        #         self.adm_no_id = admsn.id

        ss = self.env['res.partner'].search([])
        if not self.stud_id:
            raise UserError('Student do not match')

        for i in ss:
            print(self.stud_id, 'stud')
            print(i.part_id, 'paar')
            if i.part_id == self.stud_id:
                print('ya')
                i.related_student = self.id
                self.student_id = i.reference
                self.related_partner = i.id
                self.status = 'linked'
            else:
                print('ll')
        # else:
        #     raise UserError('Students do not match')

    def return_draft(self):
        self.status = 'draft'


class StudentRelationCustom(models.Model):
    _inherit = "res.partner"

    # related_student = fields.Char(string='Related Student')
    related_student = fields.Many2one('logic.students', string='Related Student', readonly=True)


# class ResUsersCustom(models.Model):
#     _inherit = "res.users"

#     # @api.model
#     def chatter_position(self):
#         print('j')

class ClassRoomReallocateStudent(models.TransientModel):
    _name = 'class.base.reallocate.student'
    _description = 'Reallocate students to another class room'
    # def student_ids_domain(self):
    #     class_obj = self.env['logic.base.class'].browse(self.env.context.get('active_id'))
    #     allocated_students = [line.student_id.id for line in class_obj.line_base_ids]
    #     return [('id','not in',already_added_studs)]
    class_id = fields.Many2one('logic.base.class', string="Class")
    batch_id = fields.Many2one('logic.base.batch', string="Batch")
    def student_ids_domain(self):
        class_obj = self.env['logic.base.class'].browse(self.env.context.get('active_id'))
        allocated_stud_line_ids = [student.id for student in class_obj.student_ids]
        return [('id','in',allocated_stud_line_ids)]
    student_ids = fields.Many2many('logic.students',domain=student_ids_domain)

class ClassRoomallocateStudent(models.TransientModel):
    _name = 'class.base.allocate.student'
    _description = 'Allocate students to class room'

    batch_id = fields.Many2one('logic.base.batch', string="Batch")

    def student_ids_domain(self):
        class_obj = self.env['logic.base.class'].browse(self.env.context.get('active_id'))
        already_added_studs = [student.id for student in class_obj.student_ids]
        return [('batch_id','=',class_obj.batch_id.id),('batch_id','!=',False),('allocated_class_id','=',False),('id','not in',already_added_studs)]

    student_ids = fields.Many2many('logic.students', string="Students", copy=True, domain=student_ids_domain)
    # student_ids_domain = fields.Char(
    #     compute="_compute_student_ids_domain",
    #     readonly=True,
    #     store=False,
    # )

    # @api.multi
    # @api.depends('batch_id')
    # def _compute_student_ids_domain(self):
    #     # for record in self:
    #     already_added_studs = [line.student_id.id for line in self.class_id.line_base_ids]
    #     return  {'domain':{'student_ids': [('batch_id', '!=', self.batch_id.id), ('id', 'not in', already_added_studs)] } }
        
    # admission_ids = fields.Many2many('res.admission', string="Admision")
    class_id = fields.Many2one('logic.base.class', string="Class")

    def action_allocation(self):
        
        
        for student_id in self.student_ids:
        #     self.env['student.base.lines'].create({
        #         'batch_id': self.batch_id.id,
        #         'student_id': student_id.id,
        #         'class_base_id': self.class_id.id,

        #     })
            student_id.write({
                'allocated_class_id': self.class_id.id
            })



        # adc = self.env['logic.students'].search([])
        # admission = self.env['res.admission'].search([])
        # print('hhi')
        # # print(self.student_ids)
        # res = []
        # adm = []
        # for i in self:
        #     for j in i.student_ids:
        #         if j.id in adc.ids:
        #             aad = self.env['logic.students'].search([('id', '=', j.id)])
        #             aad.class_id = self.class_id
        #             print(aad,'ye')
        #         else:
        #             print('no')

        #         res_list = {
        #             'student_id': j.id,
        #             # 'class_base_id': i.class_id.id,
        #             'batch_id': self.batch_id.id,
        #             # 'pending_fee': 100,
        #             # 'ad_id': j.adm_id,
        #         }
        #         res.append((0, 0, res_list))
        # print(adm, 'admission')
        # aa = self.env['logic.base.class'].search([('id', '=', self.class_id.id)])
        # print(res, 'res')
        # for ii in aa:
        #     if aa:
        #         ii.line_base_ids = res

        # self.env['logic.base.class'].create({
        #     'line_base_ids': res
        # })
        # for student in self.student_ids:
        #     admission = self.env['res.admission'].search([('batch_id.id', '=', self.batch_id.id)])
        #     print('admision')
        #     for k in admission:

        #         }
        #         print(res_list, 'list')
        #
        #
        #         self.env['logic.base.class'].create({
        #             'line_base_ids': res
        #             # 'pending_fee': self.pending_fee
        #         })
        #     print(res, 'res')
        # x.onchange_ad_id()
        # x.update({

        # })
