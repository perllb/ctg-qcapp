import os
import re
from flask import Blueprint,render_template, jsonify,request, redirect, url_for, flash
from flask_login import login_required, current_user
import datetime as dt
from time import ctime
import glob
import csv
import pandas as pd
from collections import OrderedDict
from .models import db, CTGdata
from sqlalchemy import desc
from . import app

ctgdata_blue = Blueprint('ctgdata', __name__)

#CTG DATA
@ctgdata_blue.route('/ctgdata_all',methods=['POST'])
@login_required
def ctgdata_all():
    projs=CTGdata.query.filter(CTGdata.runfolder.startswith("2"))
    order_proj = projs.order_by(CTGdata.runfolder.desc())
    return render_template(
       'ctg_data.html',
       projs=order_proj,
       title="CTG data (all)"
   )

@ctgdata_blue.route('/ctgdata_post', methods=['POST'])
@login_required
def ctgdata_post():
    # Retrieve posts from ctg_data.html
    projid = request.form.get('projid')
    runfolder = request.form.get('runfolder')
    search_proj = request.form.get('search_proj')
    del_proj = request.form.get('proj_to_delete')
    proj2020 = request.form.get('show_2020')
    proj2021 = request.form.get('show_2021')
    proj = CTGdata.query.filter_by(projid=projid).first() # if this returns a user, then the email already exists in database
    if proj: # if a projid is found, we want to redirect back to signup page so user can try again
        flash('Project ID "' + projid + '" already exists','error')
        return redirect(url_for('ctgdata.ctgdata_all'))
    if projid and runfolder:# create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_proj = CTGdata(
            projid=projid,
            runfolder=runfolder,
            created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        # add the new user to the database
        db.session.add(new_proj)
        db.session.commit()
        flash('Project ID "' + projid + '" added','success')
    if search_proj:
        return render_template(
            'ctg_data.html',
            projs=CTGdata.query.filter(CTGdata.projid.contains(search_proj)),
            title="CTG data"
        )
    return redirect(url_for('ctgdata.ctgdata_all'))

@ctgdata_blue.route('/ctgdata_2020', methods=['POST'])
@login_required
def ctgdata_2020_run():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.runfolder.startswith("20")),
        title="CTG data: 2020 Runfolders"
    )

@ctgdata_blue.route('/ctgdata_2022', methods=['POST'])
@login_required
def ctgdata_2022_run():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.runfolder.startswith("22")),
        title="CTG data: 2022 Runfolders"
    )

@ctgdata_blue.route('/ctgdata_proj')
@login_required
def ctgdata_ctgproj():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.projid.startswith("2")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: Project ID"
    )

@ctgdata_blue.route('/ctgdata_2021', methods=['POST'])
@login_required
def ctgdata_2021_run():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.runfolder.startswith("21")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: 2021 Runfolders"
    )

@ctgdata_blue.route('/ctgdata_2020p', methods=['POST'])
@login_required
def ctgdata_2020_proj():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.projid.contains("2020_")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: 2020 Projects"
    )

@ctgdata_blue.route('/ctgdata_2021p', methods=['POST'])
@login_required
def ctgdata_2021_proj():
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.projid.contains("2021_")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: 2021 Projects"
    )

