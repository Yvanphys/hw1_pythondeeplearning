from unitial import *
from pdf_extract import *

# Path of the Chromedriver
driver_path = r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver' # 浏览器驱动位置
option_path = r"C:\\Users\\86180\\AppData\\Local\\Google\\Chrome\\Userdate" # 浏览器能用自定义的设置
gg_search_url = r'https://xs.dailyheadlines.cc/scholar?q=' # 镜像谷歌源
get_bibs = GetBibs(driver_path, option_path, gg_search_url)
paper_titles = [] # Document names extracted from pdf
paper_titles = refdata['Title']

for k in range(len(paper_titles)):
    source, bib = get_bibs.get_bib(paper_titles[k]) 
    print(source+":",k)
    print(bib) 