from ipam.choices import IPAddressRoleChoices
from ipam.models import IPAddress, Prefix
from extras.reports import Report
from django.db.models import Q

# UniqueIPReport was forked from https://gist.github.com/dgarros/acc23b4fd8d42844b8a41f695e6cb769
class UniqueIPReport(Report):
    description = "Validate that we don't have an IP address allocated multiple times in the network"

    def test_unique_ip(self):
        already_found = []
        for ip in IPAddress.objects.exclude(Q(role=IPAddressRoleChoices.ROLE_ANYCAST) | Q(role=IPAddressRoleChoices.ROLE_VIP) | Q(role=IPAddressRoleChoices.ROLE_VRRP)):
            abort = False
            for i in already_found:
                if str(ip) == str(i):
                    msg = "IP skipped - Duplicate"
                    self.log_info(ip,msg)
                    abort = True

            if abort == False:
                duplicates = ip.get_duplicates()
                real_dup = 0
                for duplicate in duplicates:
                        if duplicate.interface:
                            real_dup +=1
                            if real_dup != 0:
                                already_found.append(str(ip))
                                msg = "Has %s duplicate IPs" % real_dup
                                self.log_warning( ip, msg )
                duplicates = None

class UniquePrefixReport(Report):
    description = "Validate that we don't have a Prefix allocated multiple times in a VRF"

    def test_unique_prefix(self):
        for prefix in Prefix.objects.all():
            duplicate_prefixes = Prefix.objects.filter(vrf=prefix.vrf, prefix=str(prefix.prefix)).exclude(pk=prefix.pk)
            if len(duplicate_prefixes) > 0 :
                msg = "has %s duplicate prefix(es)" % len(duplicate_prefixes)
                self.log_failure( prefix, msg )
