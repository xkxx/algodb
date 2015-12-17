import redis
from os import chdir
from subprocess import check_call as call
import traceback

rd = redis.StrictRedis(host='localhost', port=6379, db=0)

try:
    mapping_keys = rd.keys("rosetta-mapping-*")
    for key in mapping_keys:
        rd.delete(key)

    call(["curl", "-XDELETE", "http://localhost:9200/throwtable"])
    chdir("../elasticsearch_dumps/shared/")
    call(["bash", "restore_shared.sh"])
    chdir("../../AlgorithmNames")

    # check this script
    call(["python2", "index_elasticsearch_rosetta_using_crosswikis.py"])

    chdir("../elasticsearch_dumps/")
    # check this script
    call(["bash", "backup_elasticsearch.sh"])
    chdir("../AlgorithmNames")

    for doc_type in ['category', 'algorithm', 'implementation']:
        print '# of lines in %s: (remember to substract 2)' % doc_type
        call(["sed", "-n", "$=",
            "../elasticsearch_dumps/elasticsearch_%s_v4.4.json" % doc_type])

    for key in ['rosetta-mapping-similars-success',
    'rosetta-mapping-success-wikipedia-autosuggest',
    'rosetta-mapping-success-crosswikis',
    'rosetta-mapping-success-all-algo-links']:
        print key,
        print rd.scard(key)
except Exception, e:
    print e
    print(traceback.format_exc())
# finally:
    # call(["vlc", "/home/minjingzhu/Dropbox/MUSIC/copy.mp3"])
