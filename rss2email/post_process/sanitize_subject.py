# Copyright (C) 2025
#
# This file is part of rss2email.
#
# rss2email is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) version 3 of
# the License.
#
# rss2email is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rss2email.  If not, see <http://www.gnu.org/licenses/>.

r"""Subject sanitization for rss2email

This module provides a post-processing function to sanitize email subjects
by removing unwanted characters based on a configurable regex pattern.

Usage:
  Add to your config file:
  
  [DEFAULT]
  # Enable subject sanitization
  sanitize-subject = True
  
  # Optional: Customize the sanitization pattern
  # This pattern keeps only Russian, English, and Kazakh letters, digits, spaces, and punctuation
  subject-sanitization-regex = r'[^a-zA-Zа-яА-ЯәғқңөұүһіӘҒҚҢӨҰҮҺІ0-9 .,!?:;()[\]{}"\'«»\-–—]'
  
  # Set the post-processing function
  post-process = rss2email.post_process.sanitize_subject sanitize
"""

import re
import logging
from email.header import decode_header, make_header

# Get logger
from .. import LOG as _LOG

def sanitize(feed, parsed, entry, guid, message):
    """Sanitize the email subject by removing unwanted characters.
    
    Uses the subject-sanitization-regex configuration option to determine
    which characters to remove.
    
    Args:
        feed: The Feed instance
        parsed: The parsed feed
        entry: The feed entry
        guid: The entry guid
        message: The email message
        
    Returns:
        The modified message with sanitized subject
    """
    # Check if subject sanitization is enabled
    try:
        if not feed.config.getboolean(feed.section, 'sanitize-subject', fallback=False):
            return message
    except (AttributeError, ValueError):
        # If the option doesn't exist or isn't a valid boolean, return the original message
        return message
    
    # Get the sanitization regex pattern
    try:
        pattern = feed.config.get(feed.section, 'subject-sanitization-regex',
                                  fallback=r'[^a-zA-Zа-яА-ЯәғқңөұүһіӘҒҚҢӨҰҮҺІ0-9 .,!?:;()[\]{}"\'«»\-–—]')
    except (AttributeError, ValueError):
        # Use default pattern if there's an error
        pattern = r'[^a-zA-Zа-яА-ЯәғқңөұүһіӘҒҚҢӨҰҮҺІ0-9 .,!?:;()[\]{}"\'«»\-–—]'
    
    # Get the current subject
    subject = message.get('Subject')
    if subject is None:
        return message
    
    try:
        # Decode the subject if it's encoded
        if isinstance(subject, str):
            decoded_subject = subject
        else:
            decoded_subject = str(make_header(decode_header(subject)))
        
        # Log the original subject for debugging
        _LOG.debug(f'Original subject: {decoded_subject}')
        
        # Sanitize the subject
        sanitized_subject = re.sub(pattern, '', decoded_subject)
        
        # Log the sanitized subject for debugging
        _LOG.debug(f'Sanitized subject: {sanitized_subject}')
        
        # Update the message subject
        if sanitized_subject != decoded_subject:
            message.replace_header('Subject', sanitized_subject)
    except Exception as e:
        # Log any errors but don't break email delivery
        _LOG.error(f'Error sanitizing subject: {e}')
    
    return message