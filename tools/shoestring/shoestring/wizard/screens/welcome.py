from prompt_toolkit.widgets import RadioList

from shoestring.wizard.Screen import ScreenDialog
from shoestring.wizard.ShoestringOperation import ShoestringOperation


def create(_screens):
	shoestring_command_radio = RadioList(
		values=[
			(ShoestringOperation.SETUP, 'setup'),
			(ShoestringOperation.UPGRADE, 'upgrade'),
			(ShoestringOperation.RESET_DATA, 'reset data'),
			(ShoestringOperation.RENEW_CERTIFICATES, 'renew certificates'),
			(ShoestringOperation.RENEW_VOTING_KEYS, 'renew voting keys')
		],
		default=ShoestringOperation.SETUP
	)
	shoestring_command_radio.show_scrollbar = False

	return ScreenDialog(
		screen_id='welcome',
		title='Welcome to Symbol',
		body=shoestring_command_radio,

		accessor=shoestring_command_radio
	)
