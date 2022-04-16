from unitial import *

pdfname = 'E:\\desk\\python\\python_base_training\\homework1_pdf\\user_pdf.pdf' #存放的pdf路径
ref_list = GetRefPages(pdfname) 
references_list = GetRefTxt(ref_list)
final_list = GetUnitRef(references_list)
path = 'E:\\desk\\python\\python_base_training\\homework1_pdf'  #导出的txt/excel路径
filename = 'Smartphone use undermines enjoyment of face-to-face social interactions' #使用的文章名字
refdata = GetInfo(final_list)

write2txt(path, filename, final_list)
refinfo2excel(path, filename, refdata)