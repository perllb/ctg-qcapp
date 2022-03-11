from collections import Counter
import numpy as np
from os.path import exists
from datetime import datetime
import time
import os
import re
from flask import Blueprint,render_template, jsonify,request, redirect, url_for, flash
from flask_login import login_required, current_user
import datetime as dt
import glob
import csv
import locale as l
import pandas as pd
from collections import OrderedDict
from .models import db, CTGdata
from .listnewfiles import listnewfiles
listers = Blueprint('listers', __name__)
from . import app

# List projects html files
@listers.route('/qc_<proj>')
@login_required
def list_projhtml(proj):
    htmls = {}
    projdir = "na"
    rundir = "na"
    mode = "na"
    for root, dirnames, filenames in os.walk(app.config['QC_FOLDER']):
        for dir in dirnames:
            if proj == dir:
                projdir=root + "/" + dir
    # if there is a suffix after projid (e.g. 2021_202_Username)
    # try to search for a dir that starts with projid
    if projdir == "na":
        for root, dirnames, filenames in os.walk(app.config['QC_FOLDER']):
            for dir in dirnames:
                dirproj=dir[0:8]
                if dirproj == proj:
                    if "/qc/" in root:
                        empty=""
                    elif "web-summaries" in root:
                        empty=""
                    else:
                        projdir=root + "/" + dir

    if projdir != "na":
        for root, dirnames, filenames in os.walk(projdir):
            mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
            rundir=root.replace(app.config['STATIC_FOLDER'],"").split("/")[3]
            if mode == "ctg-rnaseq":
                mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[3]
                rundir=root.replace(app.config['STATIC_FOLDER'],"").split("/")[4]
                
            for file in filenames:
                if file.endswith('.html'):
                    path = root.replace(app.config['STATIC_FOLDER'],"")
                    htmls[file] = path + "/" + file
        sorthtml=dict(reversed(sorted(htmls.items())))
        #return jsonify (dirs=rundir)
    else:
        flash('No QC for Project "' + proj + '" exists in webapp','error')
        return redirect(url_for('ctgdata.ctgdata_ctgproj'))
    return render_template('list_proj_html.html',result=sorthtml,qctype=mode,rundir=rundir,proj=proj,qcdir=projdir)

# List projects html files
@listers.route('/newqc')
@login_required
def list_new_proj():
    sortnewproj,sortnewinterop,days = listnewfiles(14)
    return render_template('news.html',new_proj=sortnewproj,new_interop=sortnewinterop,days=days)

# List all root QC dirs (pipelines) in ctg-qc
@listers.route('/ctg-pipelines')
@login_required
def pipelist():
    statqc=app.config['QC_FOLDER']
    d={}
    for dir in os.listdir(statqc):
        if "interop" not in dir:
            if os.path.isdir(os.path.join(statqc, dir)):
                dir2 = dir.replace('ctg-','').upper()
                d[dir2] = dir
    sortdict=dict(sorted(d.items()))
    return render_template('pipedirs.html',result=sortdict)

# List new project folders
@listers.route('/projdirs')
@login_required
def list_all_projdir():
    projdirs={}
    qcdir=app.config['QC_FOLDER']
    for root, dirs,files in os.walk(qcdir):
        for dir in dirs:
            # Only get project folders
            pattern = re.compile("^202[0-9]_[0-9]*")
            if pattern.search(dir):
                if not dir.endswith('data') and not "archive" in root:
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                    if mode == "ctg-rnaseq":
                        mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[3]
                    # Get runfolder of project
                    # Search on first 8 chars (202*_***) of director only
                    proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                    if proj:
                        runfolder = proj.runfolder
                    else:
                        # Search full dirname
                        proj = CTGdata.query.filter_by(projid=dir).first()
                        if proj:
                            runfolder = proj.runfolder
                        # It might be that the CTGdata project has a suffix, such as 202*_***_suffix
                        else:
                            proj = CTGdata.query.filter(CTGdata.projid.contains(dir[0:8])).first()
                            if proj:
                                runfolder = proj.runfolder
                            else:
                                runfolder = "na"
                    projdirs[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]
            # Only test project folders
            pattern = re.compile("^202[0-9]_*est*")
            if pattern.search(dir):
                if not dir.endswith('data') and not "archive" in root:
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                    # Get runfolder of project
                    proj = CTGdata.query.filter_by(projid=dir).first()
                    if proj:
                        runfolder = proj.runfolder
                    else:
                        runfolder = "na"
                    projdirs[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]
            
    sortnew=dict(reversed(sorted(projdirs.items())))
    return render_template('list_all_projdir.html',result=sortnew)

