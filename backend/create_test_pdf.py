from reportlab.pdfgen import canvas

c = canvas.Canvas("test_upload.pdf")
c.drawString(100, 750, "PIA Industrial Manual Test")
c.drawString(100, 700, "This is page 1.")
c.drawString(100, 650, "Content for extraction.")
c.showPage()
c.drawString(100, 750, "PIA Industrial Manual Test - Page 2")
c.drawString(100, 700, "This is page 2.")
c.save()
print("Created test_upload.pdf")
