from VISHALMUSIC import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import asyncio

# Global variable to track enabled groups
DELETE_TRACKER_ENABLED = {}

@app.on_message(filters.command("deletetrack") & filters.group)
async def toggle_delete_tracker(client, message):
    try:
        chat_id = message.chat.id
        user = await client.get_chat_member(chat_id, message.from_user.id)
        
        if user.privileges and user.privileges.can_delete_messages:
            if chat_id not in DELETE_TRACKER_ENABLED:
                DELETE_TRACKER_ENABLED[chat_id] = True
            
            DELETE_TRACKER_ENABLED[chat_id] = not DELETE_TRACKER_ENABLED[chat_id]
            status = "ᴇɴᴀʙʟᴇᴅ" if DELETE_TRACKER_ENABLED[chat_id] else "ᴅɪsᴀʙʟᴇᴅ"
            
            await message.reply_text(
                f"**🗑️ ᴅᴇʟᴇᴛᴇ ᴛʀᴀᴄᴋᴇʀ {status}**\n\n"
                f"**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ɴᴏᴡ ᴀʟʟ ᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇs ᴡɪʟʟ ʙᴇ ʟᴏɢɢᴇᴅ" if DELETE_TRACKER_ENABLED[chat_id] 
                else "**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ᴅᴇʟᴇᴛᴇ ᴛʀᴀᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ"
            )
        else:
            await message.reply_text("❌ ʏᴏᴜ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ᴛᴏ ᴛᴏɢɢʟᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ.")
            
    except Exception as e:
        await message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

