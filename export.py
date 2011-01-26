# Akreggator archive to SQLite3 converter

import metakit as mk
import urlparse as up
import sqlite3 as sq3
from ConfigParser import ConfigParser

import md5
import zlib
import sys

size=0
idxarticle = 0
idxfeed = 0
nondupes = 0
count = 0
unread = 0
hash = dict()

# Get configuration from file

cparse = ConfigParser.ConfigParser()
cparse.read("export.cfg")

path = cparse.get("settings","akregator")
sq3file = cparse.get("settings","output")

indexfile = path + "archiveindex.mk4"

def readfeed(file):
    # Open a Metakit file, one file per blog, fetch contents
    global idxarticle
    blogdb = mk.storage(file,0)
    blogvw = blogdb.getas(blogdb.description())
    for i in blogvw:
        writedb_article(i)
        idxarticle = idxarticle + 1
    return

def getfeed(feed):
    # Read index of blogs from Akregator, translate into metakit database filenames
    global idxarticle
    sys.stdout.write("Reading "+feed.url+": ")
    writedb_feed(feed)
    file = feed.url
    site = up.urlparse(feed.url)
    file = file.replace(":","_")
    file = file.replace("/","_")
    file = path + file + ".mk4"
    readfeed(file)
    print idxarticle
    return

def initdb():
    # Initialize sqlite3 tables to receive data
    print "Deleting old tables"
    sqdb.execute("PRAGMA synchronous = OFF")
    sqdb.execute("drop table if exists blog") 
    sqdb.execute("drop table if exists article")
    sqdb.execute("drop table if exists content")
    sqdb.execute("drop table if exists contentindex")
    print "Creating new tables"
    sqdb.execute("create table blog(id integer, url text, totalCount integer, lastFetch integer)")
    sqdb.execute("create table article(id integer, idfeed integer, guid text, title text, url text, comments text, commentsLink text, status integer, pubDate integer, author text)")
    sqdb.execute("create table contentindex(id integer, id_content text)")
    sqdb.execute("create table if not exists tagindex(id integer, tag text)")
    sqdb.execute("create table if not exists tag(id integer, article integer)")
    sqdb.execute("create table content(id text, content blob)")
    return

def writedb_feed(feed):
    # Store the name of one blog to sqlite3 blog index
    global idxfeed
    insert = (idxfeed, feed.url, feed.totalCount, feed.lastfetch)
    sqdb.execute("insert into blog (id, url, totalCount, lastFetch) values(?, ?, ?, ?)", insert)    
    idxfeed = idxfeed + 1
    return

def writedb_article(article):
    # Store an article in sqlite3, generate unique hash per article to eliminate duplicate,
    # if not duplicated, gzip-compress and store as blob, also generate index-2-hash
    # index table
    global idxfeed,idxarticle,hash,nondupes
    m = md5.new()
    m.update(article.description)
    idx = m.hexdigest()
    insert = (idxarticle, idxfeed, article.guid, article.title, article.link, article.comments, article.commentsLink, article.status, article.pubDate, article.author)
    sqdb.execute("insert into article (id, idfeed, guid, title, url, comments, commentsLink, status, pubDate, author) values (?,?,?,?,?,?,?,?,?,?)", insert)
    insert2 = (idxarticle,idx)
    sqdb.execute("insert into contentindex(id, id_content) values(?, ?)", insert2)
    if idx not in hash:
    	insert = (idx, zlib.compress(article.description, 9))
        sqdb.execute("insert into content(id, content) values (?,?)", insert)
        hash[idx]=1        
	nondupes = nondupes+1
    return

print "Starting conversion:"
db=mk.storage(indexfile,0)
vw=db.getas(db.description())
print "Opening up database files"
sqdb = sq3.connect(sq3file)
initdb()

for i in vw:
    getfeed(i)

print "Imported "+str(idxarticle)+" articles (ignored "+str(idxarticle-nondupes)+" duplicates) from "+str(idxfeed)+" blogs"
print "Creating indexes:"
print "    Indexing article publishing dates..."
sqdb.execute("CREATE INDEX a_pubdate on article (pubDate ASC)")
print "    Indexing article's author names..."
sqdb.execute("CREATE INDEX a_author on article (author ASC)")
print "    Indexing articles...."
sqdb.execute("CREATE INDEX a_feed on article (idfeed ASC)")
print "    Indexing articles by content...."
sqdb.execute("CREATE INDEX c_id on content (id ASC)")
print "Indexing completed, now vacuuming database."
sqdb.execute("vacuum")
print "Vacuuming complete, now closing database."
sqdb.commit()
sqdb.close()
print "Finished!"
