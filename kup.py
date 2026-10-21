# KENT: публикация обновления в GitHub. Запуск: python ~/kent-update/kup.py
import os,json,hashlib,re,shutil,subprocess
P=os.path.expanduser('~/tmp/SAMP-Mobile-GTA-2.11/app/')
U=os.path.expanduser('~/kent-update/')
lib=P+'build/intermediates/stripped_native_libs/debug/stripDebugDebugSymbols/out/lib/arm64-v8a/libsamp.so'
os.makedirs(U+'files/lib',exist_ok=True)
shutil.copy(lib,U+'files/lib/libsamp.so')
ver=int(re.search(r'versionCode\s*=\s*(\d+)',open(P+'build.gradle.kts',encoding='utf-8').read()).group(1))
apk_url=json.load(open(P+'src/main/assets/cache.json',encoding='utf-8')).get('apk_url','')
files=[]
for root,_,names in os.walk(U+'files'):
    for n in sorted(names):
        f=os.path.join(root,n); rel=os.path.relpath(f,U+'files').replace('\\','/')
        if not (rel.startswith('lib/') or rel.startswith('km/')): continue
        h=hashlib.md5(open(f,'rb').read()).hexdigest()
        sz=os.path.getsize(f)
        if sz>95*1024*1024: print('!! больше 95 МБ, GitHub не примет:',rel); continue
        files.append({'path':rel,'size':sz,'md5':h})
news=[]
if os.path.exists(U+'news.txt'):
    for l in open(U+'news.txt',encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('#'): continue
        d,t=(l.split('|',1)+[''])[:2] if '|' in l else ('',l)
        news.append({'d':d.strip(),'t':t.strip()})
links={}
if os.path.exists(U+'links.txt'):
    for l in open(U+'links.txt',encoding='utf-8'):
        if '=' in l and not l.strip().startswith('#'):
            k,v=l.split('=',1); links[k.strip()]=v.strip()
print('новостей',len(news),'ссылок',len(links))
json.dump({'apk_version':ver,'apk_url':apk_url,'news':news,'links':links,'files':files},open(U+'manifest.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for x in files: print(x['path'],x['size'])
print('apk_version',ver)
os.chdir(U)
subprocess.call(['git','add','-A'])
subprocess.call(['git','commit','-q','-m','update'])
subprocess.call(['git','push','-q'])
print('ОПУБЛИКОВАНО')