@listers.route('/projsearch_post', methods=['POST'])
@login_required
def projsearch_post():
    # Retrieve posts from ctg_data.html
    search_proj = request.form.get('search_proj')
    qcdir=app.config['QC_FOLDER']
    projdirs={}
    for root, dirs,files in os.walk(qcdir):
        for dir in dirs:
            # Only get project folders
            if search_proj in dir:
                if not dir.endswith('data'):
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                    # Get runfolder of project
                    proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                    if proj:
                        runfolder = proj.runfolder
                    else:
                        runfolder = "na"
                        projdirs[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]
    if len(projdirs) == 0:
        flash('No project matched your search "' + search_proj + '"','error')
    else:
        flash('Search results for "*' + search_proj + '*"','success')
    
    return render_template('list_all_projdir.html',result=projdirs)


# List all project qc output from given pipeline (mode)
@listers.route('/ctg-pipeline_<mode>')
@login_required
def list_projdir(mode):
    modedir=app.config['QC_FOLDER'] + "/" + mode
    dproj={}

    # For CTG-RNASEQ
    if mode == 'uroscan' or mode == 'rnaseq_total' or mode == 'rnaseq_mrna':
        modedir=app.config['QC_FOLDER'] + "/ctg-rnaseq/" + mode
        
    # Get all projects for pipeline (mode)
    for root, dirnames, filenames in os.walk(modedir):
        for dir in dirnames:
            pattern = re.compile("^202[0-9]_[0-9]*")
            patternTest = re.compile("^202[0-9]_test*")
            pattern2 = re.compile("^2[0-9][0-9][0-9][0-9][0-9]-s")
            if (pattern.search(dir) or pattern2.search(dir) or patternTest.search(dir)) and not dir.endswith("_data") and not dir.endswith("_data_1"):
                st = os.stat(root + "/" + dir)
                mtime = dt.datetime.fromtimestamp(st.st_mtime)
                # Get runfolder of project
                # Get runfolder of project
                # Search on first 8 chars (202*_***) of director only
                proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                if proj:
                    runfolder = proj.runfolder
                else:
                    # Search full dirname
                    proj = CTGdata.query.filter_by(projid=dir).first()
                    if proj:
                        runfolder = proj.runfolder
                    # It might be that the CTGdata project has a suffix, such as 202*_***_suffix
                    else:
                        proj = CTGdata.query.filter(CTGdata.projid.contains(dir[0:8])).first()
                        if proj:
                            runfolder = proj.runfolder
                        else:
                            runfolder = "na"
                dproj[dir] = [str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]

    # Get meta_cellranger multiqc
    metaqc_fullpath=app.config['QC_FOLDER'] + "/" + mode + "/meta_cellranger_" + mode + "_metrics_all.html"
    metaqc= "ctg-qc/" + mode + "/meta_cellranger_" + mode + "_metrics_all.html"
    # Set variable to tell html whether to display the meta qc
    sendmeta="0"
    if exists(metaqc_fullpath):
        sendmeta="1"
        
    sortdict=dict(reversed(sorted(dproj.items())))
    #return jsonify(dirs=sortdict)
    return render_template('list_projdir.html',result=sortdict,qctype=mode,metaqc=metaqc,sendmeta=sendmeta)

