# Copyright (c) 2023, karim kohel & mohamed osama and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
import os
from frappe.model.naming import make_autoname

class templates(Document):
	
	def before_save(self):
		if (self.file[-4:] != "docx") and (self.file[-3:] != 'doc'):
			os.remove(frappe.local.site+"/"+self.file)
			frappe.throw("Allowed file types are: MS Word docx files only")

		self.created_by = frappe.session.user
		self.datetime = frappe.utils.now()

		templateTypeCode = frappe.db.get_value('Types', self.template_type, 'type_code')
		self.code = make_autoname(templateTypeCode + '.#####')
