from spire.pdf.common import *
from spire.pdf import *

doc = PdfDocument()
doc.LoadFromFile("퓌_PH_운송장 출력 1.pdf")

outputFile = "pdftoexcel.xlsx"

doc.SaveToFile(outputFile, FileFormat.XLSX)
doc.Close()