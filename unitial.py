import re
import fitz  # use pymupdf
import pandas as pd
import time,random
import os
from selenium import webdriver # use selenium to get the information
from urllib import parse  
from time import sleep


# Get the content of the reference page------------------------------------------------------------------------------------------------------
def GetRefPages(pdfname):
    pdf=fitz.open(pdfname)
    pagenum=len(pdf)
    ref_list=[]
    for num,p in enumerate(pdf):
        content=p.get_text('blocks')
        for pc in content:
            txtblocks=list(pc[4:-2])
            txt=''.join(txtblocks)
            if 'References' in txt or 'REFERENCES' in txt or 'referenCes' in txt :
                refpagenum=[i for i in range(num,pagenum)]
                for rpn in refpagenum:
                    refpage=pdf[rpn]
                    refcontent=refpage.get_text('blocks')
                    for n,refc in enumerate(refcontent):
                        txtblocks=list(refc[4:-2])
                        ref_list.extend(txtblocks)

    return ref_list

# Get the text of reference--------------------------------------------------------------------------------------------------------------------
def GetRefTxt(ref_list):
    refnum=0
    for nref,ref in enumerate(ref_list):
        if 'References' in ref  or 'REFERENCES' in ref or 'referenCes' in ref or 'ACKNOWLEDGMENTS' in ref:
            refnum=nref
    references_list=ref_list[refnum+1:]

    return references_list

# Parse text content into a single reference------------------------------------------------------------------------------------------------
def GetUnitRef(references_list):
    # remove unnecessary characters
    references_list=[i.replace('\n',' ') for i in references_list]
    references_list=[re.sub(r'<.*>','',i) for i in references_list]

    # turn all the text to a string
    references=' '.join(references_list).replace('- ','')
    references=re.sub(r'\([0-9]{1,3}\)','',references).replace('   ','')

    # Split by author by regular expression
    authorspattern=re.compile(r'([A-Za-z]+ ?[A-Za-z]* ?[A-Za-z]*-?[A-Za-z]*, [A-Z]\..*?\([0-9|a-zA-Z])')
    reflist=re.split(authorspattern,references)
    reflist=list(filter(None,reflist))

    # export the references
    allref_list=[]

    # Every 2 pieces are spelled into 1 document, skip the header
    reflength=len(reflist)
    step=2
    for i in range(0, reflength , step):

        # Skip the header which doesn't have '.' and ').'
        if '.' in reflist[i] or '). ' in reflist[i]:
            unitref=reflist[i:i+step]
            unit=''.join(unitref)
            allref_list.append(unit)

    # Process book references (first half and second half merge into list, then delete first half)
    mid_list=[]
    for n,a in enumerate(allref_list):
        if 'Ed' in a and re.search(r'\([0-9]+\)',a)==None:
            mid_list.append(allref_list[n-1]+allref_list[n])
        else:
            mid_list.append(a)

    final_list=[]
    for num,i in enumerate(mid_list[:-1]):
        if i not in mid_list[num+1]:
            final_list.append(i)
    final_list.append(mid_list[-1])

    return final_list

# Extract information from each reference--------------------------------------------------------------------------------------------------
def GetInfo(final_list):
    referencelist=[]
    authorlist,yearlist,titlelist,journallist=[],[],[],[]
    doilist=[]
    for f in final_list:

        # full text
        referencelist.append(f)

        # author
        try:
            author=re.findall(r'([A-Za-z]+ ?[A-Za-z]* ?[A-Za-z]*-?[A-Za-z]*, [A-Z]\..*?\()',f)[0].replace('(','')
        except:
            author='Null'
        authorlist.append(author)

        # year
        try:
            year=re.findall(r'(\([0-9|a-z| ]+\))',f)[0].replace('(','').replace(')','')
        except:
            year='Null'
        yearlist.append(year)

        # titile
        try:
            title=f.split('). ')[1].replace('?','.').split('.')[0]
        except:
            title='Null'
        titlelist.append(title)

        # journal
        try:
            # journal=f.split('). ')[1].split('.')[1].split(',')[0]
            journal=''.join(re.findall(r'.*?\)\. .*?[\.|?] (.*[,|.]?)',f)).split(',')[0]
        except:
            journal='Null'
        journallist.append(journal)

        # DOI
        try:
            if 'doi.org' in f :
                DOI=f.split('org/')[1]
            elif 'doi:' in f:
                DOI=f.split('doi:')[1]
            else:
                DOI='Null'
        except:
            DOI='Null'
        doilist.append(DOI)

        # Convert to data frame
        refdata={
        'Author':authorlist,
        'Year':yearlist,
        'Title':titlelist,
        'Journal':journallist,
        'DOI':doilist,
        'Reference':referencelist
        }
        refdata=pd.DataFrame(refdata)
    print(refdata)
    return refdata


# Write into the text/excel--------------------------------------------------------------------------------------------------------------------
def write2txt(path,filename,final_list):
    txtname=path+'\\'+'[Refs of]'+filename+'.txt'
    with open(txtname,"w",encoding='utf-8') as f:
        txtcontent='\n'.join(final_list)
        f.write('<<'+filename+'>>'+'\n'+txtcontent)

# Tip: you need to pip install oepnpyxl----------------------------------------------------------------------------------------------------------
def refinfo2excel(path,filename,refdata):
    excelname= path+'\\'+'[Refs of]'+filename+'.xlsx'
    refdata.to_excel(excelname,index=0)

# Class: Get the BibTeX-----------------------------------------------------------------------------------------------------------------------
class GetBibs():

# Start the Chrome browser------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, driver_path, option_path, gg_search_url) -> None:
        self.gg_search_url = gg_search_url
        option = webdriver.ChromeOptions()
        option.add_argument("--user-data-dir="+option_path)
        self.browser = webdriver.Chrome(executable_path = driver_path, options = option)   # Open the chromedriver
        self.browser.set_window_size(800,800) # The size of Click

# Obtained from mirror google source, mainly by inspecting element-------------------------------------------------------------------------------------------------------------
    def get_bib_from_google_scholar(self, paper_title):
        strto_pn=parse.quote(paper_title)
        url = self.gg_search_url + strto_pn
        self.browser.get(url)  # Enter the website

        # Wait the entry to load
        for i in range(100):
            try:
                element=self.browser.find_element_by_css_selector("[class='gs_r gs_or gs_scl']")
                element=element.find_element_by_css_selector("[class='gs_fl']")
                element=element.find_element_by_css_selector("[class='gs_or_cit gs_or_btn gs_nph']")
                element.click()
                break
            except:
                sleep(0.1)

        for i in range(100):
            try:
                element=self.browser.find_element_by_id("gs_citi")
                element=element.find_element_by_css_selector("[class='gs_citi']")
                element.click()
                break
            except:
                sleep(0.1)

        for i in range(100):
            try:
                bib = self.browser.find_element_by_tag_name('pre').text
                break
            except:
                sleep(0.1)

        return bib

# Print the BibTeX -------------------------------------------------------------------------------------------------------------------------------
    def get_bib(self, paper_title):
        bib = self.get_bib_from_google_scholar(paper_title)
        return "Google", self.get_bib_from_google_scholar(paper_title)