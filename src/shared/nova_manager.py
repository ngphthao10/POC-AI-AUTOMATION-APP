"""NovaAct instance manager with enhanced features"""
from nova_act import NovaAct
from typing import Callable, Optional
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


class NovaManager:
    """Manage NovaAct instance lifecycle with enhanced features"""

    @staticmethod
    def create(
        starting_page: str,
        api_key: Optional[str] = None,
        headless: Optional[bool] = None,
        record_video: Optional[bool] = None,
        logs_directory: Optional[str] = None,
        execution_id: Optional[str] = None,
        video_quality: int = 85,
        **kwargs
    ) -> NovaAct:
        # Get API key
        if not api_key:
            api_key = os.getenv('NOVA_ACT_API_KEY')
            if not api_key:
                raise ValueError(
                    "Nova Act API key not found. Set NOVA_ACT_API_KEY environment variable "
                    "or pass api_key parameter."
                )

        # Read headless mode from environment if not specified
        if headless is None:
            headless_env = os.getenv('HEADLESS', 'false').lower()
            headless = headless_env in ['true', '1', 'yes']

        # Read video recording setting from environment if not specified
        if record_video is None:
            video_env = os.getenv('RECORD_VIDEO', 'false').lower()
            record_video = video_env in ['true', '1', 'yes']

        # Setup logs directory
        if record_video or logs_directory:
            if not logs_directory:
                # Auto-generate logs directory
                if not execution_id:
                    execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

                logs_directory = f"logs/nova_traces/{execution_id}"

            # Create directory
            Path(logs_directory).mkdir(parents=True, exist_ok=True)
            print(f"📂 Logs directory: {logs_directory}")

            if record_video:
                print(f"🎥 Video recording enabled (quality: {video_quality})")

        # Build NovaAct config
        nova_config = {
            'starting_page': starting_page,
            'headless': headless,
            'ignore_https_errors': True,
            'nova_act_api_key': api_key,
            **kwargs
        }

        # Add video recording if enabled
        if record_video:
            nova_config['record_video'] = True

        # Add logs directory if specified
        if logs_directory:
            nova_config['logs_directory'] = logs_directory

        # Log configuration
        mode = "headless" if headless else "headed"
        print(f"🚀 Creating NovaAct instance ({mode} mode)")

        return NovaAct(**nova_config)

    @staticmethod
    def create_for_automation(
        automation_name: str,
        starting_page: str,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> NovaAct:
        if not execution_id:
            execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        logs_directory = f"logs/{automation_name}/{execution_id}"

        return NovaManager.create(
            starting_page=starting_page,
            logs_directory=logs_directory,
            execution_id=execution_id,
            **kwargs
        )
