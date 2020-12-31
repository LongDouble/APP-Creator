#This program breaks out seperate chapters from
#a PDF document.  It reads the chapters from
#toc.txt and splits out the pages.

import PyPDF2

def SmartSearch(PdfObject, index, beginning):
    pages = []
    PdfReader = PyPDF2.PdfFileReader(PdfObject)
    keyword = "HSE" + str(index) + "-"

    print("Searching for \'" + keyword + "\' in " + PdfObject.name)

    for i in range (beginning, PdfReader.getNumPages()):
        PageObject = PdfReader.getPage(i)
        PageText = PageObject.extractText()

        for characters in range(len(PageText)):
            if i in pages: # means we already located something on this page
                break

            if PageText[characters] == keyword[0]: #indicates first character matches

                for letters in range(1, len(keyword)):
                    characters = characters + 1

                    if characters == len(PageText):
                        break
                    
                    while PageText[characters] == '\n' or PageText[characters] == ' ': #ignore line breaks
                        characters = characters + 1
                    
                    if PageText[characters] != keyword[letters]: #if two letters do not equal
                        break
                    elif (PageText[characters] == keyword[letters] and letters == (len(keyword) - 1)): #if end of word is reached and everything has matched
                        pages.append(i)
                        break

        if len(pages) != 0 and i not in pages: #means we have gotten past the chapter
            break 
                
    if len(pages) == 0:
        print("Was unable to find \'" + keyword + "\' in file. Exiting...")
        input("\nPress enter to exit.")
        exit()
    else:
        return [pages[0], pages[len(pages)-1]]


def createPDFFiles(pdfFileObj, chapters_to_grab, table_of_contents, pages):
    current_position = 0

    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    for page_ranges in pages:

        if str((current_position+1)) in chapters_to_grab:
            pdfWriter = PyPDF2.PdfFileWriter()
            for page in range(page_ranges[0], page_ranges[1]+1):
                pdfWriter.addPage(pdfReader.getPage(page))

            with open(table_of_contents[current_position] + '.pdf', "wb") as f: 
                print("Creating ", table_of_contents[current_position], ".pdf...\n")
                pdfWriter.write(f) 
                
        current_position = current_position + 1

def readTOC(filename):
    list = []
    file = open(filename)
    
    for chapter in file.readlines():
        if (chapter != "" and chapter != '\n'):
            chapter = chapter.replace('/', '-')
            list.append(chapter.strip())

    return list

def main():
    print("Safety Manual Extractor\n")
    print("Created by Austin Goergen for West Coast Contractors, Inc.\n\n")
    pages = []
    filename = "toc.txt"
    pdfFileObj = open('2019manual.pdf', 'rb')

    table_of_contents = readTOC(filename)
    
    beginning = 0

    print("Indexing chapters...\n")
    for index in range(1, len(table_of_contents)+1): 
        pages.append(SmartSearch(pdfFileObj, index, beginning))
        print(table_of_contents[index-1], "is on pages", pages[index-1][0]+1, "through", pages[index-1][1]+1)
        beginning = pages[index-1][1]
    
    user_input = input("What chapters would you like? (seperate the numbers with commas, or type \"all\"): ")

    chapters_to_grab = []

    if user_input == "all":
        for i in range(1, len(table_of_contents)+1):
            chapters_to_grab.append(str(i))
    else:
        chapters_to_grab = user_input.split(",")

    print("Creating seperate PDF files...\n")
    createPDFFiles(pdfFileObj, chapters_to_grab, table_of_contents, pages)
    
    pdfFileObj.close()

if __name__ == "__main__":
    main()