# List all interop html files
@listers.route('/interop')
@login_required
def interop():
    # in interop dir 
    sinteropdir=app.config['QC_FOLDER'] + "/interop"
    interopreps=os.listdir(sinteropdir)
    d={}
    for rep in interopreps:
        if not rep.endswith('_data') and not rep == "occ-pf-q-score-plots" and not rep == "archive":
            run_id = rep.replace("multiqc_ctg_interop_","")
            run_id = run_id.replace(".html","")
            st = os.stat(sinteropdir + "/" + rep)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            ## occupied vs PF plots
            occpffile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/occ_pf." + run_id + "_mqc.png"
            if "_A0" in run_id:
                if exists("/srv/flask/qcapp/" + occpffile):
                    occpf = occpffile
                else:
                    occpf = "na"
            else:
                occpf = "na"
            ## q-score heatmap
            qscorefile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_q-heat-map_mqc.png"
            qscoreheat="na"
            if exists("/srv/flask/qcapp/" + qscorefile):
                qscoreheat = qscorefile
            ## q-score hist
            qscorefile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_q-histogram_mqc.png"
            qscorehist="na"
            if exists("/srv/flask/qcapp/" + qscorefile):
                qscorehist = qscorefile
            ## cell cycle intensity
            ccfile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_Intensity-by-cycle_Intensity_mqc.png"
            ccint="na"
            if exists("/srv/flask/qcapp/" + ccfile):
                ccint = ccfile
            ## cell cycle intensity
            ccflowfile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_flowcell-Intensity_mqc.png"
            ccflow="na"
            if exists("/srv/flask/qcapp/" + ccflowfile):
                ccflow = ccflowfile
            ## Cluster PF
            clusterfile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_ClusterCount-by-lane_mqc.png"
            clusterC="na"
            if exists("/srv/flask/qcapp/" + clusterfile):
                clusterC = clusterfile
            d[run_id] = [sinteropdir + rep , str(mtime.date()) + " - " + str(mtime.time())[0:8],occpf,qscoreheat,qscorehist,ccint,ccflow,clusterC]
    # sunnys runs
    sinteropdir=app.config['QC_FOLDER'] + "/sunny/runfolders"
    interopreps=os.listdir(sinteropdir)
    for rep in interopreps:
        if not rep.endswith('_data'):
            run_id = rep.replace("multiqc_ctg_","")
            run_id = run_id.replace("_seqonly.html","")
            st = os.stat(sinteropdir + "/" + rep)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            # sunnys runfolders does not exist, and we can not plot these Interop plots
            d[run_id] = [sinteropdir + rep , str(mtime.date()) + " - " + str(mtime.time())[0:8],"na","na","na","na","na","na"]
    sortdict=dict(reversed(sorted(d.items())))
    return render_template('list_interop_html.html',result=sortdict, qctype='Interop QC reports')

# Go to runfolder interopqc html file (if exists)
@listers.route('/qc_interop_<run>')
def interop_html(run):
    interopqc = "na"
    for root, dirnames, filenames in os.walk(app.config['QC_FOLDER'] + '/interop/'):
        for file in filenames:
            if file == "multiqc_ctg_interop_"+run+".html":
                interopqc="ctg-qc/interop/" + file
    if interopqc != "na":
        return redirect(url_for('static', filename=interopqc))
    else:
        # If not found, check in sunny runfolders
        for root, dirnames, filenames in os.walk(app.config['QC_FOLDER'] + '/sunny/runfolders/'):
            for file in filenames:
                if file == "multiqc_ctg_"+run+"_seqonly.html":
                    interopqc="ctg-qc/sunny/runfolders/" + file
        # found in arhive - send report html
        if interopqc != "na":
            return redirect(url_for('static', filename=interopqc))
        # if not found, report error
        else:
            flash('No interop QC for runfolder "' + run + '" exists in webapp','error')
            return redirect(url_for('listers.interop'))
        

# Go to runfolder occ pf _mqc.png  file (if exists)
@listers.route('/qc_interop_occpf_<run>')
def interop_occpf(run):
    interopqc = "na"
    files={}
    for root, dirnames, filenames in os.walk(app.config['QC_FOLDER'] + '/interop/occ-pf-q-score-plots'):
        for file in filenames:
            files[file] = filenames
            if file == "occ_pf."+run+"_mqc.png":
                interopqc="ctg-qc/interop/occ-pf-q-score-plots/" + file
#    return jsonify(files)
    if interopqc != "na":
        return redirect(url_for('static', filename=interopqc))
        #return jsonify (dirs=rundir)
    else:
        flash('No occ-pf plot for runfolder "' + interopqc + '" exists in webapp','error')
        return redirect(url_for('listers.interop'))

# Go to runfolder png interop file (if exists)
@listers.route('/qc_interop_plot_<run>/<plot>')
def interop_run_plot(run,plot):
    interopqc = "na"
    files={}
    for root, dirnames, filenames in os.walk(app.config['QC_FOLDER'] + '/interop/occ-pf-q-score-plots'):
        for file in filenames:
            files[file] = filenames
            if file == run+"_"+plot+"_mqc.png":
                interopqc="ctg-qc/interop/occ-pf-q-score-plots/" + file
