"""
MCP Email Service for VeoGen
Handles email operations through MCP servers
"""

import logging
from typing import Any, Dict, Optional

from ..mcp import mcp_client

logger = logging.getLogger(__name__)


class MCPEmailService:
    """Email service using MCP protocol for sending emails."""

    def __init__(self, mcp_server: str = "office365-mcp"):
        """Initialize with the MCP server to use for email operations."""
        self.mcp_server = mcp_server
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the MCP email service."""
        try:
            # Check if the server is running and has the required tools
            tools = await mcp_client.discover_tools(self.mcp_server)
            required_tools = {"send_email", "get_email", "list_emails"}
            available_tools = {tool["name"] for tool in tools}

            if not required_tools.issubset(available_tools):
                missing = required_tools - available_tools
                logger.error(f"MCP server {self.mcp_server} is missing required tools: {missing}")
                return False

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MCP email service: {e}")
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        cc: Optional[list] = None,
        bcc: Optional[list] = None,
        attachments: Optional[list] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send an email using the configured MCP server.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text email body
            html: HTML email body (optional)
            cc: List of CC recipients (optional)
            bcc: List of BCC recipients (optional)
            attachments: List of file paths to attach (optional)
            **kwargs: Additional parameters for the MCP server

        Returns:
            Dictionary with the result or error information
        """
        if not self.initialized:
            initialized = await self.initialize()
            if not initialized:
                return {"error": "MCP email service not initialized"}

        # Prepare the email data
        email_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "html": html,
            "cc": cc or [],
            "bcc": bcc or [],
            "attachments": [{"path": path, "filename": path.split("/")[-1]} for path in (attachments or [])],
            **kwargs,
        }

        # Call the MCP server
        try:
            result = await mcp_client.call_tool(self.mcp_server, "send_email", email_data)

            if "error" in result:
                logger.error(f"Failed to send email: {result['error']}")

            return result

        except Exception as e:
            error_msg = f"Error sending email via MCP: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    async def verify_email_setup(self) -> Dict[str, Any]:
        """Verify the email setup by sending a test email."""
        test_email = {
            "to": "test@example.com",
            "subject": "VeoGen MCP Email Test",
            "body": "This is a test email to verify MCP email setup.",
            "test_mode": True,
        }

        return await mcp_client.call_tool(self.mcp_server, "send_email", test_email)


# Global instance
mcp_email_service = MCPEmailService()

# Example usage:
if __name__ == "__main__":
    import asyncio

    async def test_email():
        service = MCPEmailService()

        # Initialize the service
        if await service.initialize():
            # Send a test email
            result = await service.send_email(
                to="recipient@example.com",
                subject="Test Email from MCP",
                body="This is a test email sent via MCP.",
                html="<p>This is a <strong>test email</strong> sent via MCP.</p>",
            )
            print("Email sent:", result)

    asyncio.run(test_email())
