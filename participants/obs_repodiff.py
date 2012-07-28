#!/usr/bin/python

from boss.obs import BuildServiceParticipant
import repo_diff

class ParticipantHandler(BuildServiceParticipant):

    def handle_wi_control(self, ctrl):
        pass

    @BuildServiceParticipant.get_oscrc    
    def handle_lifecycle_control(self, ctrl):
        if ctrl.message == "start":
            self.reposerver = ctrl.config.get("obs_repodiff", "reposerver")

    @BuildServiceParticipant.setup_obs
    def handle_wi(self, wi):
        if not wi.params.source or not wi.params.target:
            raise RuntimeError("Missing mandatory parameters source and target")
        if not wi.fields.msg:
            wi.fields.msg = []

        for repo in self.obs.getProjectRepositories(wi.params.source):
            if repo in wi.fields.exclude_repos:
                continue
            else:
                src_url = "%s/%s/%s" % ( self.reposerver, wi.params.source.replace(":",":/"), repo)
                break
        for repo in self.obs.getProjectRepositories(wi.params.target):
            if repo in wi.fields.exclude_repos:
                continue
            else:
                trg_url = "%s/%s/%s" % ( self.reposerver, wi.params.target.replace(":",":/"), repo)

        if wi.params.mode == "short":
            report = repo_diff.generate_short_diff([src_url], [trg_url])
        elif wi.params.mode == "long":
            report = repo_diff.generate_report([src_url], [trg_url])
        else:
            raise RuntimeError("unknown report mode %s" % wi.params.mode)

        wi.result = True
        if report:
            print report
            wi.result = False
            wi.fields.msg.append("Changes in project %s compared to %s, please check." % (wi.params.source, wi.params.target))
            wi.fields.msg.extend(report.split("\n"))