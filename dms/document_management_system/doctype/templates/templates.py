# Copyright (c) 2023, karim kohel & mohamed osama and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
import os
from frappe.model.naming import make_autoname

class templates(Document):
	
	def before_save(self):
		if "docx" not in self.file:
			os.remove(frappe.local.site+"/"+self.file)
			frappe.throw("Allowed file types are: MS Word docx files only")

		self.created_by = frappe.session.user
		self.datetime = frappe.utils.now()

		templateTypeCode = frappe.db.get_value('Types', self.custom_type, 'type_code')
		self.custom_template_code = make_autoname(templateTypeCode + '.#####')