from os.path import exists
import os, time
import datetime as dt
import re
from .models import db, CTGdata
from . import app

# List new project folders
def listnewfiles(days):
    newfiles={}
    qcdir=app.config['QC_FOLDER']
    now = dt.datetime.now()
    ago = now-dt.timedelta(days=days)

    # Check for new project QC
    for root, dirs,files in os.walk(qcdir):
        for dir in dirs:
            # Only get project folders
            pattern = re.compile("^202[0-9]_[0-9]*")
            if pattern.search(dir):
                if not dir.endswith('data'):
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    if mtime > ago:
                        mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                        if mode == "ctg-rnaseq":
                            mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[3]
                        # Get runfolder of project from ctgdata db
                        # Use only first 8 letters (e.g. 202*_***) from dir.. 
                        proj = CTGdata.query.filter_by(projid=dir).first()
                        if proj:
                            runfolder = proj.runfolder
                        else:
                            # Search full dirname
                            proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                            if proj:
                                runfolder = proj.runfolder
                            # It might be that the CTGdata project has a suffix, such as 202*_***_suffix
                            else:
                                proj = CTGdata.query.filter(CTGdata.projid.contains(dir[0:8])).first()
                                if proj:
                                    runfolder = proj.runfolder
                                else:
                                    runfolder = "na"
                        newfiles[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]
            # Get test-project folders
            pattern = re.compile("^202[0-9]_test*")
            if pattern.search(dir):
                if not dir.endswith('data'):
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    if mtime > ago:
                        mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                        if mode == "ctg-rnaseq":
                            mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[3]
                        # Get runfolder of project
                        proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                        if proj:
                            runfolder = proj.runfolder
                        else:
                            runfolder = "na"
                        newfiles[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]

    # Check for SeqOnly QC
    for root, dirs,files in os.walk(qcdir):
        for dir in dirs:
            # Only get project folders
            pattern = re.compile("^2[0-2][0-9][0-9][0-9][0-9]*-seqonly*")
            if pattern.search(dir):
                if not dir.endswith('data'):
                    path = os.path.join(root, dir)
                    st = os.stat(path)
                    mtime = dt.datetime.fromtimestamp(st.st_mtime)
                    if mtime > ago:
                        mode=root.replace(app.config['STATIC_FOLDER'],"").split("/")[2]
                        # Get runfolder of project
                        proj = CTGdata.query.filter_by(projid=dir[0:8]).first()
                        if proj:
                            runfolder = proj.runfolder
                        else:
                            runfolder = "na"
                        newfiles[dir] = [path,mode,str(mtime.date()) + " - " + str(mtime.time())[0:8],runfolder]

    # Check for new Interop stats
    sinteropdir=app.config['QC_FOLDER'] + "/interop/"
    interopreps=os.listdir(sinteropdir)
    newinterop={}
    for rep in interopreps:
        pattern = re.compile("^multiqc_ctg_interop_")
        if pattern.search(rep) and not rep.endswith("_data"):
            print(rep)
            st = os.stat(sinteropdir+"/"+rep)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > ago:
                run_id = rep.replace("multiqc_ctg_interop_","")
                run_id = run_id.replace(".html","")
                ## occupied vs PF plots
                occpffile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/occ_pf." + run_id + "_mqc.png"
                occpf="na"
                if "_A0" in run_id:
                    if exists("/srv/flask/qcapp/" + occpffile):
                        occpf = occpffile
                ## q-score heatmap
                qscorefile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_q-heat-map_mqc.png"
                qscore="na"
                if exists("/srv/flask/qcapp/" + qscorefile):
                    qscore = qscorefile
                ## q-score histogram
                qscorehistfile="/qcapp/static/ctg-qc/interop/occ-pf-q-score-plots/" + run_id + "_q-histogram_mqc.png"
                qscorehist="na"
                if exists("/srv/flask/qcapp/" + qscorehistfile):
                    qscorehist = qscorehistfile
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
                newinterop[run_id] = [sinteropdir+"/"+rep,"interop",str(mtime.date()) + " - " + str(mtime.time())[0:8], occpf,qscore,qscorehist,ccint,ccflow,clusterC]

    # Sort on date
    sortnewproj = dict(sorted(newfiles.items(), key=lambda item: item[1][2], reverse=True))
    sortnewinterop = dict(sorted(newinterop.items(), key=lambda item: item[1][2], reverse=True))
    return (sortnewproj,sortnewinterop,days)
