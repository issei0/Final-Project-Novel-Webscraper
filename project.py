from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re, zipfile, os, sys, shutil, subprocess
from PIL import ImageFont, ImageDraw, Image
from pyfiglet import Figlet


def main():
    print('Please wait for a few seconds')
    novel_list = create_list() # creates full list of novels available on freewebnovel.com
    while True:
        while True:
            try:
                statment = """
How would you like to proceed:
1) Display whole list
2) Search the novel
Exit the program at any stage by using ctrl+c and enter it
Answer with above the numbers: """
                argu = input(statment)
                if argu == "1":
                    openingfile() # opening the novel_list
                    while True:
                        # select novel id
                        idd = int(input('\nEnter the id of your novel: '))
                        name, url, boo = extraction(idd, novel_list)
                        if boo == True:
                            break
                    else:
                        continue
                    break

                elif argu == "2":
                    while True:
                        search = input("\nSearch: ")
                        # all results related to the search
                        searched = [dic for dic in novel_list if re.search(rf"^{search}", dic['Name'], re.IGNORECASE)]

                        if searched == []:
                            print("\nNot Found")
                        else:
                            print("\nSearch result:")
                            for item in searched:
                                iden = item["id"]
                                Name = item["Name"]
                                print(f"{iden} : {Name}")

                            while True:
                                idd = int(input("\nEnter the id number of novel: "))
                                name, url, booli = extraction(idd, searched)
                                if booli == True:
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break

            except KeyboardInterrupt:
                os.remove("novel_list.txt")
                sys.exit("Exiting....")
            except:
                pass

        latest_chapter = int(get_latest_chapter(url))
        print("\nNo of chapters available: ", latest_chapter) # Gets the latest novel chapter

        while True:
            try:
                while True:
                    start = int(input("Select the starting chapter: ")) # First chapter
                    if start <= latest_chapter:
                        break
                    else:
                        print('\nplease enter valid the chapter number!!!')

                while True:
                    end = int(input("Select the ending chapter: ")) + 1 # Last chapter
                    if end <= (latest_chapter + 1):
                        break
                    else:
                        print('\nplease enter valid the chapter number!!!')
        
                else:
                    continue
                break

            except KeyboardInterrupt:
                os.remove("novel_list.txt")
                sys.exit("Exiting....")
            except:
                pass
                
        gen_img(name) # creates the title cover for the novel
        chapter_list = []

        print("")
        while start < end:
            sou, so = webscrape(start, url) # Scrapes the chapter
            chapter, content, naming = filterr(sou, so) # Extract the chapter and content from scraped content
            chapter_list.append(naming) # naming is full chapter name extracted from title tag
            create_chapter(chapter, content, naming) # write the chapter on html file
            print(f"{naming} - written") # Chapter number written
            start += 1

        create_mimetype() # create mimetype
        create_pagestyle() # create pagestyle
        create_stylesheet() # create stylesheet
        create_titlepage() # create titlepage
        create_toc(name, chapter_list) # create table of content
        create_content_opf(name, chapter_list) # create content.opf
        create_container() # create container for epub
        epub(name, chapter_list) # packs all necessary files for epub
        file_remove() # remove all unnecessary file

        for item in chapter_list:
            os.remove(f'{item}.html')
        
        figlet = Figlet()
        figlet.setFont(font="double")
        print(figlet.renderText("Novel Completed"))
        
        while True:
            try:
                repeat = """
Options:
     1) Download more novels
ctrl+c) For exiting
Answer: """
                state = input(repeat)
                if state == "1":
                    break
                else:
                    pass

            except KeyboardInterrupt:
                os.remove("novel_list.txt")
                sys.exit("Exiting....")
            except:
                pass



