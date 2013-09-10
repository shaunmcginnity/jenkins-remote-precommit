import jenkins

class JenkinsJob:
    def __init__(self, url, jobId):
        self.url = url
        self.jenkins = jenkins.Jenkins(url)
        self.jobId = jobId
        info = self.Info()

    def Info(self):
        return self.jenkins.get_job_info(self.jobId)
    