#    return jsonify(files)
    if interopqc != "na":
        return redirect(url_for('static', filename=interopqc))
        #return jsonify (dirs=rundir)
    else:
        flash('No ' + plot + " for runfolder " + run + " exists in webapp",'error')
        return redirect(url_for('listers.interop'))

# Display ls4 squeue
@listers.route('/ctg-squeue')
@login_required
def squeue():
    squeue={}
    file3 = app.config['STATIC_FOLDER'] + "/cron/squeue.current.txt" # squeue ls4 each minute
    sq = pd.read_csv(file3,delim_whitespace=True,index_col=0,skiprows=1)
    squeue = sq.to_html()
    # Read date of squeue file
    sqtid = ""
    with open(file3, "r") as file:
        sqtid = file.readline().strip()
        for last_line in file:
            pass
    
    return render_template('squeue.html',squeue=squeue,sqtid=sqtid)

# Display runfolder sync log
@listers.route('/ctg-rf-sync')
@login_required
def rfsync():
    sync={}
    file2n = app.config['STATIC_FOLDER'] + "/cron/log.ctg.runfolder.snc.ls4"
    file2 = open(file2n, 'r',errors='ignore') # trannel ls4 sync log
    file2tid=time.ctime(os.path.getmtime(file2n))
    # Read file2
    count=0
    while True:
        count += 1
        # Get next line from file
        lineraw = file2.readline()
        line = lineraw.replace(" CET","")
        # if line is empty
        # end of file is reached
        if not line:
            break
        # get type of info
        type=""
        if "New CTG" in line:
            type="completed"
        if "identified" in line:
            type="identified"
        if "Starting sync" in line or "STARTED" in line:
            type="start"
        if "Synced" in line or "COMPLETED" in line:
            type="synced"
        if "FAILED" in line:
            type="failed"
        sync[count] = [line.strip("> "),type]
    file2.close()
    
    revsync = OrderedDict(sorted(sync.items(), reverse=True, key=lambda t: t[0]))
    return render_template('rfsync.html',sync=revsync,runtid=file2tid)

# Display runfolder sync log
@listers.route('/ctg-ls4-cron')
@login_required
def ls4cron():
    ls4={}
    file1n = app.config['STATIC_FOLDER'] + "/cron/ctg-cron.log"
    file1 = open(file1n, 'r',errors='ignore') # ls4 automation log
    
    # Get time of update cron log and runfolder sync files
    file1tid=time.ctime(os.path.getmtime(file1n))
        
    # Read file1
    count = 0
    while True:
        count += 1
        # Get next line from file
        lineraw = file1.readline()
        line = lineraw.replace(" CET","")
        # if line is empty
        # end of file is reached
        if not line:
            break
        # get type of line
        type=""
        if "interop" in line:
            type="interop"
        if "sav-save" in line:
            type="sav-save"
        if "parse-samplesheet" in line:
            type="parse-samplesheet"
        if "panel-tumor-only" in line:
            type="panel-tumor-only"
        if "sc-rna-10x" in line:
            type="sc-rna-10x"
        if "sc-multi-10x" in line:
            type="sc-multi-10x"
        if "seqonly" in line:
            type="seqonly"
        if "rawdata" in line:
            type="rawdata"
        if "cellplex" in line:
            type="cellplex"
        if "cite-seq" in line:
            type="cite-seq"
        if "FAILED" in line:
            type=type+"-failed"
        if "DONE" in line:
            type=type+"-done"
        if "DELIVERED" in line:
            type=type+"-delivered"
        ls4[count] = [line,type]
    file1.close()
    revls4 = OrderedDict(sorted(ls4.items(), reverse=True, key=lambda t: t[0]))
    return render_template('ls4cron.html',ls4=revls4,crontid=file1tid)
    