@app.on_message(filters.group)
async def advanced_delete_tracker(client, message):
    try:
        chat_id = message.chat.id
        
        # Default enable for new groups
        if chat_id not in DELETE_TRACKER_ENABLED:
            DELETE_TRACKER_ENABLED[chat_id] = True
        
        # Check if tracker is enabled
        if not DELETE_TRACKER_ENABLED[chat_id]:
            return
            
        # User info with stylish format
        user = message.from_user
        if not user:
            return
            
        user_name = user.first_name or "ᴜɴᴋɴᴏᴡɴ"
        user_id = user.id
        username = f"@{user.username}" if user.username else "ɴᴏɴᴇ"
        
        # Get user profile photo
        profile_photo = None
        try:
            photos = await client.get_chat_photos(user_id, limit=1)
            if photos:
                profile_photo = photos[0].file_id
        except:
            profile_photo = None
        
        # Message content capture with stylish format
        if message.text:
            content = f"**ᴛᴇxᴛ:** `{message.text}`"
            msg_type = "📝 ᴛᴇxᴛ"
        elif message.photo:
            content = "**ᴘʜᴏᴛᴏ:** 🖼️ ᴍᴇᴅɪᴀ"
            msg_type = "📸 ᴘʜᴏᴛᴏ"
        elif message.video:
            content = "**ᴠɪᴅᴇᴏ:** 🎥 ᴍᴇᴅɪᴀ" 
            msg_type = "🎬 ᴠɪᴅᴇᴏ"
        elif message.document:
            doc_name = message.document.file_name or "ᴜɴᴋɴᴏᴡɴ"
            content = f"**ᴅᴏᴄᴜᴍᴇɴᴛ:** 📄 {doc_name}"
            msg_type = "📁 ᴅᴏᴄᴜᴍᴇɴᴛ"
        elif message.sticker:
            sticker_emoji = message.sticker.emoji or "🎭"
            content = f"**sᴛɪᴄᴋᴇʀ:** {sticker_emoji}"
            msg_type = "😊 sᴛɪᴄᴋᴇʀ"
        elif message.audio:
            audio_title = message.audio.title or "ᴜɴᴋɴᴏᴡɴ"
            content = f"**ᴀᴜᴅɪᴏ:** 🎵 {audio_title}"
            msg_type = "🎵 ᴀᴜᴅɪᴏ"
        else:
            content = "**ᴏᴛʜᴇʀ ᴄᴏɴᴛᴇɴᴛ**"
            msg_type = "🔗 ᴏᴛʜᴇʀ"
        
        # Stylish delete alert message
        alert_text = f"""
🚫 **ᴅᴇʟᴇᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴀᴄᴛɪᴠᴇ**

👤 **ᴜsᴇʀ ɪɴғᴏ:**
   ├ **ɴᴀᴍᴇ:** {user_name}
   ├ **ɪᴅ:** `{user_id}`
   ├ **ᴜsᴇʀɴᴀᴍᴇ:** {username}
   └ **ᴛʏᴘᴇ:** {msg_type}

💬 **ᴄᴏɴᴛᴇɴᴛ:**
{content[:150]}{'...' if len(str(content)) > 150 else ''}

📱 **ᴄʜᴀᴛ:** {message.chat.title}
⏰ **sᴇɴᴛ:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}

**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡᴀs ᴘʀᴏᴛᴇᴄᴛᴇᴅ
        """
        
        # Keyboard buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👀 ᴠɪᴇᴡ ᴜsᴇʀ", url=f"tg://user?id={user_id}"),
                InlineKeyboardButton("🔧 ᴛᴏɢɢʟᴇ", callback_data=f"toggle_tracker_{chat_id}")
            ]
        ])
        
        # Send alert with or without profile photo
        if profile_photo:
            # With profile photo
            await client.send_photo(
                chat_id=message.chat.id,
                photo=profile_photo,
                caption=alert_text,
                reply_markup=keyboard
            )
        else:
            # Without profile photo
            await client.send_message(
                chat_id=message.chat.id,
                text=alert_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        
    except Exception as e:
        print(f"❌ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛʀᴀᴄᴋᴇʀ ᴇʀʀᴏʀ: {e}")

# Callback handler for toggle button
@app.on_callback_query(filters.regex("toggletracker"))
async def toggle_tracker_callback(client, callback_query):
    try:
        chat_id = int(callback_query.data.split("_")[2])
        
        if callback_query.from_user.id not in [admin.user.id for admin in await client.get_chat_members(chat_id, filter="administrators")]:
            await callback_query.answer("❌ ʏᴏᴜ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs!", show_alert=True)
            return
            
        if chat_id not in DELETE_TRACKER_ENABLED:
            DELETE_TRACKER_ENABLED[chat_id] = True
            
        DELETE_TRACKER_ENABLED[chat_id] = not DELETE_TRACKER_ENABLED[chat_id]
        status = "ᴇɴᴀʙʟᴇᴅ" if DELETE_TRACKER_ENABLED[chat_id] else "ᴅɪsᴀʙʟᴇᴅ"
        
        await callback_query.answer(f"ᴅᴇʟᴇᴛᴇ ᴛʀᴀᴄᴋᴇʀ {status}!", show_alert=True)
        
        # Edit the message to show new status
        original_text = callback_query.message.text or callback_query.message.caption
        if original_text:
            new_text = original_text.replace(
                "**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡᴀs ᴘʀᴏᴛᴇᴄᴛᴇᴅ",
                f"**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ᴛʀᴀᴄᴋᴇʀ ɪs ɴᴏᴡ {status}"
            )
            
            if hasattr(callback_query.message, 'caption'):
                await callback_query.message.edit_caption(new_text)
            else:
                await callback_query.message.edit_text(new_text)
                
    except Exception as e:
        await callback_query.answer("❌ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ!", show_alert=True)

# Command to check status
@app.on_message(filters.command("trackstatus") & filters.group)
async def track_status(client, message):
    chat_id = message.chat.id
    status = DELETE_TRACKER_ENABLED.get(chat_id, True)
    status_text = "ᴇɴᴀʙʟᴇᴅ" if status else "ᴅɪsᴀʙʟᴇᴅ"
    
    await message.reply_text(
        f"🔍 **ᴅᴇʟᴇᴛᴇ ᴛʀᴀᴄᴋᴇʀ sᴛᴀᴛᴜs**\n\n"
        f"**ᴄᴜʀʀᴇɴᴛʟʏ:** {status_text}\n"
        f"**ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ** - ᴜsᴇ `/deletetrack` ᴛᴏ ᴛᴏɢɢʟᴇ"
    )