import argparse
import PyPDF2
from os import listdir, mkdir
from os.path import isfile, join, isdir
from tkinter import filedialog
from tkinter import *
from pprint import pprint 
from sys import platform
from shutil import copyfile
import re

class Sorter:
    def __init__(self):
        self.seenNames = []

    def getFolderNames(self, parentFolder):
        return [join(parentFolder, f) for f in listdir(parentFolder) if not isfile(join(parentFolder, f))]

    def getFileNames(self, folderName):
        return [join(folderName, f) for f in listdir(folderName) if isfile(join(folderName, f))]

    def getFirstPage(self, f):
        fileObj = open(f, 'rb')
        pdfReader = PyPDF2.PdfFileReader(fileObj, strict=False)
        firstPage = pdfReader.getPage(0)
        return firstPage.extractText().encode('utf-8')

    def getNameAndGrade(self, string):
        encoding = 'utf-8'
        string = string.decode(encoding).replace('\n', '')
        name = re.search('Student Name: (.*) ASN', string)
        grade = re.search('Grade Level: (.*) DOB', string)

        try:
            name = name.group(1)
            grade = grade.group(1)
        except AttributeError as e:
            print(string)
            return None, None
        return name, grade

    def renameAndSortFile(self, name, grade, filepath, folder):

        if platform == 'win32':
            folderDivider = '\\'
        else:
            folderDivider = '/'

        if name == None or grade == None:
            filename = filepath.split(folderDivider)[-1]
            fixfold = folder + folderDivider + 'fix'
            if not isdir(fixfold):
                mkdir(fixfold)
            fixFolderPath = fixfold + folderDivider + filename
            copyfile(filepath, fixFolderPath)
            return

        folderNames = self.getFolderNames(folder)
        
        gradeFolder = folder + folderDivider + 'grade' + str(grade)
        
        if not isdir(gradeFolder):
            mkdir(gradeFolder)

        name = ', '.join(name.split(' ', 1)[::-1])

        if name in self.seenNames:
            self.seenNames.append(name)
            n = len([x for x in self.seenNames if x == name])
            newFileName = name + '_' + str(n) + '.pdf'
        else:
            self.seenNames.append(name)
            newFileName = name + '.pdf'

        newFilePath = gradeFolder + folderDivider + newFileName

        copyfile(filepath, newFilePath)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rename pdfs and sort into folders')
    parser.add_argument('--in', dest='inFolder', type=str,
        help='The folder containing original files')
    
    args = parser.parse_args()

    if not args.inFolder:
        root = Tk()
        root.withdraw()
        args.inFolder = filedialog.askdirectory()

    sorter = Sorter()
    
    fileNames = sorter.getFileNames(args.inFolder)

    for f in fileNames:
        pagestring = sorter.getFirstPage(f)
        name, grade = sorter.getNameAndGrade(pagestring)
        sorter.renameAndSortFile(name, grade, f, args.inFolder)

