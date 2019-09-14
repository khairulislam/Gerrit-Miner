from enum import Enum


class Gerrit(Enum):
    android = "https://android-review.googlesource.com"
    chromium = "https://chromium-review.googlesource.com"
    cloudera = "https://gerrit.cloudera.org"
    eclipse = "https://git.eclipse.org/r"
    gerrithub = "https://review.gerrithub.io"
    go = "https://go-review.googlesource.com"
    libreoffice = "https://gerrit.libreoffice.org"
    opencord = "https://gerrit.opencord.org"
    openstack = "https://review.openstack.org"
    unlegacy = "https://gerrit.unlegacy-android.org"
    qt = "https://codereview.qt-project.org"

    def __str__(self):
        return f"{self.name}"