@ctgdata_blue.route('/ctgdata_import', methods=['POST'])
@login_required
def ctgdata_import():
    def assign_data(data):
        for row in data.iterrows():
            liro = list(list(row)[1])
            projectid = liro[0]
            status  = liro[1]
            runfolder = liro[2]
            bnfdude = liro[3]
            lsens4 = liro[4]
            workfolder = liro[5]
            customerpi = liro[6]
            customer2 = liro[7]
            lfs603user = liro[8]
            deliverycontact = liro[9]
            datatype = liro[10]
            library = liro[11]
            ctgbnf = liro[12]
            delivered = liro[13]
            qclogged = liro[14]
            ctginterop = liro[15]
            ctgsavsave = liro[16]
            deliveryrep = liro[17]
            comment = liro[18]
            created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            proj = CTGdata.query.filter_by(projid=projectid).first() # if this returns a project, it exists already
            if proj:
                flash('Project ID "' + str(projectid) + '" already exists','error')
                #return redirect(url_for('ctgdata.ctgdata_all'))
            else:
                new_proj = CTGdata(
                    projid = projectid,
                    status  = status,
                    runfolder = runfolder,
                    bnfdude = bnfdude,
                    lsens4 = lsens4,
                    workfolder = workfolder,
                    customerpi = customerpi,
                    customer2 = customer2,
                    lfs603user = lfs603user,
                    deliverycontact = deliverycontact,
                    datatype = datatype,
                    library = library,
                    ctgbnf = ctgbnf,
                    delivered = delivered,
                    qclogged = qclogged,
                    ctginterop = ctginterop,
                    ctgsavsave = ctgsavsave,
                    deliveryrep = deliveryrep,
                    comment = comment,
                    created=created
                )
                db.session.add(new_proj)
                db.session.commit()
                flash('Project ID "' + str(projectid) + '" added','success')
    ## 2021
    data = pd.read_csv(app.config["STATIC_FOLDER"] + "/ctg-data/ctg-data_2021.csv", sep=";")
    assign_data(data)
    ## 2020
    data = pd.read_csv(app.config["STATIC_FOLDER"] + "/ctg-data/ctg-data_2020.csv", sep=";")
    assign_data(data)
    return render_template(
         'ctg_data.html',
         projs=CTGdata.query.filter(CTGdata.projid.startswith("20")).order_by(CTGdata.runfolder.desc()),
         title="CTG data (all)"
         )

@ctgdata_blue.route('/ctgdata_delete', methods=['POST'])
@login_required
def ctgdata_delete():
    del_proj = request.form.get('proj_to_delete')
    if del_proj:
        CTGdata.query.filter_by(projid=del_proj).delete()
        db.session.commit()
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))

