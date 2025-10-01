import time
import json
import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from instagrapi import Client
from openai import OpenAI
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APIFY_KEY = os.getenv("APIFY_KEY")
INSTA_USERNAME = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD")
POLL_INTERVAL = 10  # seconds
STORE_FILE = "store.json"


class ReelResponderBot:
    """Instagram bot that auto-replies to reels sent in DMs with AI-generated responses."""
    
    def __init__(self):
        """Initialize the bot with API clients and configuration."""
        self.instagram_client = None
        self.openai_client = None
        self.apify_client = None
        self.replied_messages = set()
        
        self._setup_clients()
        self._load_replied_messages()
    
    def _setup_clients(self):
        """Configure all API clients (Instagram, OpenAI, Apify)."""
        # Configure OpenAI client
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Configure Apify client
        self.apify_client = ApifyClient(APIFY_KEY)
        
        # Login to Instagram
        self.instagram_client = Client()
        self.instagram_client.login(INSTA_USERNAME, INSTA_PASSWORD)
        print("✓ Successfully logged into Instagram")
    
    def _load_replied_messages(self):
        """Load previously replied message IDs from store file."""
        try:
            with open(STORE_FILE, 'r') as f:
                data = json.load(f)
                self.replied_messages = set(data.get('replied_to', []))
            print(f"✓ Loaded {len(self.replied_messages)} previously replied messages")
        except FileNotFoundError:
            self.replied_messages = set()
            self._save_replied_messages()
            print("✓ Created new message store")
    
    def _save_replied_messages(self):
        """Save replied message IDs to store file."""
        with open(STORE_FILE, 'w') as f:
            json.dump({'replied_to': list(self.replied_messages)}, f, indent=2)
    
    def get_new_reel_messages(self) -> List[Tuple[str, object, str]]:
        """
        Fetch new reel messages from Instagram DMs.
        
        Returns:
            List of tuples: (thread_id, message_object, reel_code)
        """
        threads = self.instagram_client.direct_threads()
        new_messages = []
        
        for thread in threads:
            for msg in thread.messages:
                # Check if it's a reel from another user that we haven't replied to
                is_from_other_user = msg.user_id != self.instagram_client.user_id
                is_reel = msg.item_type == 'clip'
                not_replied = msg.id not in self.replied_messages
                
                if is_from_other_user and is_reel and not_replied:
                    new_messages.append((thread.id, msg, msg.clip.code))
                    # Mark as replied immediately to prevent duplicates
                    self.replied_messages.add(msg.id)
        
        if new_messages:
            self._save_replied_messages()
        
        return new_messages
    
    def get_reel_comments(self, reel_code: str, limit: int = 3) -> List[str]:
        """
        Fetch top comments from an Instagram reel using Apify.
        
        Args:
            reel_code: Instagram reel short code
            limit: Number of comments to fetch
            
        Returns:
            List of comment texts
        """
        reel_url = f"https://www.instagram.com/p/{reel_code}"
        
        run_input = {
            "directUrls": [reel_url],
            "resultsLimit": 10,
        }
        
        try:
            run = self.apify_client.actor("SbK00X0JYCPblD2wp").call(run_input=run_input)
            comments = []
            
            for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
                if len(comments) >= limit:
                    break
                comments.append(item['text'])
            
            return comments
        except Exception as e:
            print(f"⚠ Error fetching comments for reel {reel_code}: {e}")
            return []
    
    def generate_reply(self, comments: List[str]) -> str:
        """
        Generate an AI reply based on reel comments using OpenAI.
        
        Args:
            comments: List of comment texts from the reel
            
        Returns:
            Generated reply text
        """
        if not comments:
            return "Nice reel! 😄"
        
        prompt = f"""Based on these top comments from an Instagram reel: {comments}

Generate a single funny, casual reply (1-2 sentences max) that acknowledges the reel.
Don't use quotation marks. Keep it natural and friendly."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective and fast
                messages=[
                    {"role": "system", "content": "You are a friendly person replying to Instagram reels from friends. Keep responses casual, funny, and brief."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Remove surrounding quotes if present
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            
            return reply
        except Exception as e:
            print(f"⚠ Error generating reply: {e}")
            return "Nice reel! 😄"
    
    def send_reply(self, thread_id: str, message, reply_text: str):
        """
        Send a reply to an Instagram DM thread.
        
        Args:
            thread_id: Instagram thread ID
            message: Original message object
            reply_text: Text to send as reply
        """
        try:
            self.instagram_client.direct_send(
                reply_text,
                thread_ids=[thread_id],
                reply_to_message=message
            )
            self.instagram_client.direct_message_seen(int(thread_id), int(message.id))
            print(f"✓ Replied to thread {thread_id}: {reply_text}")
        except Exception as e:
            print(f"✗ Error sending reply to thread {thread_id}: {e}")
    
    def process_reel(self, thread_id: str, message, reel_code: str):
        """
        Complete workflow: fetch comments, generate reply, send response.
        
        Args:
            thread_id: Instagram thread ID
            message: Message object
            reel_code: Instagram reel short code
        """
        print(f"\n📹 Processing reel: {reel_code}")
        
        # Get comments from the reel
        comments = self.get_reel_comments(reel_code)
        print(f"  • Found {len(comments)} comments")
        
        # Generate AI reply
        reply = self.generate_reply(comments)
        print(f"  • Generated reply: {reply}")
        
        # Send the reply
        self.send_reply(thread_id, message, reply)
    
    def run(self):
        """Main bot loop - continuously check for new reels and respond."""
        print("\n" + "="*50)
        print("🤖 Reel Responder Bot Started")
        print("="*50)
        print(f"• Checking for new reels every {POLL_INTERVAL} seconds")
        print(f"• Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Fetch new reel messages
                new_messages = self.get_new_reel_messages()
                
                if new_messages:
                    print(f"\n🔔 Found {len(new_messages)} new reel(s) to respond to")
                    
                    # Process each reel
                    for thread_id, msg, reel_code in new_messages:
                        self.process_reel(thread_id, msg, reel_code)
                
                # Wait before next poll
                time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            raise


def main():
    """Entry point for the bot."""
    bot = ReelResponderBot()
    bot.run()


if __name__ == "__main__":
    main()
