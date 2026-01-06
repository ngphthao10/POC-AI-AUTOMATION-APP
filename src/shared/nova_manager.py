from nova_act import NovaAct
from typing import Callable, Optional
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


class NovaManager:

    @staticmethod
    def create_for_automation(
        automation_name: str,
        starting_page: str,
        execution_id: Optional[str] = None,
        api_key: Optional[str] = None,
        headless: Optional[bool] = None,
        record_video: Optional[bool] = None,
        video_quality: int = 85,
        **kwargs
    ) -> NovaAct:

        # Generate execution ID if not provided
        if not execution_id:
            execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Get API key
        if not api_key:
            api_key = os.getenv('NOVA_ACT_API_KEY')

        # Read headless mode from environment if not specified
        if headless is None:
            headless_env = os.getenv('HEADLESS', 'false').lower()
            headless = headless_env in ['true', '1', 'yes']

        # Read video recording setting from environment if not specified
        if record_video is None:
            video_env = os.getenv('RECORD_VIDEO', 'false').lower()
            record_video = video_env in ['true', '1', 'yes']

        # Setup logs directory
        logs_directory = f"logs/{automation_name}/{execution_id}"

        if record_video or logs_directory:
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

        # Add logs directory
        nova_config['logs_directory'] = logs_directory

        # Log configuration
        mode = "headless" if headless else "headed"
        print(f"🚀 Creating NovaAct instance ({mode} mode)")

        return NovaAct(**nova_config)