@ctgdata_blue.route('/ctgdata_delivered', methods=['GET','POST'])
@login_required
def ctgdata_delivered():
    deliv_proj = request.form.get('proj_delivered')
    if deliv_proj:
        project = CTGdata.query.filter_by(projid=deliv_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.delivered != 'y':
            newdel='y'
            project.status="delivered"
        else:
            newdel='n'
            project.status="not delivered"

        project.delivered = newdel
        db.session.commit()
        newstat = "delivered" if newdel == 'y' else "not delivered"
        flash('Project ID "' + str(deliv_proj) + '" updated to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))

@ctgdata_blue.route('/ctgdata_ctginteroprun', methods=['GET','POST'])
@login_required
def ctgdata_ctginterop():
    ctginterop_proj = request.form.get('proj_ctginterop')
    if ctginterop_proj:
        project = CTGdata.query.filter_by(projid=ctginterop_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.ctginterop != 'y':
            newdel='y'
        else:
            newdel='n'
        project.ctginterop = newdel
        db.session.commit()
        newstat = "completed" if newdel == 'y' else "not completed"
        flash('Project ID "' + str(ctginterop_proj) + '" updated to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))


@ctgdata_blue.route('/ctgdata_qclog', methods=['GET','POST'])
@login_required
def ctgdata_qclog():
    qclog_proj = request.form.get('proj_qclog')
    if qclog_proj:
        project = CTGdata.query.filter_by(projid=qclog_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.qclogged != 'y':
            newdel='y'
        else:
            newdel='n'
        project.qclogged = newdel
        db.session.commit()
        newstat = "completed" if newdel == 'y' else "not completed"
        flash('Project ID "' + str(qclog_proj) + '" updated to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))

@ctgdata_blue.route('/ctgdata_ctgsavsave', methods=['GET','POST'])
@login_required
def ctgdata_ctgsavsave():
    sav_proj = request.form.get('proj_ctgsavsave')
    if sav_proj:
        project = CTGdata.query.filter_by(projid=sav_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.ctgsavsave != 'y':
            newdel='y'
        else:
            newdel='n'
        project.ctgsavsave = newdel
        db.session.commit()
        newstat = "completed" if newdel == 'y' else "not completed"
        flash('Project ID "' + str(sav_proj) + '" updated to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))


@ctgdata_blue.route('/ctgdata_deliveryrep', methods=['GET','POST'])
@login_required
def ctgdata_deliveryrep():
    deliv_proj = request.form.get('proj_deliveryrep')
    if deliv_proj:
        project = CTGdata.query.filter_by(projid=deliv_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.deliveryrep != 'y':
            newdel='y'
        else:
            newdel='n'
        project.deliveryrep = newdel
        db.session.commit()
        newstat = "delivered" if newdel == 'y' else "not delivered"
        flash('Project ID "' + str(deliv_proj) + '" Delivery report is now set to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))

@ctgdata_blue.route('/ctgdata_interop', methods=['GET','POST'])
@login_required
def ctgdata_interop():
    interop_proj = request.form.get('proj_interop')
    if interop_proj:
        project = CTGdata.query.filter_by(projid=interop_proj).first()
        # change to N if Y, change to Y if N
        newdel = 'n'
        if project.ctginterop != 'y':
            newdel='y'
        else:
            newdel='n'
        project.ctginterop = newdel
        db.session.commit()
        newstat = "completed" if newdel == 'y' else "not completed"
        flash('Project ID "' + str(interop_proj) + '"  is now set to "' + newstat + '"','success')
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))



@ctgdata_blue.route('/ctgdata_edit/<proj>', methods=['GET','POST'])
@login_required
def edit_project(proj):
    project = CTGdata.query.filter_by(projid=proj).first()
    if request.method=='GET':
        return render_template('ctg_data_edit.html',
            proj=project,
            title="Edit project " + str(proj)
            )
    if request.method =='POST':
        #fetch form data
        projDetails= request.form
        project.projid = projDetails['projectid']
        project.status  = projDetails['status']
        project.runfolder = projDetails['runfolder']
        project.bnfdude = projDetails['bnfdude']
        project.lsens4 = projDetails['lsens4']
        project.workfolder = projDetails['workfolder']
        project.customerpi = projDetails['customerpi']
        project.customer2 = projDetails['customer2']
        project.lfs603user = projDetails['lfs603user']
        project.deliverycontact = projDetails['deliverycontact']
        project.datatype = projDetails['datatype']
        project.library = projDetails['library']
        project.delivered = projDetails['delivered']
        project.qclogged = projDetails['qclogged']
        project.ctginterop = projDetails['ctginterop']
        project.ctgsavsave = projDetails['ctgsavsave']
        project.deliveryrep = projDetails['deliveryrep']
        project.comment = projDetails['comment']
        db.session.commit()
        flash("Project " + proj + " Updated Successfully","success")
        return redirect(url_for('ctgdata.ctgdata_ctgproj'))



@ctgdata_blue.route('/ctgdata_export', methods=['POST'])
@login_required
def ctgdata_export():
    import sqlite3
    import csv
    from sqlalchemy import create_engine
    from flask import make_response

    now = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    fn = app.config["BASEDIR"] + '/ctg-data/dumps/ctg-data.'+now+'.csv'

    columns = CTGdata.__table__.columns.keys()
    print("Columns")
    print(columns)
    lines=[]
    for row in CTGdata.query.filter(CTGdata.runfolder.startswith("2")).order_by(CTGdata.runfolder.desc()):
        line = []
        for col in columns:
            data = str(row.__dict__[col])
            line.append(data)
        lines.append(line)
    df=pd.DataFrame(lines,columns=columns)
    df.to_csv(fn,sep="\t",index=False)

    flash('Table exported to "' + fn + '"','success')
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.projid.startswith("20")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: Project ID"
    )



@ctgdata_blue.route('/addproject',methods=['GET','POST'])
@login_required
def ctgdata_addproject():
        if request.method=='GET':
            return render_template('ctg_data_add.html',
                title="Add new project "
                )
        if request.method =='POST':
            #fetch form data
            projDetails= request.form
            projid = projDetails['projectid']
            runfolder = projDetails['runfolder']
            project_exists = CTGdata.query.filter_by(projid=projid).first()
            if project_exists:
                flash("Project " + projid + " already exists in database..","error")
            else:
                new_proj = CTGdata(
                    projid=projid,
                    runfolder=runfolder,
                    created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                # add the new project to the database
                db.session.add(new_proj)
                db.session.commit()
                project = CTGdata.query.filter_by(projid=projid).first()
                project.status  = projDetails['status']
                project.bnfdude = projDetails['bnfdude']
                project.lsens4 = projDetails['lsens4']
                project.workfolder = projDetails['workfolder']
                project.customerpi = projDetails['customerpi']
                project.customer2 = projDetails['customer2']
                project.lfs603user = projDetails['lfs603user']
                project.deliverycontact = projDetails['deliverycontact']
                project.datatype = projDetails['datatype']
                project.library = projDetails['library']
                project.delivered = projDetails['delivered']
                project.qclogged = projDetails['qclogged']
                project.ctginterop = projDetails['ctginterop']
                project.ctgsavsave = projDetails['ctgsavsave']
                project.deliveryrep = projDetails['deliveryrep']
                project.comment = projDetails['comment']
                db.session.commit()
                flash("Project " + projid + " added successfully","success")
            return redirect(url_for('ctgdata.ctgdata_ctgproj'))

@ctgdata_blue.route('/ctgdata_addproj',methods=['POST'])
@login_required
def ctgdata_addproj_post():
    projid = request.form.get('projid')
    runfolder = request.form.get('projid')
    proj = CTGdata.query.filter_by(projid=projid).first() # if this returns a project not ok.
    if proj: # if a projid is found, we want to redirect back to signup page so user can try again
        flash('Project ID "' + projid + '" already exists','error')
        return redirect(url_for('ctgdata.ctgdata_addproj'))
    if projid and runfolder:# create a new project with the form data.
        new_proj = CTGdata(
            projid=projid,
            runfolder=runfolder,
            created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        # add the new project to the database
        db.session.add(new_proj)
        db.session.commit()
        flash('Project ID "' + projid + '" added','success')
    return render_template(
        'ctg_data.html',
        projs=CTGdata.query.filter(CTGdata.projid.startswith("20")).order_by(CTGdata.runfolder.desc()),
        title="CTG data: Project ID"
    )





### SCAN LSENS RUNFOLDERS
@ctgdata_blue.route('/scanprojects',methods=['GET','POST'])
@login_required
def ctgdata_scanLsens():
    # read scanned_sheets.txt in static/cron - see if new projects / runfolders are there
    if request.method=='GET':
        scannedsheets=app.config["STATIC_FOLDER"] + "/cron/ctg-projids-run-pipe.22.csv"
        data=pd.read_csv(scannedsheets,sep=",",header=None)
        data.columns=["run","projid","pipe","interop","savsave"]
        any_added=0
        for index,row in data.iterrows():
            projid=row['projid']
            run=row['run']
            pipeline=row['pipe']
            interoprun=row['interop']
            savsaved=row['savsave']
            project_exists = CTGdata.query.filter_by(projid=projid).first()
            if project_exists:
                print("An entry with project id " + projid + " already exists in CTG data DB")
            else:
                if pipeline=="noSheet":
                    # No projid - but chech also whether the run has been previously added as "noSheet" project
                    # Check also if it is aready added as "-noSheet" project
                    pNoSheet=run[0:6]+"-noSheet"
                    project_noSheet_exists = CTGdata.query.filter_by(projid=pNoSheet).first()
                    if project_noSheets_exists:
                        print("A 'noSheet' entry with project id " + pNoSheet + " already exists in CTG data DB")
                    else:
                        any_added=1
                        new_proj = CTGdata(
                            projid=run[0:6]+"-noSheet",
                            runfolder=run,
                            status="AUTO_ADD",
                            datatype=pipeline,
                            lsens4 = 'y',
                            ctginterop = interoprun,
                            ctgsavsave = savsaved,
                            created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        # add the new project to the database
                        db.session.add(new_proj)
                        db.session.commit()
                        flash("Runfolder " + run + " added successfully","success")
                else:
                    any_added=1
                    new_proj = CTGdata(
                        projid=projid,
                        runfolder=run,
                        status="AUTO_ADD",
                        datatype=pipeline,
                        lsens4 = 'y',
                        workfolder = "shared/ctg-projects/" + pipeline + "/" + projid + "-" + pipeline,
                        lfs603user = "ctg-" + projid,
                        ctginterop = interoprun,
                        ctgsavsave = savsaved,
                        created=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    # add the new project to the database
                    db.session.add(new_proj)
                    db.session.commit()
                    flash("Project " + projid + " added successfully","success")
        if any_added==0:
            flash("No new projects / runfolders were identified.. ","error")
    return redirect(url_for('ctgdata.ctgdata_ctgproj'))