# Display cronlog files
@listers.route('/ctg-cron')
@login_required
def cron():
    ls4={}
    sync={}
    squeue={}

    file1n = app.config['STATIC_FOLDER'] + "/cron/ctg-cron.log"
    file2n = app.config['STATIC_FOLDER'] + "/cron/log.ctg.runfolder.snc.ls4"
    file1 = open(file1n, 'r',errors='ignore') # ls4 automation log
    file2 = open(file2n, 'r',errors='ignore') # trannel ls4 sync log
    file3 = app.config['STATIC_FOLDER'] + "/cron/squeue.current.txt" # squeue ls4 each minute

    # Get time of update cron log and runfolder sync files
    file1tid=time.ctime(os.path.getmtime(file1n))
    file2tid=time.ctime(os.path.getmtime(file2n))
    
    # Read file1
    count = 0
    while True:
        count += 1
        # Get next line from file
        lineraw = file1.readline()
        line = lineraw.replace(" CET","")
        # if line is empty
        # end of file is reached
        if not line:
            break
        # get type of line
        type=""
        if "interop" in line:
            type="interop"
        if "sav-save" in line:
            type="sav-save"
        if "parse-samplesheet" in line:
            type="parse-samplesheet"
        if "panel-tumor-only" in line:
            type="panel-tumor-only"
        if "sc-rna-10x" in line:
            type="sc-rna-10x"
        if "sc-multi-10x" in line:
            type="sc-multi-10x"
        if "seqonly" in line:
            type="seqonly"
        if "rawdata" in line:
            type="rawdata"
        if "cellplex" in line:
            type="cellplex"
        if "cite-seq" in line:
            type="cite-seq"
        if "FAILED" in line:
            type=type+"-failed"
        if "DONE" in line:
            type=type+"-done"
        if "DELIVERED" in line:
            type=type+"-delivered"
        ls4[count] = [line,type]
    file1.close()

    # Read file2
    count=0
    while True:
        count += 1
        # Get next line from file
        lineraw = file2.readline()
        line = lineraw.replace(" CET","")
        # if line is empty
        # end of file is reached
        if not line:
            break
        # get type of info
        type=""
        if "New CTG" in line:
            type="completed"
        if "identified" in line:
            type="identified"
        if "Starting sync" in line or "STARTED" in line:
            type="start"
        if "Synced" in line or "COMPLETED" in line:
            type="synced"
        if "FAILED" in line:
            type="failed"
        sync[count] = [line.strip("> "),type]
    file2.close()

    # Read file3 Squeue
    sq = pd.read_csv(file3,delim_whitespace=True,index_col=0,skiprows=1)
    squeue = sq.to_html()
    # Read date of squeue file
    sqtid = ""
    with open(file3, "r") as file:
        sqtid = file.readline().strip()
        for last_line in file:
            pass
    
    revls4 = OrderedDict(sorted(ls4.items(), reverse=True, key=lambda t: t[0]))
    revsync = OrderedDict(sorted(sync.items(), reverse=True, key=lambda t: t[0]))
    return render_template('crondisplay.html',ls4=revls4,sync=revsync,squeue=squeue,sqtid=sqtid,crontid=file1tid,runtid=file2tid)


# FUNCTION for status (get date of table)
def getDate(df):
    dates=df[0] + ":" + df[1].astype(str) + ":" + df[2].astype(str)
    date=dates.iloc[-1]
    dl=" ".join(date.split()).split()
    # if 2nd element is numeric, it is swedish
    if dl[1].isnumeric():
        l.setlocale(l.LC_ALL, 'sv_SE')
        day=dl[1]
        month=dl[2]
        year=dl[3]
        date=day+"-"+month+"-"+year[2:4]+" "+dl[4]
    else:
        l.setlocale(l.LC_ALL, 'en_US')
        day=dl[2]
        month=dl[1]
        year=dl[5]
        date=day+"-"+month+"-"+year[2:4]+" "+dl[3]
    a=str(datetime.strptime(date,"%d-%b-%y %H:%M:%S"))
    a=a[2:]
    a=a[:len(a)-3]
    a=a.replace("-","")
    return(a)

# Function to get pending processes (for def Status below)
def getPending(projPD):
    pendproc=[]
    for index,row in projPD.iterrows():
        proc=row.NAME.split("_")[0].replace("nf-","")
        pendproc.append(proc)
    p=str(Counter(pendproc)).replace("Counter({","").replace("})","").replace("'","").replace(",","\n    -").replace(": ",":\t")
    pendstring="    Pending:\n    - %s" % p
    return(pendstring)

   
