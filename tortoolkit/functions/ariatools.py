# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]

import asyncio, aria2p, logging, os
from ..core.getVars import get_val
from telethon.tl.types import KeyboardButtonCallback
from telethon.errors.rpcerrorlist import MessageNotModifiedError

# referenced from public leech
# pylint: disable=no-value-for-parameter
torlog = logging.getLogger(__name__)

async def aria_start():
    aria2_daemon_start_cmd = []
    # start the daemon, aria2c command
    aria2_daemon_start_cmd.append("aria2c")
    # aria2_daemon_start_cmd.append("--allow-overwrite=true")
    aria2_daemon_start_cmd.append("--daemon=true")
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--follow-torrent=false")
    aria2_daemon_start_cmd.append("--max-connection-per-server=8")
    aria2_daemon_start_cmd.append("--min-split-size=10M")
    aria2_daemon_start_cmd.append("--rpc-listen-all=false")
    aria2_daemon_start_cmd.append(f"--rpc-listen-port=8100")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")
    aria2_daemon_start_cmd.append("--seed-ratio=0.0")
    aria2_daemon_start_cmd.append("--seed-time=1")
    aria2_daemon_start_cmd.append("--split=10")
    aria2_daemon_start_cmd.append(f"--bt-stop-timeout=100")
    #
    torlog.debug(aria2_daemon_start_cmd)
    #
    process = await asyncio.create_subprocess_exec(
        *aria2_daemon_start_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    torlog.debug(stdout)
    torlog.debug(stderr)
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=8100,
            secret=""
        )
    )
    return aria2

def add_magnet(aria_instance, magnetic_link, c_file_name):
    try:
        download = aria_instance.add_magnet(
            magnetic_link
        )
    except Exception as e:
        return False, "⚠ **FAILED** \n" + str(e) + " \nPlease do not send SLOW links."
    else:
        return True, "" + download.gid + ""


def add_torrent(aria_instance, torrent_file_path):
    if torrent_file_path is None:
        return False, "⚠ **FAILED** \n\nSomething went wrong when trying to add <u>TORRENT</u> file!"
    if os.path.exists(torrent_file_path):
        # Add Torrent Into Queue
        try:
            download = aria_instance.add_torrent(
                torrent_file_path,
                uris=None,
                options=None,
                position=None
            )
        except Exception as e:
            return False, "⚠ **FAILED** \n" + str(e) + " \nPlease do not send SLOW links."
        else:
            return True, "" + download.gid + ""
    else:
        return False, "⚠ **FAILED** \n" + str(e) + " \nPlease try other sources to get workable link."


def add_url(aria_instance, text_url, c_file_name):
    uris = [text_url]
    # Add URL Into Queue
    try:
        download = aria_instance.add_uris(
            uris
        )
    except Exception as e:
        return False, "⚠ **FAILED** \n" + str(e) + " \nPlease do not send SLOW links."
    else:
        return True, "" + download.gid + ""

async def check_metadata(aria2, gid):
    file = aria2.get_download(gid)
    torlog.info(file)
    if not file.followed_by_ids:
        return None
    new_gid = file.followed_by_ids[0]
    torlog.info("Changing GID " + gid + " to " + new_gid)
    return new_gid

async def aria_dl(
    incoming_link,
    c_file_name,
    sent_message_to_update_tg_p,
    user_msg
):
    aria_instance = await aria_start()
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif incoming_link.lower().endswith(".torrent"):
        #sagtus, err_message = add_torrent(aria_instance, incoming_link)
        #sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
        return False, "⚠ Cannot download this .torrent file! "
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    torlog.info(err_message)

    op = await check_progress_for_dl(
        aria_instance,
        err_message,
        sent_message_to_update_tg_p,
        None,
        user_msg=user_msg
    )
    if incoming_link.startswith("magnet:"):
        #
        err_message = await check_metadata(aria_instance, err_message)
        #
        await asyncio.sleep(1)
        if err_message is not None:
            op = await check_progress_for_dl(
                aria_instance,
                err_message,
                sent_message_to_update_tg_p,
                None,
                user_msg=user_msg
            )
        else:
            return False, "can't get metadata \n\n#stopped"
    await asyncio.sleep(1)
    
    if op is None:
        return False, "⚠ Known error. Nothing wrong here. You didnt follow instructions."
    else:
        statusr, stmsg = op
        if statusr:
            file = aria_instance.get_download(err_message)
            to_upload_file = file.name
        
            return True, to_upload_file
        else:
            return False, stmsg

