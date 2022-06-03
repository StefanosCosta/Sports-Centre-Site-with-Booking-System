from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter
from barcode import generate

def gen(name, surname,currentDate,id,price,startWeek,endWeek,sc,sp,sh):
    str1=""
    if sc==1:
        str1=str1+"Squash Room-2 "
        if sp==1:
            str1=str1+",Swimming Pool "
        if sh==1:
            str1=str1+",Sports Hall"
    else:
        if sp==1:
            str1=str1+"Swimming Pool "
            if sh==1:
                str1=str1+",Sports Hall"
        else:
            if sh==1:
                str1=str1+"Sports Hall"
    # Create instance of FPDF class
    # Letter size paper, use inches as unit of measure
    pdf=FPDF(format='letter', unit='in')

    # Add new page. Without this you cannot create the document.
    pdf.add_page()

    # Remember to always put one of these at least once.
    pdf.set_font('Times','',10.0)

    # Effective page width, or just epw
    epw = pdf.w - 2*pdf.l_margin

    # Set column width to 1/4 of effective page width to distribute content
    # evenly across table and page
    col_width = epw/2
    # Text height is the same as current font size
    th = pdf.font_size

    # Since we do not need to draw lines anymore, there is no need to separate
    # headers from data matrix.
    # if receiptType == "Booking":
    #     data = [['Product','Booking Date','Booking Time','Price'],
    #     [product,bookingDate,bookingTime,price]]
    data = [['Product','Price'],
    ["Week Plan for " + startWeek + " - " + endWeek ,''],
    [str1,price]]
    # elif receiptType == "Membership":
    #     data = []
    # else
    #     return False
    strId = str(id)
    newString = ""
    while len(strId) + len(newString) < 12:
        newString += '0'
    codeId = newString + strId
    EAN = barcode.get_barcode_class('ean13')
    ean = barcode.get('ean13', codeId, writer=ImageWriter())
    barcode_path = 'app/static/barcodes/' + str(id)
    fullname = ean.save(barcode_path)
    # Line break equivalent to 4 lines
    pdf.ln(4*th)

    pdf.set_font('Times','B',14.0)
    pdf.cell(epw, 0.0, 'The 19 Gym ', align='C')
    pdf.ln(0.5)
    pdf.cell(epw, 0.0, 'Week Plan Invoice', align='C')
    pdf.set_font('Times','',10.0)
    pdf.ln(0.4)
    pdf.cell(epw/2, 0.0, 'Name: '+ name, align='L')
    pdf.cell(epw/2, 0.0, 'Date: '+ str(currentDate), align='R')
    pdf.ln(0.2)
    pdf.cell(epw/2, 0.0, 'Surname: '+ surname, align='L')
    pdf.cell(epw/2, 0.0, 'Receipt ID: #'+ str(id), align='R')
    pdf.ln(0.2)

    counter = 0
    # Here we add more padding by passing 2*th as height
    for row in data:
        if counter == 0:
            pdf.set_font('Times','B',12.0)
            # pdf.setFillColor(50)
            counter = 1
        elif counter == 1:
            pdf.set_font('Times','',10.0)
            counter+=1
        for datum in row:
            # Enter data in colums
            pdf.cell(col_width, 2*th, str(datum), border=1)
        pdf.ln(2*th)


    pdf.ln(0.2)
    pdf.cell(epw, 0.0, 'Total: '+ str(price), align='R')
    pdf.ln(0.2)
    path = barcode_path + ".png"
    pdf.image(path)

    filename = 'app/static/receipts/' + str(id) + '.pdf'
    pdf.output(filename,'F')
