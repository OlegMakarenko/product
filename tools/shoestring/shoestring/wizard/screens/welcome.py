from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.widgets import Box, Button, Shadow

from shoestring.wizard.Screen import Screen
from shoestring.wizard.ShoestringOperation import ShoestringOperation


class ButtonWithOperation(Button):
	def __init__(self, operation, label, width=12):
		super().__init__(label, width=width)
		self.operation = operation


def create(_screens):
	values = [
		(ShoestringOperation.SETUP, 'setup'),
		(ShoestringOperation.UPGRADE, 'upgrade'),
		(ShoestringOperation.RESET_DATA, 'reset data'),
		(ShoestringOperation.RENEW_CERTIFICATES, 'renew certificates'),
		(ShoestringOperation.RENEW_VOTING_KEYS, 'renew voting keys')
	]

	max_label = max(len(label) for (_, label) in values)
	buttons = [
		ButtonWithOperation(operation, label, width=max_label + 3)
		for (operation, label) in values
	]

	return Screen(
		'welcome',
		Box(
			Shadow(
				HSplit([
					Window(
						FormattedTextControl(_('wizard-welcome-title')),
						align=WindowAlign.CENTER
					),
					Box(
						HSplit([
							Box(button, padding_top=1, padding_bottom=0) for button in buttons
						]),
						style='class:navigation'
					)
				], style='class:dialog.body')
			)
		),
		accessor=buttons,
		hide_navbar=True
	)