def create_list():
    while True:
        try:
            url = Request(url="https://freewebnovel.com/sitemap.xml", headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'})
            break
        except:
            pass
    xml = urlopen(url).read()
    soup = BeautifulSoup(xml, "xml")

    listing = []

    file_object = open("novel_list.txt", "a", encoding="utf-8")
    file_object.write("Brower these novels here.\nExit the terminal supported editor using ^X and the enter the id associated with the novel your want to scrape.\nIn case, it asks for buffer modification then proceed with N or no.\n\n")

    # extract url from url list
    for index, sou in enumerate(soup.find_all('loc'), start=1):
        name = list(sou.get_text()[25:-5])

        # extract chapter name from url
        rename = ""
        for x in name:
            if x == "-":
                rename = rename + " "
            else:
                rename = rename + x

        listing.append({'id': index, 'Name': rename.title(), 'URL': sou.get_text()})
        file_object.write(f"{index} : {rename.title()}\n")

    file_object.close()

    return listing


def openingfile():
    file_name = "novel_list.txt"
    if hasattr(os, "startfile"):
        os.startfile(file_name)
    elif shutil.which("xdg-open"):
        subprocess.call(["xdg-open", file_name])
    elif "EDITOR" in os.environ:
        subprocess.call([os.environ["EDITOR"], file_name])


def extraction(idd, lis):
    for x in lis:
        if idd == x["id"]:
            name = x['Name']
            url = x['URL']
            return name, url, True
    return None, None, False


def get_latest_chapter(url):
    while True:
        try:
            url = Request(url=url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'})
            break
        except:
            pass

    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # latest chapter section
    sou = soup.find('ul', class_='ul-list5')
    so = sou.find('a')
    href = so['href']

    # Extracting chapter number from url because chapter number in text and in url may vary
    latest = re.search(r'/chapter-([0-9]*).html', href)
    return latest.group(1)


def gen_img(s):
    string = ""
    ss = s.split(" ")

    # Dividing the chapter name after every 3 words in order to avoid overflow
    for item in ss:
        idd = ss.index(item)
        if idd == 0:
            string = string + item + " "
        elif (idd % 3) == 0:
            string = string + "\n" + item + " "
        else:
            string = string + item + " "

    img = Image.open('cover.jpg')
    Width, Heigh = img.size

    # Image is converted into editable form using
    # Draw function and assigned to d1
    d1 = ImageDraw.Draw(img)

    # Font selection from the downloaded file
    myFont = ImageFont.truetype('./FreeSansBold.ttf', 75)
    _, _, width, height = d1.textbbox((0, 0), string, font=myFont)

    # Decide the text location, color and font
    d1.multiline_text(((Width-width)/2, (Heigh-height)/2), string, fill =(255, 255, 255),font=myFont)

    img.save("cover.jpeg")


def webscrape(i, url):
    while True:
        # Scraping the indivilual chapter
        try:
            url = Request(url=f"{url[:-5]}/chapter-{i}.html", headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'})
            break
        except:
            pass

    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    sou = soup.find('div', class_='txt') # extracting chapter content
    so = soup.find('title') # extracting chapter name from title tag

    return list(sou), list(so)


def filterr(strips, strips1):
    # filter self-advertisement of website's owner
    for n, item in enumerate(strips):
        if re.search("<sub", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search("<div", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search("Translator", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search("Translate", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search("Translation", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search("Editor", str(item), re.IGNORECASE):
            strips.pop(n)
        if re.search(r"chapter [0-9]*", str(item), re.IGNORECASE):
            strips.pop(n)

    # Extracting chapter name for the chapter title
    naming = re.search(r"(Chapter [0-9]*.*)(?: - Free Web Novel)", str(strips1), re.IGNORECASE)
    chapter = "<h1 class='calibre1'>" + naming.group(1) + "</h1>"

    return chapter, strips, naming.group(1)


def create_chapter(chapter, strips, naming):
    file_object = open(f'{naming}.html', 'a', encoding="utf-8")

    head =f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{naming}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
    <link rel="stylesheet" type="text/css" href="page_styles.css"/>
</head>
<body class="calibre">
"""

    end ="""</body>
</html>"""


    file_object.write(head)
    file_object.write(chapter)
    for listitem in strips:
        file_object.write('%s\n' % listitem)
    file_object.write(end)
    file_object.close()


def create_mimetype():
    file_object = open('mimetype', 'a', encoding="utf-8")
    file_object.write("application/epub+zip")
    file_object.close()


def create_pagestyle():
    file_object = open('page_styles.css', 'a', encoding="utf-8")
    style = """@page {
    margin-bottom: 5pt;
    margin-top: 5pt;
}"""
    file_object.write(style)
    file_object.close()


def create_stylesheet():
    file_object = open('stylesheet.css', 'a', encoding="utf-8")
    style = """.calibre {
    display: block;
    font-size: 1em;
    padding-left: 0;
    padding-right: 0;
    margin: 0 5pt;
}"""
    file_object.write(style)
    file_object.close()


def create_titlepage():
    file_object = open('titlepage.xhtml', 'a', encoding="utf-8")
    content = """<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>Cover</title>
    <style type="text/css" title="override_css">
        @page {padding: 0pt; margin:0pt}
        body { text-align: center; padding:0pt; margin: 0pt; }
    </style>
</head>
<body>
    <div>
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="100%" height="100%" viewBox="0 0 1200 1600" preserveAspectRatio="none">
            <image width="1200" height="1600" xlink:href="cover.jpeg"/>
        </svg>
    </div>
</body>
</html>"""
    file_object.write(content)
    file_object.close()


def create_toc(name, chapter_list):
    file_object = open('toc.ncx', 'a', encoding="utf-8")
    head = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx version="2005-1" xml:lang="en" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content="b5327a9c-3fd8-4ba0-b467-d5156bee4a48"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>{name}</text>
  </docTitle>
  <navMap>"""
    file_object.write(head)

    # write the contents of the table
    for i, item in enumerate(chapter_list, start=1):
        content = f"""
    <navPoint id="{item}" playOrder="{i}">
      <navLabel>
        <text>{item}</text>
      </navLabel>
      <content src="{item}.html"/>
    </navPoint>"""

        file_object.write(content)

    end = """
  </navMap>
</ncx>"""

    file_object.write(end)
    file_object.close()


def create_content_opf(name, chapter_list):
    file_object = open('content.opf', 'a', encoding='utf-8')
    head = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>{name}</dc:title>
    <dc:language>en</dc:language>
    <dc:creator>Programmer</dc:creator>
    <dc:identifier id="BookId" opf:scheme="ISBN">123456789X</dc:identifier>
    <dc:creator opf:file-as="Programmer" opf:role="aut">Programmer</dc:creator>
  </metadata>
  <manifest>"""
    file_object.write(head)

    manifest_start = """
    <item id="cover" href="cover.jpeg" media-type="image/jpeg"/>
    <item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>"""
    file_object.write(manifest_start)

    # writing the chapter name in the manifest
    for item in chapter_list:
        manifest_chapter = f"""
    <item id="{item}" href="{item}.html" media-type="application/xhtml+xml"/>"""
        file_object.write(manifest_chapter)

    manifest_end = """
    <item id="page_css" href="page_styles.css" media-type="text/css"/>
    <item id="css" href="stylesheet.css" media-type="text/css"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>"""
    file_object.write(manifest_end)

    spine = """
  </manifest>

  <spine toc="ncx">"""
    file_object.write(spine)

    titlepage = """
    <itemref idref="titlepage"/>"""
    file_object.write(titlepage)

    # writing the chapter id in spine
    for item in chapter_list:
        chap = f"""
        <itemref idref="{item}"/>"""
        file_object.write(chap)

    end = """
  </spine>

  <guide>
    <reference type="cover" href="titlepage.xhtml" title="Title page"/>
  </guide>
</package>"""
    file_object.write(end)
    file_object.close()


def create_container():
    try:
        os.mkdir('META-INF')
    except (FileExistsError):
        pass

    file_object = open('./META-INF/container.xml', 'a')
    content = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>"""
    file_object.write(content)


def epub(name, chapter_list):
    if os.path.isdir("./Novels"):
        pass
    else:
        os.mkdir("./Novels")
        
    if os.path.isfile(f"./Novels/{name}.epub"):
        x = 1
        while True:
            if os.path.isfile(f"./Novels/{name}_{x}.epub"):
                pass
            else:
                myzip = zipfile.ZipFile(f'./Novels/{name}_{x}.zip', 'a')
                filename = f'./Novels/{name}_{x}'
                break
            x += 1
    else:
        myzip = zipfile.ZipFile(f'./Novels/{name}.zip', 'a')
        filename = f'./Novels/{name}'

    for item in chapter_list:
        myzip.write(f'{item}.html')

    myzip.write('mimetype')
    myzip.write('page_styles.css')
    myzip.write('stylesheet.css')
    myzip.write('titlepage.xhtml')
    myzip.write('toc.ncx')
    myzip.write('content.opf')
    myzip.write('cover.jpeg')
    myzip.write('META-INF/container.xml')

    myzip.close()

    os.rename(f'{filename}.zip', f'{filename}.epub')


def file_remove():
    os.remove('mimetype')
    os.remove('page_styles.css')
    os.remove('stylesheet.css')
    os.remove('titlepage.xhtml')
    os.remove('toc.ncx')
    os.remove('content.opf')
    os.remove('cover.jpeg')
    os.remove('META-INF/container.xml')
    os.rmdir('META-INF')


if __name__ == "__main__":
    main()