from typing import Optional
from redditwarp.ASYNC import Client
from redditwarp.models.submission_ASYNC import LinkPost, TextPost, GalleryPost
from fastmcp import FastMCP
import logging

mcp = FastMCP("Reddit MCP")
client = Client()
logging.getLogger().setLevel(logging.WARNING)

@mcp.tool()
async def fetch_reddit_hot_threads(subreddit: str, limit: int = 10) -> str:
    """
    Fetch hot threads from a subreddit
    
    Args:
        subreddit: Name of the subreddit
        limit: Number of posts to fetch (default: 10)
        
    Returns:
        Human readable string containing list of post information
    """
    try:
        posts = []
        async for submission in client.p.subreddit.pull.hot(subreddit, limit):
            post_info = (
                f"Title: {submission.title}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.num_comments}\n"
                f"Author: {submission.author_display_name or '[deleted]'}\n"
                f"Type: {_get_post_type(submission)}\n"
                f"Content: {_get_content(submission)}\n""
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            posts.append(post_info)
            
        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def fetch_reddit_post_content(post_id: str, include_comments: bool = True) -> str:
    """
    Fetch detailed content of a specific post
    
    Args:
        post_id: Reddit post ID
        include_comments: Whether to include top comments (default: True)
        
    Returns:
        Human readable string containing post content and optional comments
    """
    try:
        submission = await client.p.submission.fetch(post_id)
        
        content = (
            f"Title: {submission.title}\n"
            f"Score: {submission.score}\n"
            f"Author: {submission.author_display_name or '[deleted]'}\n"
            f"Type: {_get_post_type(submission)}\n"
            f"Content: {_get_content(submission)}\n"
        )
        
        if include_comments:
            comments = await client.p.comment_tree.fetch(post_id, sort='top', limit=5)
            if comments.children:
                content += "\nTop Comments:\n"
                for i, comment in enumerate(comments.children[:5], 1):
                    content += (
                        f"\n{i}. Author: {comment.value.author_display_name or '[deleted]'}\n"
                        f"   Score: {comment.value.score}\n"
                        f"   {comment.value.body}\n"
                    )
            else:
                content += "\nNo comments found."
                
        return content

    except Exception as e:
        return f"An error occurred: {str(e)}"

def _get_post_type(submission) -> str:
    """Helper method to determine post type"""
    if isinstance(submission, LinkPost):
        return 'link'
    elif isinstance(submission, TextPost):
        return 'text'
    elif isinstance(submission, GalleryPost):
        return 'gallery'
    return 'unknown'

def _get_content(submission) -> Optional[str]:
    """Helper method to extract post content based on type"""
    if isinstance(submission, LinkPost):
        return submission.permalink
    elif isinstance(submission, TextPost):
        return submission.body
    elif isinstance(submission, GalleryPost):
        return str(submission.gallery_link)
    return None