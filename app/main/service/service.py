""" Business logic for Thbred API endpoints."""
from email import message
import os, json, re, requests, itertools, sqlalchemy, itertools, calendar, dateutil, time
from datetime import datetime, date, timedelta
import datetime as dt
from http import HTTPStatus
from sqlalchemy import func, asc, desc
from flask import current_app, jsonify, session, send_file
from flask_restx import abort
from time import strptime
from werkzeug.utils import secure_filename
from app.main import db
from .decorators import token_required
from applogger import logger
from app.main.util.datetime_util import remaining_fromtimestamp, format_timespan_digits
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

import config
from app.main.models.models import (BlacklistedToken, ExtractedItems, User)

FILE_FOLDER = os.environ.get('FILE_FOLDER')
POPPLER_PATH = os.environ.get('POPPLER_PATH')
TESSERACT_PATH = os.environ.get('TESSERACT_PATH')

""" ===============================<< Registration of New User starts >>=============================== """

def registerUser(username, email, password):
    logger.info(f"Name : {username}")
    logger.info(f"Email : {email}")
    logger.info(f"Password : {password}")
    username = username.lower()
    email = email.lower()
    if User.find_by_email(email):
        abort(HTTPStatus.CONFLICT, f"{email} is already registered", status="fail")
    if User.find_by_username(username):
        abort(HTTPStatus.CONFLICT, f"{username} is already registered", status="fail")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        userInfo = User(username=username, email=email, password=password, created_ts=now)
        db.session.add(userInfo)
        db.session.commit()
        
        logger.info("User Registered")
        response = dict(status = 'success', message = 'User Registered.')
        return response, HTTPStatus.CREATED
    except:
        logger.exception("User Registration Failed")
        response = dict(status = 'fail', message = 'User Registration Failed')
        return response, HTTPStatus.CONFLICT
    
""" ===============================<< Registration of New User ends >>=============================== """
""" ===============================<< User Login Process starts >>=============================== """

def login(username, password):
    logger.info(f"username : {username}")
    logger.info(f"password : {password}")
    username = username.lower()
    session['user_name'] = username
    user = User.find_by_username(username)
    if not user or not user.check_password(password):
        logger.info("Username or Password Does not match")
        abort(HTTPStatus.UNAUTHORIZED, "Username or Password Does not match", status="fail")
    access_token = user.encode_access_token()
    logger.info("Logged In successfully.")
    
    return _create_auth_successful_response(
        message="Successfully logged in",
        token=access_token
    )
    
