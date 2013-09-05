#!/usr/bin/env python
from BuildPackageSummary import JenkinsJob, BuildPackageSummary
from optparse import OptionParser
import sys

parser = OptionParser()
parser.add_option("-u", "--user",
                  dest="user",
                  help="")
parser.add_option("-p", "--password",
                  dest="password",
                  help="")
parser.add_option("-j",
                  dest="job",
                  help="")
parser.add_option("-1",
                  dest="buildId1",
                  help="")
parser.add_option("-2",
                  dest="buildId2",
                  help="")

(options, args) = parser.parse_args(sys.argv[1:])

def usage():
    print "Invalid options:\n"
    print "JobStatus.py -c <changeNum> -u <user> -p <password> -j <job> [-r <reviewId>]\n"
    sys.exit(0)

print "Using -> " + options.job

job = JenkinsJob('http://jenkins.bfs.openwave.com:8080/jenkins',
                 options.user,
                 options.password,
                 options.job) 

url1 = job.Info()['url'] + str(options.buildId1)

if options.buildId2:
    url2 = job.Info()['url'] + str(options.buildId2)
else:
    instrumentedJobLabel = 'Instrumented_' + options.job.replace('Pre-Commit_', '')
    print "Instrumented : " + instrumentedJobLabel
    instrumentedJob = JenkinsJob('http://jenkins.bfs.openwave.com:8080/jenkins',
                                 options.user,
                                 options.password,
                                 instrumentedJobLabel)
    print instrumentedJob.Info()
    url2 = instrumentedJob.Info()['lastSuccessfulBuild']['url']
    tmpUrl = url1
    url1 = url2
    url2 = tmpUrl

buildSummary1 = BuildPackageSummary(url1)
buildSummary2 = BuildPackageSummary(url2)


[removed, changed, added] = buildSummary1.compareTo(buildSummary2)

print removed
print "\n\n"
print changed
print "\n\n"
print added

def compare(old, new, idx):
    if old[idx] == new[idx]:
        return ['-', '-']

    oldVal = old[idx].split('/')
    newVal = new[idx].split('/')
    hit = '-'
    total = '-'
    if newVal[0] == '0':
        hit = '!' + " " + oldVal[0] + "/" + newVal[0]
        total = '!' + " " + oldVal[1] + "/" + newVal[1]
        return [hit, total]

    if not oldVal[0] == newVal[0]:
        old = int(oldVal[0])
        new = int(newVal[0])
        if old < new:
            hit = '^ %d/%d %d' % (old, new, (new - old))
        else:
            hit = 'v %d/%d %d' % (old, new, (old - new))
    if not oldVal[1] == newVal[1]:
        old = int(oldVal[1])
        new = int(newVal[1])
        if old < new:
            total = '^ %d/%d %d' % (old, new, (new - old))
        else:
            total = 'v %d/%d %d' % (old, new, (old - new))

    return [hit, total]

def report(package, metric, hit, total):
    print "%50s : %15s : hits %20s     total %20s" % (package, metric, hit, total)

for [old, new] in changed:
    for metric in ['files', 'methods', 'lines', 'classes', 'conditionals']:
        [hit, total] = compare(old, new, metric)
        if hit != '-' or total != '-':
            report(old['package'], metric, hit, total)

#                   total
#                   same          up            down
#   hits    same    -             RED           GREEN
#           up      GREEN         UNKNOWN       GREEN
#           down    RED           RED           UNKNOWN

