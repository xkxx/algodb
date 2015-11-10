import xmlrpclib
import urllib2
import json

client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')

def getListPkgs():
  return client.list_packages()

def getPkgInfo(pkgName):
  data = json.load(urllib2.urlopen("http://pypi.python.org/pypi/%s/json" % pkgName))
  info = data["info"]
  latestVer = info["version"]
  latestPkg = data["releases"][latestVer][0]["url"]  

  return {
    "name": info["name"],
    "summary": info["summary"],
    "description": info["description"],
    "docs_url": info["docs_url"],
    "version": info["version"],
    "downloads": info["downloads"]["last_month"],
    "classifiers": info["classifiers"],
    "home_page": info["home_page"]
  }   

if __name__ == "__main__":
    import sys
    print getPkgInfo(sys.argv[-1])
    

