import os,logging,time,traceback,shutil
import aiohttp
from ..core.getVars import get_val
from ..core import thumb_manage # i guess i will dodge this one ;) as i am importing the vids helper anyways
from . import vids_helpers,zip7_utils
from .progress_for_telethon import progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from telethon.errors import VideoContentTypeInvalidError
from ..core.database_handle import tkupload
from .. import user_db
from telethon.tl.types import KeyboardButtonCallback,DocumentAttributeVideo,DocumentAttributeAudio
from telethon.utils import get_attributes
from .Ftele import upload_file




env_email = get_val("EMAIL_KEY")
env_api_key = get_val("API_KEY")

torlog = logging.getLogger(__name__)


async def mixdrop_driver(path,message,from_uid,files_dict,job_id=0,force_edit=False,updb=None,from_in=False,thumb_path=None, user_msg=None):
    # creting here so connections are kept low
    if updb is None:
        # Central object is not used its Acknowledged 
        updb = tkupload()

    #logging.info("Uploading Now:- {}".format(path))

    if os.path.isdir(path):
        logging.info("Uplaoding the directory:- {}".format(path))

        directory_contents = os.listdir(path)
        directory_contents.sort()
        try:
            # maybe way to refresh?!
            message = await message.client.get_messages(message.chat_id,ids=[message.id])
            message = message[0]
        except:pass

        message = await message.edit("{}\nFound {} files for this download".format(message.text,len(directory_contents)))
        
        if not from_in:
            updb.register_upload(message.chat_id,message.id)
            if user_msg is None:
                sup_mes = await message.get_reply_message()
            else:
                sup_mes = user_msg
            
            data = "upcancel {} {} {}".format(message.chat_id,message.id,sup_mes.sender_id)
            buts = [KeyboardButtonCallback("Cancel upload.",data.encode("UTF-8"))]
            message = await message.edit(buttons=buts)


        for file in directory_contents:
            if updb.get_cancel_status(message.chat_id,message.id):
                continue

            await mixdrop_driver(
                os.path.join(path,file),
                message,
                from_uid,
                files_dict,
                job_id,
                force_edit,
                updb,
                from_in=True,
                thumb_path=thumb_path,
                user_msg=user_msg
            )
        
        if not from_in:
            if updb.get_cancel_status(message.chat_id,message.id):
                await message.edit("{} - Cancled By user.".format(message.text),buttons=None)
            else:
                await message.edit(buttons=None)
            updb.deregister_upload(message.chat_id,message.id)

    else:
        logging.info("Uplaoding the file:- {}".format(path))
        if os.path.getsize(path) > get_val("TG_UP_LIMIT"):
            # the splitted file will be considered as a single upload ;)
            
            
            metadata = extractMetadata(createParser(path))
            
            if metadata is not None:
                # handle none for unknown
                metadata = metadata.exportDictionary()
                try:
                    mime = metadata.get("Common").get("MIME type")
                except:
                    mime = metadata.get("Metadata").get("MIME type")

                ftype = mime.split("/")[0]
                ftype = ftype.lower().strip()
            else:
                ftype = "unknown"
            
            if ftype == "video":    
                todel = await message.reply("FILE LAGRE THEN THRESHOLD SPLITTING NOW.Processing.....\n```Using Algo FFMPEG SPLIT```") 
                split_dir = await vids_helpers.split_file(path,get_val("TG_UP_LIMIT"))
            else:
                todel = await message.reply("FILE LAGRE THEN THRESHOLD SPLITTING NOW.Processing.....\n```Using Algo PARTED ZIP SPLIT```") 
                split_dir = await zip7_utils.split_in_zip(path,get_val("TG_UP_LIMIT"))
            
            dircon = os.listdir(split_dir)
            dircon.sort()

            if not from_in:
                updb.register_upload(message.chat_id,message.id)
                if user_msg is None:
                    sup_mes = await message.get_reply_message()
                else:
                    sup_mes = user_msg
                data = "upcancel {} {} {}".format(message.chat_id,message.id,sup_mes.sender_id)
                buts = [KeyboardButtonCallback("Cancel upload.",data.encode("UTF-8"))]
                await message.edit(buttons=buts)

            for file in dircon:
                if updb.get_cancel_status(message.chat_id,message.id):
                    continue
            
                await mixdrop_driver(
                    os.path.join(split_dir,file),
                    message,
                    from_uid,
                    files_dict,
                    job_id,
                    force_edit,
                    updb=updb,
                    from_in=True,
                    thumb_path=thumb_path,
                    user_msg=user_msg
                )
            
            try:
                shutil.rmtree(split_dir)
                os.remove(path)
            except:pass
            
            if not from_in:
                if updb.get_cancel_status(message.chat_id,message.id):
                    await message.edit("{} - Cancled By user.".format(message.text),buttons=None)
                else:
                    await message.edit(buttons=None)
                updb.deregister_upload(message.chat_id,message.id)
            # spliting file logic blah blah
        else:
            if not from_in:
                updb.register_upload(message.chat_id,message.id)
                if user_msg is None:
                    sup_mes = await message.get_reply_message()
                else:
                    sup_mes = user_msg
                
                data = "upcancel {} {} {}".format(message.chat_id,message.id,sup_mes.sender_id)
                buts = [KeyboardButtonCallback("Cancel upload.",data.encode("UTF-8"))]
                await message.edit(buttons=buts)
            #print(updb)
            if not os.path.exists(path):
                sentmsg = None
            else:
                sentmsg = await mixFileup(
                    path,
                    message,
                    force_edit,
                    updb,
                    thumb_path,
                    user_msg
                )

            if not from_in:
                if updb.get_cancel_status(message.chat_id,message.id):
                    await message.edit("{} - Cancled By user.".format(message.text),buttons=None)
                else:
                    await message.edit(buttons=None)
                updb.deregister_upload(message.chat_id,message.id)

            if sentmsg is not None:
                files_dict[os.path.basename(path)] = sentmsg.id

    return files_dict


