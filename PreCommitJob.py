#!/usr/bin/env python
import jenkins
import time
import p4Change
from optparse import OptionParser
import sys

class PreCommitJob:
    def __init__(self, url, user, password, jobId, p4ShelfNum, reviewBoardId = 0):
        self.url = url
        self.jenkins = jenkins.Jenkins(url, user, password)
        self.jobId = jobId
        self.p4ShelfNum = p4ShelfNum
        self.reviewBoardId = reviewBoardId
        info = self.Info()

        # if there is a job in the queue then we don't
        # submit another as we can't get a reliable build number for it
        if info['queueItem'] is None:
            self.buildable = True
        else:
            self.buildable = False

    def Info(self):
        return self.jenkins.get_job_info(self.jobId)

    def Build(self):
        if self.buildable is False:
            return 0

        nextBuild = self.Info()['nextBuildNumber']
        print str(nextBuild) + "\n"
        self.jenkins.build_job(self.jobId, {'SHELVE':self.p4ShelfNum, 'REVIEWBOARD_ID':self.reviewBoardId, 'token':'opwv'})
        return nextBuild
       
    def URLFor(self, buildNumber):
        return self.url + "/" + self.jobId + "/" + str(buildNumber)


parser = OptionParser()
parser.add_option("-r", "--review",
                  dest="reviewBoardId",
                  help="")
parser.add_option("-c", "--change",
                  dest="p4ChangeNum",
                  help="")
parser.add_option("-u", "--user",
                  dest="user",
                  help="")
parser.add_option("-p", "--password",
                  dest="password",
                  help="")
parser.add_option("-j", "--job",
                  dest="job",
                  help="")

(options, args) = parser.parse_args(sys.argv[1:])

precommitJob = PreCommitJob('http://jenkins.bfs.openwave.com:8080/jenkins',
                            options.user,
                            options.password,
                            options.job, 
                            options.p4ChangeNum, options.reviewBoardId)

buildNum = precommitJob.Build()
if buildNum is 0:
    print "Can't submit pre-commit build : job already queued\n";
else:
    buildUrl = precommitJob.URLFor(buildNum)
    print "Build URL : " + buildUrl
    p4Change = p4Change.P4Change(options.p4ChangeNum)
    p4Change.AddToDescription("Pre-Commit: " + buildUrl)
    p4Change.Save()

