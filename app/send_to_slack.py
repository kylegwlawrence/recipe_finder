import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_to_slack(github_link:str, channel_id:str="C06NZKA1L03") -> None:
	"""Send a message with a link to slack"""
	logger = logging.getLogger(__name__)

	# get recipe ingredients from link and num recipes
	recipe_info = github_link.split('/')[-1]
	ingredients = recipe_info.split('_')[1].replace('-', ', ')
	num_recipes = recipe_info.split('_')[2]

    # instantiate the webclient with a bot token
	try:
		client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
	except SlackApiError as e:
		logger.error("Error creating client: {}".format(e))
	try:
		# call app.client.chat_postMessage
		result = client.chat_postMessage(
			channel=channel_id,
			text=f"{num_recipes} new recipes for {ingredients} in <{github_link}|Github>"
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
	g = 'https://github.com/kylegwlawrence/recipe_finder/blob/main/md_recipes/recipes_vodkasauce-pasta-kale_3_20240311-144445_test2.md'
	#md_file = 'requirements.txt'
	send_to_slack(g)