async def mixFileup(path,message,force_edit,database=None,thumb_path=None,user_msg=None):
    queue = message.client.queue
    if database is not None:
        if database.get_cancel_status(message.chat_id,message.id):
            # add os remove here
            return None
    if not os.path.exists(path):
        return None
    #todo improve this uploading ✔️
    file_name = os.path.basename(path)
    file_size = os.path.getsize(path)
    metadata = extractMetadata(createParser(path))
    ometa = metadata    
    if metadata is not None:
        # handle none for unknown
        metadata = metadata.exportDictionary()
        try:
            mime = metadata.get("Common").get("MIME type")
        except:
            mime = metadata.get("Metadata").get("MIME type")

        ftype = mime.split("/")[0]
        ftype = ftype.lower().strip()
    else:
        ftype = "unknown"
    if not force_edit:
        if user_msg is None:
            sup_mes = await message.get_reply_message()
        else:
            sup_mes = user_msg
        
        data = "upcancel {} {} {}".format(message.chat_id,message.id,sup_mes.sender_id)
        buts = [KeyboardButtonCallback("Cancel upload.",data.encode("UTF-8"))]
        msg = await message.reply("Uploading {}".format(file_name),buttons=buts)
    else:
        msg = message
        #print(metadata)
    uploader_id = None
    if queue is not None:
        torlog.info(f"Waiting for the worker here for {file_name}")
        msg = await msg.edit(f"{msg.text} - Waiting for a uploaders to get free")
        uploader_id = await queue.get()
        torlog.info(f"Waiting over for the worker here for {file_name} aquired worker {uploader_id}")
    out_msg = None
    start_time = time.time()
    tout = get_val("EDIT_SLEEP_SECS")
    opath = path

    try:
        email = env_email
        api_key = env_api_key
        upload_url = "https://ul.mixdrop.co/api"
        async with aiohttp.ClientSession() as session:
            data = {
                'file': open(path,"rb"),
                'email': email,
                'key': api_key
            }
            response = await session.post(upload_url, data=data)
            link = await response.json()
#            dl_b = f"https://mixdrop.co/f/{link['result']['fileref']}"
            torlog.info("success")            
    except Exception as e:
        if str(e).find("cancel") != -1:
            torlog.info("cancled an upload lol")
            await msg.delete()
        else:
            torlog.info(traceback.format_exc())
    finally:
        if queue is not None:
            await queue.put(uploader_id)
            torlog.info(f"Freed uploader with id {uploader_id}")
    if out_msg is None:
        return None
    if out_msg.id != msg.id:
        await msg.delete()
    
    return out_msg