# Display STATUS table files
@listers.route('/ctg-status')
@login_required
def status():

    file1n = app.config['STATIC_FOLDER'] + "/cron/ctg-cron.log"
    file2n = app.config['STATIC_FOLDER'] + "/cron/log.ctg.runfolder.snc.ls4.clean"
    file3n = app.config['STATIC_FOLDER'] + "/cron/ctg-projids-run-pipe.22.csv"
    squeuef = app.config['STATIC_FOLDER'] + "/cron/squeue.current.txt" # squeue ls4 each minute

    class color:
        BOLD = '\033[1m'
        END = '\033[0m'

    pipecron = pd.read_csv(file1n,sep=":",header=None)
    runcron = pd.read_csv(file2n,sep=":",header=None)
    squeue = pd.read_csv(squeuef,skiprows=1,delim_whitespace=True)
    # Get all runfodlers from runfolder sync and cronlog
    runfolders=[]
    for run in list(runcron[3]):
        curr=run.strip()
        if curr.startswith("2"):
            runfolders.append(curr)
            
    for run in list(pipecron[3]):
        curr=run.strip()
        if curr.startswith("2"):
            runfolders.append(curr)
                    
    runfolders = set(runfolders)
    
    # Get proj-runfolder list from lsens
    projtab = pd.read_csv(file3n,header=None)
    projtab.columns=["Runfolder","projid","pipeline","interop","savsave"]
    projtab=projtab[projtab.pipeline.notnull()]

    # Set up columns for downstream additions
    for a in ['Sync_Status', 'Pipe_Status', 'Started', 'Delivered', 'Done', 'Squeue', 'Failed']:
        projtab[a] = ""

    for index, row in projtab.iterrows():
        #####
        # Get and Set runfolder sync status
        #####
        run=row[0]
        rundate=run.split("_")[0]
        runnr=run.split("_")[2]
        runid=rundate+"_"+runnr
        # If Nova
        if "_A" in run:
            if runcron[runcron[3].str.contains(run)].empty==False:
                status=runcron[runcron[3].str.contains(run)].iloc[-1][4].strip()
                if "COMPLETE" in status:
                    status="COMPLETED"
            else:
                status="NA"
        else:
            status="Manual sync (Not Nova)"
            projtab.loc[index,"Sync_Status"] = status

        ######
        # Check for pipeline status
        ######
        pipe=row["pipeline"]
        proj=row["projid"]
        
        # pipe + projid
        pipeprojdf=pipecron[pipecron[3].str.contains(run)][pipecron[5].str.contains(pipe)][pipecron[5].str.contains(proj)]
        # pipe only
        pipedf=pipecron[pipecron[3].str.contains(run)][pipecron[5].str.contains(pipe)]
        # Sequqe
        projq = squeue[squeue.NAME.str.contains(proj[0:8]) | squeue.NAME.str.contains(runid)]
        
        finalstring=""
        runstring=""
        pendstring=""
        if "R" in list(projq.ST):
            projtab.loc[index,"Pipe_Status"] = "Running"
            pipestat="Running"
            projRun=projq[projq.ST.str.contains("R")]
            runstring = str(list(projRun[["TIME","NAME","ST"]].agg(" ".join,axis=1))).replace("'","").replace("[","").replace("]","").replace("nf-","").replace(proj,"").replace(runid,"").replace("_("," ").replace("_)"," ").replace(pipe," ").replace(")","").replace("-","").replace(" R","").replace(" PD","").replace(",","\n").replace(proj[0:8],"").replace(runid,"")
            # See if there are any Pending processes in addition to the running
            if "PD" in list(projq.ST):
                projPD=projq[projq.ST.str.contains("PD")]
                pendstring=getPending(projPD)
                finalstring=runstring + "\n" + pendstring
            else:
                finalstring=runstring
            # Set Squeue string
            projtab.loc[index,"Squeue"] = finalstring
        # if no running prcesses, then gather the pending processes
        elif "PD" in list(projq.ST):
            pipestat="Pending"
            projPD=projq[projq.ST.str.contains("PD")]
            pendstring=getPending(projPD)
            finalstring=pendstring
            projtab.loc[index,"Pipe_Status"] = "Pending"
            # Set Squeue string
            projtab.loc[index,"Squeue"] = finalstring
       # else:
            # Check Status of last pipe run for runfolder 
        elif pipedf.empty==False:
            last=pipedf.iloc[-1].to_frame().transpose()
            print("?===============")
            print("- last pipedf")
            print(last)
            stat=str(last[4])
            if "DELIV" in stat:
                date=getDate(last)
                projtab.loc[index,"Delivered"] = date
                projtab.loc[index,"Pipe_Status"] = "Delivered"
                projtab.loc[index,"Squeue"] = ""
            if "DONE" in stat:
                date=getDate(last)
                projtab.loc[index,"Done"] = date
                projtab.loc[index,"Pipe_Status"] = "Done"
                projtab.loc[index,"Squeue"] = ""
            if "FAILED" in stat:
                date=getDate(last)
                projtab.loc[index,"Failed"] = date
                projtab.loc[index,"Pipe_Status"] = "FAILED"
                projtab.loc[index,"Squeue"] = "FAILED at %s" % date
            if "DONE" in stat and "DELIV" in stat:
                date=getDate(pipeprojdf[pipeprojdf[4].str.contains("DONE")])
                projtab.loc[index,"Done"] = date
                projtab.loc[index,"Pipe_Status"] = "Done"
                projtab.loc[index,"Squeue"] = ""
 #           if "STARTED" in stat:
 #               date=getDate(last)
 #               projtab.loc[index,"Started"] = date