async def check_progress_for_dl(aria2, gid, event, previous_message, rdepth = 0, user_msg=None):
    try:
        file = aria2.get_download(gid)
        complete = file.is_complete
        if not complete:
            if not file.error_message:
                msg = ""
                downloading_dir_name = "getting data... "
                try:
                    downloading_dir_name = str(file.name)
                except:
                    pass

                msg = f"\n<b>📥 Downloading:</b> <code>{downloading_dir_name}</code>"
                msg += f"\n<b>🚀 Speed:</b> <code>{file.download_speed_string()}</code>"
                msg += f"\n<b>⏳ Progress:</b> <code>{file.progress_string()}</code>"
                msg += f"\n<b>⏰ ETA:</b> <code>{file.eta_string()}</code>"
                msg += f"\n<b>🔥 Size:</b> <code>{file.total_length_string()}</code>"
                msg += f"\n\n  <i>⚡ Using Engine:</i> <code>aria2</code>"
                if file.seeder is False:
                    """https://t.me/c/1220993104/670177"""
                    #msg += f"| S: {file.num_seeders} |"
                # msg += f"\nStatus: {file.status}"
                #msg += f"\n<code>/cancel {gid}</code>"
                
                # format :- torcancel <provider> <identifier>
                if user_msg is None:
                    mes = await event.get_reply_message()
                else:
                    mes = user_msg
                data = f"torcancel aria2 {gid} {mes.sender_id}"
                
                # LOGGER.info(msg)
                if msg != previous_message:
                    if rdepth < 3:
                        await event.edit(msg,parse_mode="html", buttons=[KeyboardButtonCallback("Cancel Direct Leech",data=data.encode("UTF-8"))])
                    else:
                        await event.edit(msg,parse_mode="html")
                    previous_message = msg
            else:
                msg = file.error_message
                await event.edit(f"`{msg}`",parse_mode="html", buttons=None)
                torlog.error(f"⚠ The aria download faild due to this reason:- {msg}")
                return False, f"⚠ The aria download faild due to this reason:- {msg}"
            await asyncio.sleep(get_val("EDIT_SLEEP_SECS"))
            
            # TODO idk not intrested in using recursion here
            return await check_progress_for_dl(
                aria2, gid, event, previous_message,user_msg=mes
            )
        else:
            await event.edit(f"✅ <b>Download completed:</b> <code>{file.name}</code>\n⏳ Trying to upload... ",parse_mode="html", buttons=None)
            return True, "Download Complete"
    except aria2p.client.ClientException as e:
        if " not found" in str(e) or "'file'" in str(e):
            fname = "getting data... "
            try:
                fname = file.name
            except:pass

            return False, f"The Download was canceled. {fname}"
        else:
            torlog.warning("Errored due to ta client error.")
        pass
    except MessageNotModifiedError:
        pass
    except RecursionError:
        file.remove(force=True)
        return False, "⚠ The link is basically dead."
    except Exception as e:
        torlog.info(str(e))
        if " not found" in str(e) or "'file'" in str(e):
            return False, "The Download was canceled."
        else:
            torlog.warning(str(e))
            return False, f"Error: {str(e)}"

async def remove_dl(gid):
    aria2 = await aria_start()
    try:
        downloads = aria2.get_download(gid)
        downloads.remove(force=True, files=True)
    except:
        torlog.exception("exc")
        pass