def _create_auth_successful_response(token, message ):
    response = jsonify(
        message=message,
        access_token=token,
        token_type="Bearer",
        expires_in=_get_token_expire_time()
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response
def _get_token_expire_time():
    token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
    token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
    expires_in_seconds = token_age_h * 3600 + token_age_m * 60
    now = dt.datetime.now()
    new_time = now + timedelta(seconds=expires_in_seconds)
    expire_time = new_time.strftime("%y-%m-%d %I:%M:%S %p")
    return expire_time

""" ===============================<< User Login Process ends >>=============================== """
@token_required
def get_logged_in_user():
    id = get_logged_in_user.user_id
    user = User.find_by_id(id)
    expires_at = get_logged_in_user.expires_at
    user.token_expires_in = format_timespan_digits(remaining_fromtimestamp(expires_at))
    return user

""" ===============================<< User logout process starts >>=============================== """

@token_required
def logout():
    access_token = logout.token
    expires_at = logout.expires_at
    blacklisted_token = BlacklistedToken(access_token, expires_at)
    db.session.add(blacklisted_token)
    db.session.commit()

    del session['user_name']
    
    response = dict(status="success", message="Successfully Logged Out")
    return response, HTTPStatus.OK

""" ===============================<< User logout process ends >>=============================== """
""" ===============================<< Change password starts >>=============================== """

@token_required 
def resetPassword(new_password):
    try:
        user = get_logged_in_user()
        if not user.check_password(new_password):
            user.password = new_password
            db.session.commit()
            response = dict(status = 'success', message = 'Password updated successfully!')
            logger.info("Password updated successfully!")
            return response, HTTPStatus.CREATED
        else:
            logger.exception("Please choose a different password than previous one")
            response = dict(status = 'conflict', message = 'Please choose a different password than previous one')
            return response, HTTPStatus.CONFLICT
    except:
        logger.exception("Password Could not be Updated")
        response = dict(status = 'fail', message = 'Password Could not be Updated')
        return response, HTTPStatus.BAD_REQUEST
   
""" ===============================<< Change password ends >>===============================  """
""" ===============================<< Extract PDF Starts >>=============================== """

FILE_EXTENSIONS = set(['pdf','PDF'])
def allowed_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in FILE_EXTENSIONS

@token_required
def extractPDF(files):
    
    if files.filename == '':
        abort(HTTPStatus.NOT_FOUND, "Blank File", status="fail")
    try:
        user  = get_logged_in_user()
        username = user.username
        current_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if files and allowed_doc(files.filename):
            filename = secure_filename(files.filename)
            extension = os.path.splitext(filename)[1]
            files.filename = str(username)+'_'+current_time+extension
            files.save(os.path.join(os.environ.get('FILE_FOLDER'),files.filename))
            # PDF_file = open(f'{FILE_FOLDER}'+files.filename, 'r')
            path = f'{FILE_FOLDER}'+files.filename
            pages = convert_from_path(f'{path}', 500, poppler_path=POPPLER_PATH)
            image_counter = 1

            for page in pages:
                filename = f'{FILE_FOLDER}'+'page_'+str(image_counter)+'.jpg'
                page.save(filename, 'JPEG')
                image_counter = image_counter + 1

            filelimit = image_counter-1
            outfile = f'{FILE_FOLDER}'+'extracted_text.txt'
            f = open(outfile, "a")
            for i in range(1, filelimit + 1):
                filename = f'{FILE_FOLDER}'+'page_'+str(i)+'.jpg'
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
                text = str(((pytesseract.image_to_string(Image.open(filename)))))
                text = text.replace('-\n', '')	
                f.write(text)
            f.close()

            _dict = {}
            f = open(f'{FILE_FOLDER}'+'extracted_text.txt', 'r')
            page_content_list = []
            for line in f:
                page_content_list.append(line)
            for index,line in enumerate(page_content_list):
                if 'Order No' in line:
                    result = re.search('Order No: (.*) Item', line)
                    _dict['job_number'] = int(result.group(1))
                    
                if 'Item' in line:
                    result = re.search('Item:(.*)', line)
                    item = result.group(1)
                    item = item.replace(" ", "")
                    _dict['task_item_number'] = item
                
                if 'Qty Ordered:' in line:
                    _dict['task_quantity'] = int(page_content_list[index+1].strip('\n'))
            extractedItem = ExtractedItems(username=username,job_number=_dict['job_number'],task_item_number=_dict['task_item_number'],task_quantity=_dict['task_quantity'],extracted_ts=now)
            db.session.add(extractedItem)
            db.session.commit()
            _dict['extracted_id'] = extractedItem.extraction_id
            
            logger.info(f"{user.username} : File Extracted Successfull")
            response = dict(filename = files.filename, message = "File Extracted Successfully", result = _dict )
            return response, HTTPStatus.OK
            
        else:
            response = dict(status = 'fail', message = 'Allowed file types are -> pdf,PDF')
            return response, HTTPStatus.NOT_ACCEPTABLE
    except:
        logger.exception("File Extraction Failed")
        response = dict(status = 'fail', message = 'File Extraction Failed')
        return response, HTTPStatus.BAD_REQUEST

""" ===============================<< Extract PDF Ends >>=============================== """
""" ===============================<< Fetch Extracted Items Starts >>=============================== """
@token_required 
def fetchExtractedItems(id):
    try:
        extractedItemInfo = db.session.query(ExtractedItems).filter_by(extraction_id=id).first()
        if extractedItemInfo != None:
            extractedItemDict = {}
            extractedItemDict['id'] = extractedItemInfo.extraction_id
            extractedItemDict['job_number'] = extractedItemInfo.job_number
            extractedItemDict['task_item_number'] = extractedItemInfo.task_item_number
            extractedItemDict['task_quantity'] = extractedItemInfo.task_quantity

            logger.info("Extracted Items Fetched successfully!")
            return extractedItemDict, HTTPStatus.OK
        else:
            logger.exception("No Extracted Items are present for the given ID")
            response = dict(status = 'fail', message = 'No Extracted Items are present for the given ID')
            return response, HTTPStatus.NOT_FOUND
    except:
        logger.exception("Extracted Items Could not be Fetched")
        response = dict(status = 'fail', message = 'Extracted Items Could not be Fetched')
        return response, HTTPStatus.BAD_REQUEST
""" ===============================<< Fetch Extracted Items Ends >>=============================== """
""" ===============================<< Update Extracted Items Starts >>=============================== """
@token_required 
def updateExtractedItems(id, job_number, task_item_number, task_quantity):
    try:
        extractedItemInfo = db.session.query(ExtractedItems).filter_by(extraction_id=id).first()
        if extractedItemInfo != None:
            extractedItemInfo.job_number = job_number
            extractedItemInfo.task_item_number = task_item_number
            extractedItemInfo.task_quantity = task_quantity
            db.session.commit()
            response = dict(status = 'success', message = 'Password updated successfully!')
            logger.info("Extracted Items Updated successfully!")
            response = dict(status = 'success', message = 'Extracted Items Updated successfully!')
            return response, HTTPStatus.OK
        else:
            logger.exception("No Extracted Items are present for the given ID")
            response = dict(status = 'fail', message = 'No Extracted Items are present for the given ID')
            return response, HTTPStatus.NOT_FOUND
    except:
        logger.exception("Extracted Items Could not be Updated")
        response = dict(status = 'fail', message = 'Extracted Items Could not be Updated')
        return response, HTTPStatus.BAD_REQUEST

""" ===============================<< Update Extracted Items Ends >>=============================== """