#                projtab.loc[index,"Pipe_Status"] = "Running"
 #               projtab.loc[index,"Squeue"] = finalstring
        # Get last pipe started
        starteds=pipedf[pipedf[4].str.contains("STARTED")]
        if starteds.empty==False:
            last=starteds.iloc[-1].to_frame().transpose()
            projtab.loc[index,"Started"] = getDate(last)
        if projtab.loc[index,"Pipe_Status"]=="":
            # Get current projects runfolder - check if syncing/sequencing ongoing
            rf = projtab.loc[index,"Runfolder"]
            if runcron[runcron[3].str.contains(rf)].empty==False:
                curr=runcron[runcron[3].str.contains(rf)]
                last=curr.iloc[-1].to_frame().transpose()
                date=getDate(last)
                stat=str(last[4])
                status="unknown"
                if "COMPL" in stat:
                    status="COMPLETED"
                if "STARTED" in stat:
                    status="Syncing_runfolder"
                if "identifi" in stat:
                    status="Sequencing_ongoing"
                if "sequencing compl" in stat:
                    status="Sequencing_completed"
                # IF not completed sync/sequencing of runfolder, set sync status as pipe status
                if status != "COMPLETED":
                    projtab.loc[index,"Pipe_Status"]=status
                    projtab.loc[index,"Started"] = getDate(last)
                    projtab.loc[index,"Sync_Status"]=status
                                

    for rf in runfolders:
        if rf not in list(projtab["Runfolder"]):
            if runcron[runcron[3].str.contains(rf)].empty==False:
                curr=runcron[runcron[3].str.contains(rf)]
                last=curr.iloc[-1].to_frame().transpose()
                date=getDate(last)
                stat=str(last[4])
                status="unknown"
                if "COMPL" in stat:
                    status="COMPLETED"
                if "STARTED" in stat:
                    status="Syncing_runfolder"
                if "identifi" in stat:
                    status="Sequencing_ongoing"
                if "sequencing compl" in stat:
                    status="Sequencing_completed"
                # Get samplesheet identified
                row=pd.Series([rf,"na","na","","",status,status,date,"","","",""])
                row_df = pd.DataFrame([row], index = [max([i for i in projtab.index])+1])
                row_df.columns=projtab.columns
                projtab=pd.concat([projtab,row_df])

    projtab=projtab.sort_values("Runfolder",ascending=False)
    projtab=projtab[['Runfolder', 'Sync_Status',  'interop', 'savsave', 'projid', 'pipeline','Pipe_Status','Started', 'Delivered', 'Done', 'Squeue']]

    # Get only 2022 runfolders
    projtab=projtab[projtab.Runfolder.str.startswith("22")]
    # Sort on activity (and Runfolder)
    projtab["rank"]=[1 if pipe=="Running" or pipe=="Pending" or pipe=="FAILED" else 2 for pipe in projtab.Pipe_Status]
    projtab=projtab.sort_values(["rank","Runfolder"],ascending=(True,False))
    projtab=projtab.drop("rank",axis=1)
    tab=projtab.values.tolist()

    return render_template('status.html',tab=tab)
