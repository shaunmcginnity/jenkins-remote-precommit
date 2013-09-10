#!/usr/bin/env python
from JenkinsJob import JenkinsJob
import time
from optparse import OptionParser
import urllib2
from bs4 import BeautifulSoup
from scrapy.item import Item, Field
import sys

class BuildPackageSummary:
    def __init__(self,url):
        print "Getting summary for " + url
        try:
            soup = BeautifulSoup(urllib2.urlopen(url + "/cobertura/").read())
        except urllib2.HTTPError, e:
            print e
            sys.exit(1)

        statsTable = soup.find('table', attrs={'class':'pane sortable'})
        self.packages = dict()
        for row in statsTable.findChildren('tr', recursive=False):
            #print "Found row " + str(row)
            tds = row.find_all('td', recursive=False)
            if tds:
                package = tds[0].a.text
                files = self.getStatFromPackageTable(tds[1], "0/1")
                classes = self.getStatFromPackageTable(tds[2], "0/1")
                methods = self.getStatFromPackageTable(tds[3], "0/1") 
                lines = self.getStatFromPackageTable(tds[4], "0/1")
                conditionals = self.getStatFromPackageTable(tds[5], "0/1")
                self.packages[package] = {'package':package,
                                          'files':files, 
                                          'classes':classes,
                                          'methods':methods,
                                          'lines':lines,
                                          'conditionals':conditionals
                                         }        

    def getStatFromPackageTable(self,td,default):
        statTable = td.findChildren('td')
        return statTable[1].text if len(statTable) > 1 else default

    def dump(self):
        for package in self.packages:
            files = self.packages[package]['files'].split('/')
            print package + " " + self.packages[package]['files'] + " " + str(float(100 * int(files[0]) / int(files[1])))

    def compareTo(self, other):
        removed = []
        changed = []
        added = []
        for package in self.packages:
            thisPackage = self.packages[package]
            if package in other.packages:
                otherPackage = other.packages[package]
                if thisPackage != otherPackage:
                    changed.append([thisPackage, otherPackage])
            else:
                removed.append(thisPackage)

        for package in other.packages:
            if not package in self.packages:
                added.append(other.packages[package])

        return [removed, changed, added]

def main():
    parser = OptionParser()
    parser.add_option("-j", "--job",
                      dest="job",
                      help="")
    parser.add_option("-l", "--latest",
                      dest="latest",
                      action="store_true",
                      help="")
    parser.add_option("-b", "--buildId",
                      dest="buildId",
                      help="")

    (options, args) = parser.parse_args(sys.argv[1:])

    if options.job is None:
        usage()

    print "Using job : " + options.job
    job = JenkinsJob('http://jenkins.bfs.openwave.com:8080/jenkins', options.job) 

    info = job.Info()
    print info

    if options.latest:
        url = info['lastSuccessfulBuild']['url']
    else:
        if options.buildId:
            url = info['url'] + str(options.buildId)
        else:
            usage()

    print "Fetching " + url

    buildSummary = BuildPackageSummary(url)

    buildSummary.dump()

def usage():
    print "Invalid options:\n"
    print "BuildSummary.py -j <job> \n"
    sys.exit(0)


if __name__ == "__main__":
    main()
