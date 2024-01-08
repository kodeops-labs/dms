# Copyright (c) 2023, karim kohel & mohamed osama and contributors
# For license information, please see license.txt
from frappe.model.document import Document
import frappe
import os
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from frappe.model.naming import make_autoname
from datetime import datetime

# DEPRECATED
# import aspose.words as aw
# def convert_to_PDF(fileName: str) -> None:
# 	"""Fucntion that converts a word file to pdf by reading the file from storage, convert and then save it back in the same place
# 	"""
# 	docxFilePath: str = frappe.local.site+"/"+fileName
# 	fileName: str = docxFilePath.rsplit('.', 1)[0] # split the name at the last "." and give the first half
# 	document = aw.Document(docxFilePath)
# 	document.save(f"{fileName}.pdf")
# 	os.remove(docxFilePath)

def imprint_on_pdf(fileName: str, docCode: str, docProtocol: str) -> None:
	"""A function that imprints the information needed on the document after submission
	- the function only works on vertical pages and still needs updating to work on horizontal pages
	"""
	pdfFilePath: str = frappe.local.site+"/"+fileName

	# read existing pdf and get size
	existing_pdf = PdfReader(open(pdfFilePath, "rb"))
	singePage = existing_pdf._get_page(0)
	pdfWidth, pdfHight = singePage.mediabox.upper_right


	packet = BytesIO()
	can = canvas.Canvas(packet, pagesize=A4)
	can.rotate(90)
	# writing the left hand code 
	can.drawString(10, -10, docCode)
	# writing the right hand code
	can.drawString(10, -(int(pdfWidth)-2), docProtocol) # TODO: solve the document protocol not printing
	can.save()
	packet.seek(0)
	new_pdf = PdfReader(packet)
	output = PdfWriter()
	
	# add the "watermark" (which is the new pdf) on the existing page
	for page in existing_pdf.pages:
		page.merge_page(new_pdf.pages[0])
		output.add_page(page)
	# finally, write "output" to a real file
	output_stream = open(pdfFilePath, "wb")
	output.write(output_stream)
	output_stream.close()

def assign_protocol(doc: Document) -> str: # TODO: This would probably fail if the same user produces the same document in the same day
	docBusinessPartner = frappe.db.get_value('Business Partner', doc.document_business_partner, 'partner_code')
	date = datetime.today().strftime('%y%m%d')
	userInitials = frappe.session.user[:3]

	return make_autoname(f'{date}/{userInitials}/{docBusinessPartner}/.#####')

class Document(Document):

	def before_save(self):

		if "pdf" not in self.file:
			os.remove(frappe.local.site+"/"+self.file)
			frappe.throw("Allowed file types are: MS Word docx or PDF only")

		self.created_by = frappe.session.user
		self.datetime = frappe.utils.now()

		self.protocol_number = assign_protocol(self)

	def before_submit(self):
		templateUsedCode = frappe.db.get_value('templates', self.document_template_used, 'code')

		imprint_on_pdf(self.file, templateUsedCode, self.protocol_number)