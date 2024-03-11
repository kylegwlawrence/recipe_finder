import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_to_slack(f_path:str, channel_id:str="C06NZKA1L03") -> None:
	"""Take a recipe markdown file and upload it to a given channel_id in your Slack workspace."""
	logger = logging.getLogger(__name__)
    # instantiate the webclient with a bot token
	try:
		client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
		# Tests to see if the token is valid
		auth_test = client.auth_test()
		bot_user_id = auth_test["user_id"]
		print(f"App's bot user: {bot_user_id}")
		print(f'Auth test results: {auth_test}')
	except SlackApiError as e:
		logger.error("Error creating client: {}".format(e))
	try:
		# call method to upload files to channel
		result = client.files_upload_v2(
			channel=channel_id,
			initial_comment="New recipes",
			file=f'./{f_path}',
			request_file_info=False
		)
		logger.info(result)

		# call app.client.chat_postMessage
		result = client.chat_postMessage(
			channel=channel_id,
			text=" - list item 1\n - list item 2", 
			mrkdwn=True
		)
		logger.info(result)

	except SlackApiError as e:
		logger.error("Error uploading file: {}".format(e))
		# send failure message to slack channel
		try:
			result = client.chat_postMessage(
    			channel=channel_id,
				text="File upload to Slack failed."
			)
			logger.info(result)
		except SlackApiError as e:
			logger.error("Error sending failure message: {}".format(e))   
			
if __name__=='__main__':
	md_file = 'md_recipes/recipes_beef-onions-celery-carrots-saffron-milk-kimchi_5_20240311-090134.md'
	#md_file = 'requirements.txt'
	send_to_slack(md_file)