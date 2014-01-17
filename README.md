## AAPKaManch

Version: 0.0.1

License: GNU General Public License v3

Copyright: Contributors

Prototype of a platform to facilitate communication and information sharing among public, members and office bearers of Aam Aadmi Party.

Currently all information is shared via Facebook, Whatsapp, SMS, emails. There is no unified communication platform. If this platform is built, it will lead to information sharing and also enhance engagement of members.


### Install

AAP Ka Manch is built on MySQL and webnotes framework (Python). To install it locally, you will need to install

#### Pre-requisites

1. MySQL
1. Python-2.7
1. Python Setuptools (Python Package Manager)
1. Memcache

#### Steps

1. Start MySQL and memcache
1. Setup Python Virtualenv (optional - only if you are running multiple python projects requiring different versions of libraries)
1. Install pip: `sudo easy_install pip`
1. Create a `bench` directory
1. Clone `wnframework` in the `bench` as `webnotes`: `git clone https://github.com/webnotes/wnframework.git webnotes` and checkout `4.0.0-wip` branch
1. Install python libraries `sudo pip install webnotes/requirements.txt`
1. Clone `aapkamanch` in `bench`: `git clone https://github.com/AamAadmiParty/aapkamanch.git`
1. Install the packages: `pip install -e webnotes/` and `pip install -e aapkamanch/`
1. Create `sites` directory
1. Create `apps.txt`: `echo aapkamanch >> sites/apps.txt`
1. Change to `sites` directory
1. Setup a site: `webnotes test.appkamanch.org --install aapkamanch`
1. To test facebook login, add `127.0.0.1  test.aapkamanch.org` to `/etc/hosts`
1. Start serving: `webnotes test.aapkamanch.org --serve`
1. Start a browser and go to `http://test.aapkamanch.org:8000`

Putting it all together:

```
sudo easy_install pip
mkdir bench
cd bench
git clone https://github.com/webnotes/wnframework.git webnotes
cd webnotes
git checkout 4.0.0-wip
cd ..
sudo pip install webnotes/requirements.txt
git clone https://github.com/AamAadmiParty/aapkamanch.git
pip install -e webnotes/
pip install -e aapkamanch/
mkdir sites
echo aapkamanch >> sites/apps.txt
cd sites
webnotes test.appkamanch.org --install aapkamanch
webnotes test.aapkamanch.org --serve
```

#### Pulling Latest Updates

1. Update your git repositories
1. Go to `bench/sites` directory
1. Run `webnotes test.aapkamanch.org --latest`
1. Run `webnotes test.aapkamanch.org --build`
1. Run `webnotes test.aapkamanch.org --flush`

#### Admin Login

1. go to "/login"
1. Administrator user name: "Administrator"
1. Administrator passowrd "admin"

### Components

1. Database backend of all messages
1. Application layer that will map users and their roles.
1. Web front end
1. Mobile Apps for information collection and sharing.

### Roadmap

1. Build web prototype
1. Build mobile applications
1. Test and deploy live.

### Long Term vision

To build an extensible platform that will be the commnication / information backbone for AAP

1. To build a unified communication platform for AAP
1. To connect public, members, office bearers
1. Internal Communication
1. Resources - banners, leaflets, letter formats (for police permission etc)
1. Events - future and past and outcomes
1. Meeting minutes and follow-up
1. News
1. Election info - candidates, manifestoes etc

### Technology

1. Backend will by MySQL
1. Web app will be served by Webnotes framwork
1. Mobile apps in PhoneGap
1. Chat to implemented by HTTP polling (first cut)
1. No push-notifications - they are very annoying specially for high message volumes.

First target is to show proof of concept, once it is polished, the backend will be designed to be more scalable.

### Features for version 0.0.1

1. Zone classification
1. Chat application for public, members and committee members
1. Web and mobile applications

