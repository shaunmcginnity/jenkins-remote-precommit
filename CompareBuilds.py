#!/usr/bin/env python
from BuildPackageSummary import JenkinsJob, BuildPackageSummary
from optparse import OptionParser
import sys

def usage():
    print "Invalid options:\n"
    print "CompareBuilds.py -j <job> -1 <buildId1> [-2 <buildId2>]\n"
    print "If -2 build is omitted then -1 is compared to the last instrumented build for this pre-commit job"
    sys.exit(0)

def main():
    parser = OptionParser()
    parser.add_option("-j",
                      dest="job",
                      help="")
    parser.add_option("-1",
                      dest="buildId1",
                      help="")
    parser.add_option("-2",
                      dest="buildId2",
                      help="")
    parser.add_option("-l",
                      action="store_true",
                      dest="lines",
                      help="")
    parser.add_option("-c",
                      action="store_true",
                      dest="conditionals",
                      help="")

    (options, args) = parser.parse_args(sys.argv[1:])

    if not options.job:
        usage()

    print 'Using job %s' % (options.job)

    job = JenkinsJob('http://jenkins.bfs.openwave.com:8080/jenkins',
                     options.job) 

    metrics = []
    if options.lines:
        metrics.append('lines')
    if options.conditionals:
        metrics.append('conditionals')

    if 0 == len(metrics):
        metrics = ['files', 'methods', 'lines', 'classes', 'conditionals']

    print 'Using metrics %s' % (metrics)

    url1 = job.Info()['url'] + str(options.buildId1)

    if options.buildId2:
        url2 = job.Info()['url'] + str(options.buildId2)
    else:
        instrumentedJobLabel = 'Instrumented_' + options.job.replace('Pre-Commit_', '')
        print "Instrumented : " + instrumentedJobLabel
        instrumentedJob = JenkinsJob('http://jenkins.bfs.openwave.com:8080/jenkins',
                                     instrumentedJobLabel)
        url2 = instrumentedJob.Info()['lastSuccessfulBuild']['url']
        tmpUrl = url1
        url1 = url2
        url2 = tmpUrl

    buildSummary1 = BuildPackageSummary(url1)
    buildSummary2 = BuildPackageSummary(url2)

    [removed, changed, added] = buildSummary1.compareTo(buildSummary2)

    reports = []
    sums = dict()
    counts = dict()
    for metric in metrics:
        counts[metric] = 0
        sums[metric] = 0
    
    for [old, new] in changed:
        for metric in metrics:
            [hit, total, ratio, delta] = compare(old, new, metric)
            if hit != '-' or total != '-':
                counts[metric] += 1
                sums[metric] += delta
                reports.append(report(new['package'], metric, hit, total, ratio, delta))

    if reports:
        print 'Changed\n%s\n%s' % (reportHeader(), ''.join(reports))
        print '\n%s %s\n' % (counts, sums)

    reports = []
    for new in added:
        for metric in metrics:
            [hit, total, ratio, delta] = compare([], new, metric)
            if hit != '-' or total != '-':
                reports.append(report(new['package'], metric, hit, total, ratio, delta))

    if reports:
        print 'Added\n%s\n%s' % (reportHeader(), ''.join(reports))
    #print ''.join(reports)

def diff(old, new):
    if old == new:
        return ['- %d:%d' % (new, new), 0]

    if old < new:
        return ['^ %d:%d' % (old, new), new - old]

    return ['v %d:%d' % (old, new), old - new]

def compareDiffs(hitDiff, totalDiff):
    if hitDiff > totalDiff:
        return '^ %d' % (hitDiff - totalDiff)
    else:
        if hitDiff == totalDiff:
            return '- %d' % (totalDiff - hitDiff)
        else:
            return 'v %d' % (totalDiff - hitDiff)

def ratio(hit, total) :
    if total == 0:
       return 0.0 
    return float(hit) / float(total)

def compare(old, new, idx):
    oldMetric = '0/0'

    if idx in old:
        if old[idx] == new[idx]:
            return ['-', '-', '-', '-']
        else:
            oldMetric = old[idx]

    oldVal = oldMetric.split('/')
    newVal = new[idx].split('/')
    oldHit = int(oldVal[0])
    newHit = int(newVal[0])
    oldTotal = int(oldVal[1])
    newTotal = int(newVal[1])

    hit = '-'
    total = '-'
    hitDiff = 0
    totalDiff = 0
    if newHit == 0:
        hit = '! %s:%s'  % (oldVal[0], newVal[0])
        [total, totalDiff] = diff(oldTotal, newTotal)
        return [hit, total, 0.0, 100*(ratio(newHit, newTotal) - ratio(oldHit,oldTotal))] #compareDiffs(0, totalDiff)]

    [hit, hitDiff] = diff(oldHit, newHit)
    [total, totalDiff] = diff(oldTotal, newTotal)

    return [hit, total, 100*(ratio(newHit,newTotal)), 100*(ratio(newHit,newTotal) - ratio(oldHit,oldTotal))] #compareDiffs(hitDiff, totalDiff)]

def reportHeader():
    return '%50s   %15s   %20s     %20s    %7s    %s\n\n' % ('Package', 'Metric', 'Hits', 'Total', '% ', 'Delta')

def report(package, metric, hit, total, ratio, delta):
    return '%50s   %15s   %20s     %20s    %7.2f  %7.2f\n' % (package, metric, hit, total, ratio, delta)


#                   total
#                   same          up            down
#   hits    same    -             RED           GREEN
#           up      GREEN         UNKNOWN       GREEN
#           down    RED           RED           UNKNOWN

if __name__ == "__main__":
    main()
