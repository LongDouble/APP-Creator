import PyPDF2
import os

def OpenPDFFile(filename):
    try:
        print("\nAttempting to open " + filename + "...")
        PdfObject = open(filename, 'rb')
    except IOError:
        print("Can not open " + filename + "! Exiting...")
        input("\nPress enter to exit.")
        exit()
        
    print(filename + " opened successfully!")
    return PdfObject


def GetAPPName():
    if os.path.exists('PUTAPPHERE') and len(os.listdir('PUTAPPHERE')) == 1:
        APPName = os.listdir('PUTAPPHERE')
        return APPName[0]
    else:
        print("The folder \"PUTAPPHERE\" could not be found, is empty, or contains more than one file.\nCreate the folder and put your APP there. Exiting...")
        input("\nPress enter to exit.")
        exit()
    


def SetFileNames():
    with open("filenames.txt", "r") as file:
        filenames = eval(file.readline())

    return filenames


def SmartSearch(PdfObject, keyword, start_page = 0):
    PdfReader = PyPDF2.PdfFileReader(PdfObject)
    print("Searching for \'" + keyword + "\' in " + PdfObject.name)

    for i in range (start_page, PdfReader.getNumPages()):
        PageObject = PdfReader.getPage(i)
        PageText = PageObject.extractText()

        for characters in range(len(PageText)):
            if PageText[characters] == keyword[0]: #indicates first character matches

                for letters in range(1, len(keyword)):
                    characters = characters + 1

                    if characters == len(PageText): #we will go out of bounders otherwise
                        break

                    while PageText[characters] == '\n': #ignore line breaks
                        characters = characters + 1
                    
                    while PageText[characters] == ' ' and keyword[letters] != ' ': #ignore extra spaces
                        characters = characters + 1
                    
                    if PageText[characters] != keyword[letters]: #if two letters do not equal
                        break
                    elif (PageText[characters] == keyword[letters] and letters == (len(keyword) - 1)): #if end of word is reached and everything has matched
                        return i

    print("Was unable to find \'" + keyword + "\' in file.")
    return -1


def GetPageNumbers(PdfObject):
    print("\nScanning APP...\n")

    with open("keywords.txt", "r") as file:
        keywords = eval(file.readline())

    with open("alternate_keywords.txt", "r") as file:
        alternate_keywords = eval(file.readline())

    end_of_toc = SmartSearch(PdfObject, 'Plan prepared by:')

    page_numbers = {}

    print('\n')

    for key in keywords:
        page_numbers[key] = SmartSearch(PdfObject, keywords[key], end_of_toc)

        if page_numbers[key] == -1: # if it couldnt be found with normal search
            print("Searching with alternate keyword...")
            page_numbers[key] = SmartSearch(PdfObject, alternate_keywords[key], end_of_toc)

            if page_numbers[key] == -1:
                input("\nWas unable to find + \'" + keywords[key] + "\' or \'" + alternate_keywords[key] + "\'. Press enter to continue.")
        
        print("\n")

    page_numbers['inspectorqualifications'] = page_numbers['deficiencylogs'] # this should be mentioned on the same page as deficiency logs
    page_numbers['spillplan'] = page_numbers['drugprogram'] # mentioned on same page
    page_numbers['fireprotection'] = page_numbers['drugprogram'] # mentioned on same page
    
    return page_numbers


def constructPDF(PdfObject, filenames, page_numbers):
    PdfWriter = PyPDF2.PdfFileWriter()
    PdfReader = PyPDF2.PdfFileReader(PdfObject)

    for pages in range(PdfReader.numPages):
        files_to_add = []
        PdfWriter.addPage(PdfReader.getPage(pages))

        if pages in page_numbers.values():
            for keys in page_numbers: # figure out what documents go on that page
                if page_numbers[keys] == pages:
                    files_to_add.append(keys)
                
            for files in files_to_add:
                if files != 'ahafile' and files != 'resumefile' and files != 'osha30file' and files != 'certificationsfile':
                    PdfToAddObj = OpenPDFFile(filenames[files])
                    PdfToAddReader = PyPDF2.PdfFileReader(PdfToAddObj)

                    for i in range(PdfToAddReader.numPages):
                        PdfWriter.addPage(PdfToAddReader.getPage(i))

                else:
                    for contents in os.listdir(filenames[files]):
                        PdfToAddObj = OpenPDFFile(filenames[files] + '/' + contents)
                        PdfToAddReader = PyPDF2.PdfFileReader(PdfToAddObj)

                        for i in range(PdfToAddReader.numPages):
                            PdfWriter.addPage(PdfToAddReader.getPage(i))

    NewPdfFile = open('PUTAPPHERE/CompletedAPP.pdf', 'wb')
    PdfWriter.write(NewPdfFile)
    NewPdfFile.close()
    print("PDF Created Sucessfully!  It is in the \"PUTAPPHERE\" folder.")


def main():
    print("Email austinlgoergen@gmail.com to report any bugs.\n")
    input("Put your APP PDF in the folder named \"PUTAPPHERE\" then press enter.")
    filenames = SetFileNames()
    APPName = GetAPPName()
    PdfObject = OpenPDFFile('PUTAPPHERE/' + APPName)
    page_numbers = GetPageNumbers(PdfObject)
    constructPDF(PdfObject, filenames, page_numbers)
    PdfObject.close()

    print("\nThe following documents need to be manually inserted (if they are needed):\n")
    print("Crane Certifications (after equipment checklist)")
    print("Subcontractor Management Plan")
    print("Diagram of Barge or Floating Plant") 
    print("Checklist of Barge or Floating Plant (after diagram of barge)")

    if (-1) in page_numbers.values():
        print("\nWARNING: The following texts could not be found and must have their sections be manually inserted!\n")
        
        with open("keywords.txt", "r") as file:
            keywords = eval(file.readline())
        
        for keys in page_numbers:
            if page_numbers[keys] == -1 and keys in keywords.keys():
                print("Text: \'" + keywords[keys] + "\'")

    input("\nPress enter to exit.")


if __name__ == "__main__":
    main()
